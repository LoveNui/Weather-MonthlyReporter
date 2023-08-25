import firebirdsql
from datetime import datetime
from argparse import ArgumentParser
import pygsheets
import pandas as pd
import re
import csv

conn = firebirdsql.connect(
    host='localhost',
    database='D:\WeatherMaster-MonthlyReporter\WeatherData.FDB',
    user='sysdba',
    password='masterkey'
)
cur = conn.cursor()

def list_date(year, month):
    start_date = datetime.strptime(f'{year}-{month}-01', "%Y-%m-%d")
    if month == 12:
        end_date = datetime.strptime(f'{year+1}-01-01', "%Y-%m-%d")
    else:
        end_date = datetime.strptime(f'{year}-{month + 1}-01', "%Y-%m-%d")

    date_list = pd.date_range(start_date, end_date, freq='D').strftime("%Y-%m-%d")
    return date_list.to_list()

def get_maxmin_temp(start_date, end_date):
    k_start = re.findall(r'(\d+)', start_date)
    k_end = re.findall(r'(\d+)', end_date)
    start = str(k_start[2]) + "." + str(k_start[1]) + "." + str(k_start[0])
    end = str(k_end[2]) + "." + str(k_end[1]) + "." + str(k_end[0])
    query =f'SELECT Max(r.MEASVALUE), Min(r.MEASVALUE) FROM( SELECT * FROM MEASUREMENTHIST WHERE MEASTIMESTAMP BETWEEN \'{start}, 07:00:00.000\' AND \'{end}, 06:59:59.999\' and MEASID = 1 and MEASVALUE BETWEEN -58 and 122 ORDER BY MEASTIMESTAMP ASC) as r'
    try:
        result = cur.execute(query=query).fetchall()
        if result != []:
            return result[0]
        else:
            return result
    except:
        return []

def get_sum_rain(start_date, end_date):
    k_start = re.findall(r'(\d+)', start_date)
    k_end = re.findall(r'(\d+)', end_date)
    start = str(k_start[2]) + "." + str(k_start[1]) + "." + str(k_start[0])
    end = str(k_end[2]) + "." + str(k_end[1]) + "." + str(k_end[0])
    query =f'SELECT SUM(r.MEASVALUE) FROM( SELECT * FROM MEASUREMENTHIST WHERE MEASTIMESTAMP BETWEEN \'{start}, 07:00:00.000\' AND \'{end}, 06:59:59.999\' and MEASID = 10 and MEASVALUE BETWEEN -58 and 122 ORDER BY MEASTIMESTAMP ASC) as r'
    try:
        result = cur.execute(query=query).fetchall()
        if result != []:
            return result[0]
        else:
            return result
    except:
        return []

def collecting_data(year, month):
    date_list = list_date(year=year, month=month)
    data_temp = []
    data_rain = []
    df_temp = pd.DataFrame()
    df_rain = pd.DataFrame()
    date = []
    temp_max = []
    temp_min = []
    rain_value = []
    for i in range(len(date_list)-1):
        date.append(date_list[i])
        temp = get_maxmin_temp(date_list[i], date_list[i + 1])
        temp_max.append(temp[0])
        temp_min.append(temp[1])
        rain = get_sum_rain(date_list[i], date_list[i + 1])
        rain_value.append(rain[0])
    df_temp['date'] = date
    df_temp['max'] = temp_max
    df_temp['min'] = temp_min
    df_rain['date'] = date
    df_rain['rain'] = rain_value

    return df_temp, df_rain

def save_google_sheet(args):
    year = args.year
    month = args.month
    print(year, month)
    df_temp, df_rain = collecting_data(year=year, month=month)
    gc = pygsheets.authorize(service_file='cred.json')
    sheet_name = f'Weather Report {year}-{month}'
    sheet_id = ""
    try:
        res = gc.sheet.create(sheet_name)
        sheet_id = res['spreadsheetId']
    except:
        pass
    sh = gc.open_by_key(sheet_id)
    print(f"Created spreadsheet with id:{sh.id} and url:{sh.url}")
    # Share with self to allow to write to it                                                                                                                                                                                                                                                                                         
    sh.share('yujinxian1212@gmail.com', role='writer', type='user')
    sh = gc.open(sheet_name)
    try:
        sh.sheet1.title = "Temperature"
        sh.add_worksheet("Rain")
    except:
        pass
    try:
        temp = sh[0] 
        temp.set_dataframe(df_temp,(1,1))
        rain = sh[1]
        rain.set_dataframe(df_rain,(1,1))
        return print("Successfuly write on google sheet")
    except:
        return print("Failed in writing on google sheet")

if __name__ == '__main__':
    parser = ArgumentParser()  
    parser.add_argument("--year", type=int, help="Input the year you want")
    parser.add_argument("--month", type =int, help="Input the month you want")
    args = parser.parse_args()
    save_google_sheet(args)
    conn.close()
