from firebirdsql.fbcore import Connection, Cursor
from datetime import datetime
import calendar
import pygsheets
import pandas as pd
import re

def list_date(year, month):

    end_res = calendar.monthrange(year, month)
    end_day = end_res[1]
    end_date = datetime.strptime(f'{year}-{month}-{end_day}', "%Y-%m-%d")
    end_date = datetime.now() if end_date > datetime.now() else end_date
    if month == 1:
        start_res = calendar.monthrange(year-1, 12)
        start_day = start_res[1]
        start_date = datetime.strptime(f'{year-1}-12-{start_day}', "%Y-%m-%d")
    else:
        start_res = calendar.monthrange(year, month -1)
        start_day = start_res[1]
        start_date = datetime.strptime(f'{year}-{month-1}-{start_day}', "%Y-%m-%d")

    date_list = pd.date_range(start_date, end_date, freq='D').strftime("%Y-%m-%d")
    return date_list.to_list()

def get_maxmin_temp(start_date:str, end_date:str, db_cur:Cursor):
    k_start = re.findall(r'(\d+)', start_date)
    k_end = re.findall(r'(\d+)', end_date)
    start = str(k_start[2]) + "." + str(k_start[1]) + "." + str(k_start[0])
    end = str(k_end[2]) + "." + str(k_end[1]) + "." + str(k_end[0])
    query =f'SELECT Max(r.MEASVALUE), Min(r.MEASVALUE) FROM( SELECT * FROM MEASUREMENTHIST WHERE MEASTIMESTAMP BETWEEN \'{start}, 07:00:00.000\' AND \'{end}, 06:59:59.999\' and MEASID = 1 and MEASVALUE BETWEEN -58 and 122 ORDER BY MEASTIMESTAMP ASC) as r'
    try:
        result = db_cur.execute(query=query).fetchall()
        if result != []:
            return result[0]
        else:
            return result
    except:
        return []

def get_sum_rain(start_date:str, end_date:str, db_cur:Cursor):
    k_start = re.findall(r'(\d+)', start_date)
    k_end = re.findall(r'(\d+)', end_date)
    start = str(k_start[2]) + "." + str(k_start[1]) + "." + str(k_start[0])
    end = str(k_end[2]) + "." + str(k_end[1]) + "." + str(k_end[0])
    query_previous = f'SELECT Max(r.MEASVALUE) FROM( SELECT * FROM MEASUREMENTHIST WHERE MEASTIMESTAMP BETWEEN \'{start}, 00:00:00.000\' AND \'{start}, 06:59:59.999\' and MEASID = 10 ORDER BY MEASTIMESTAMP ASC) as r'
    query_first =f'SELECT Max(r.MEASVALUE) FROM( SELECT * FROM MEASUREMENTHIST WHERE MEASTIMESTAMP BETWEEN \'{start}, 07:00:00.000\' AND \'{start}, 23:59:59.999\' and MEASID = 10 ORDER BY MEASTIMESTAMP ASC) as r'
    query_second = f'SELECT Max(r.MEASVALUE) FROM( SELECT * FROM MEASUREMENTHIST WHERE MEASTIMESTAMP BETWEEN \'{end}, 00:00:00.000\' AND \'{end}, 06:59:59.999\' and MEASID = 10 ORDER BY MEASTIMESTAMP ASC) as r'
    rain = 0
    flag = 0
    try:
        result_previous = db_cur.execute(query=query_previous).fetchall()
        result_first = db_cur.execute(query=query_first).fetchall()
        result_second = db_cur.execute(query=query_second).fetchall()
        if result_first != [] and result_second != [] and result_previous != []:
            if result_first[0][0] != None:
                rain = rain + result_first[0][0]
                flag = 1
            if result_second[0][0] != None:
                rain = rain + result_second[0][0]
                flag = 1
            if result_previous[0][0] != None:
                rain = rain - result_previous[0][0]
                flag = 1
            if flag == 1:
                return rain
            else:
                return None
        else:
            return None
    except Exception as e:
        print(e)
        return []

def get_temp_dawn(date:str, db_cur:Cursor):
    k_date = re.findall(r'(\d+)', date)
    when = str(k_date[2]) + "." + str(k_date[1]) + "." + str(k_date[0])
    query =f'SELECT SUM(r.TEMPERATURE) From(SELECT MEASID, AVG(MEASVALUE)as TEMPERATURE FROM MEASUREMENTHIST WHERE MEASTIMESTAMP BETWEEN \'{when}, 06:59:00.000\' AND \'{when}, 07:00:59.999\' and MEASVALUE BETWEEN -58 and 122 Group By MEASID)as r WHERE r.MEASID = 1'
    try:
        result = db_cur.execute(query=query).fetchall()
        if result != []:
            return result[0]
        else:
            return result
    except:
        return []

def collecting_data(year, month, db:Connection):
    date_list = list_date(year=year, month=month)
    data_temp = []
    data_rain = []
    df_data = pd.DataFrame()
    df_rain = pd.DataFrame()
    date = []
    date_period = []
    temp_max = []
    temp_min = []
    temp_dawn = []
    rain_value = []
    db_cur = db.cursor()
    for i in range(len(date_list)-1):
        date.append(date_list[i+1])
        date_period.append(f'{date_list[i]}:7:00:00 to {date_list[i + 1]}:6:59:59')
        temp = get_maxmin_temp(date_list[i], date_list[i + 1], db_cur)
        dawn = get_temp_dawn(date_list[i+1], db_cur)
        rain = get_sum_rain(date_list[i], date_list[i + 1], db_cur)
        temp_max.append(temp[0])
        temp_min.append(temp[1])
        temp_dawn.append(dawn[0])
        rain_value.append(rain)
    df_data['Date'] = date
    df_data['Max Temp'] = temp_max
    df_data['Min Temp'] = temp_min
    df_data['Temp at 7:00'] = temp_dawn
    df_data['Rain'] = rain_value
    df_data['Time Period of observation'] = date_period
    db.close()
    return df_data

def save_google_sheet(year:int, month:int, db:Connection, users:list, cred:str):
    print(year, month)
    df_data = collecting_data(year=year, month=month, db=db)
    print(type(df_data))
    gc = pygsheets.authorize(service_file=cred)
    sheet_name = f'Weather Report {year}-{month}'
    try:
        a = gc.open(sheet_name)
        a.delete()
    except:
        pass
    res = gc.sheet.create(sheet_name)
    sheet_id = res['spreadsheetId']
    sh = gc.open_by_key(sheet_id)
    print(f"Created spreadsheet with id:{sh.id} and url:{sh.url}")
    # Share with self to allow to write to it                     
    for i in users:
        sh.share(i, role='writer', type='user')
    try:
        sh.sheet1.title = "Wheather Data"
    except:
        pass
    try:
        temp = sh[0] 
        temp.set_dataframe(df_data,(1,1))
        return sh.url
    except Exception as e:
        print(e)
        return "Failed in writing on google sheet"


def save_csv(year:int, month:int, db:Connection, f_path:str):
    print(year, month)
    df_data = collecting_data(year=year, month=month, db=db)
    df_data.to_csv(f_path, sep=',', index=False, encoding='utf-8')
