from src.db_cred import save_google_sheet
from dotenv import load_dotenv, find_dotenv
from plyer import notification
from pystray import Icon, MenuItem
import firebirdsql
import os, datetime, time, sys
from Settings import WidgetGallery

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import threading

from PIL import Image

class Weather():

    def __init__(self):

        self.dotenv_file = find_dotenv()
        load_dotenv(self.dotenv_file)
        if self.dotenv_file == "":
            with open(".env", "w") as f:
                f.write("DB_PATH=\nDB_USER=\nDB_PASSWORD=\nUPDATE_FORMAT=\nUPDATE_SCHEDULE=\nSHARE_USER=\nCREDJSON=")
            f.close()
            self.dotenv_file = find_dotenv()
            load_dotenv(self.dotenv_file)
        self.app = QApplication(sys.argv)
        self.gallery = WidgetGallery(parent=None, env_path=self.dotenv_file)
        
        this_path = os.path.dirname(__file__)
        icon_image = QIcon(os.path.join(this_path,'src/assets/icon.ico'))

        self.day_of_week = ["Mon", "Thu", "Wed", "Thur", "Fri", "Sat", "Sun"]
        self.root_path = os.path.dirname(__file__)
        self.main_flag = True

        self.icon = QSystemTrayIcon()

        self.icon.setIcon(icon_image)

        self.icon.setVisible(True)

        ctmenu = QMenu()
        actionshow = ctmenu.addAction("Settings")
        actionshow.triggered.connect(self.show_from_taskbar)
        actionquit = ctmenu.addAction("Quit")
        actionquit.triggered.connect(self.quit_action)

        self.icon.setContextMenu(ctmenu)
        self.flag = True
        self.thread1 = threading.Thread(target=self.main)
        self.thread1.start()

    def show_from_taskbar(self):
        self.gallery.show()
        

    def quit_action(self):
        self.flag = False
        self.gallery.close()
        # self.close()
        time.sleep(5)
        self.thread1.join()
        self.app.exit()

    def main(self):
        while self.flag:
            current_time = datetime.datetime.now()
            update_method = os.getenv("UPDATE_FORMAT")
            update_schedule = os.getenv("UPDATE_SCHEDULE")
            print(update_method)
            print(update_schedule)
            if update_method == 'None':
                pass
            elif update_method == 'Hourly':
                schedule = update_schedule.split("#")
                time_obj = datetime.datetime.strptime(schedule[-1], '%Y-%m-%d %H:%M:%S.%f')
                second = (current_time - time_obj).total_seconds()
                unit = int(schedule[1])*60*(1 if schedule[0]=="minutes" else 60)
                print(second)
                if second%unit < 5:
                    self.generate_sheet()
            elif update_method == 'Monthly':
                schedule = update_schedule.split("#")
                date = f'{current_time.year}-{current_time.month}-{schedule[0]} {schedule[1]}'
                time_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if abs((current_time - time_obj).total_seconds()) < 5:
                    self.generate_sheet()
            elif update_method == 'Weekly':
                schedule = update_schedule.split("#")
                delta = self.day_of_week.index(schedule[0]) - current_time.weekday()
                delta = delta + 7 if delta < 0 else 0
                day = current_time.date() + datetime.timedelta(days=delta)
                date = f'{day.strftime("%Y-%m-%d")} {schedule[1]}'
                time_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if abs((current_time - time_obj).total_seconds()) < 5:
                    self.generate_sheet()
            elif update_method == 'Daily':
                date = f'{current_time.year}-{current_time.month}-{current_time.day} {update_schedule}'
                time_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if abs((current_time - time_obj).total_seconds()) < 5:
                    self.generate_sheet()

            time.sleep(5)

    def generate_sheet(self):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        try:
            conn = firebirdsql.connect(
                host='localhost',
                database=os.getenv("DB_PATH"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            user =  os.getenv("SHARE_USER")
            users = user if user else ""
            users = users.split(",")
            if users != [''] and users != []:
                url = save_google_sheet(year=year, month=month, db=conn, users=users, cred=os.getenv("CREDJSON"))
                try:
                    notification.notify(
                        title = f'Successfully!',
                        message = f'The {month} report was successfully updated.\n{url}',
                        timeout = 5,
                        app_icon = os.path.join(self.root_path,'src\\assets\success.ico')
                    )
                except Exception as E:
                    pass
            else:
                raise Exception("You don't input ueser of the weather report")
        except Exception as e:
            try:
                notification.notify(
                    title = f'Failed',
                    message = f'Failed to update the {month} weather report.\n {str(e)}',
                    timeout = 5,
                    app_icon = os.path.join(self.root_path,'src\\assets\warning.ico')
                )
            except Exception as E:
                pass
    
# entry point of the module: copy and paste into the new module
# ensuring you are calling the "parse_command_line" of the new created class
if __name__ == '__main__':

    weather = Weather()
    weather.icon.show()
    sys.exit(weather.app.exec())
    