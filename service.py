'''
SMWinservice
by Davide Mastromatteo

Base class to create winservice in Python
-----------------------------------------

Instructions:

1. Just create a new class that inherits from this base class
2. Define into the new class the variables
   _svc_name_ = "nameOfWinservice"
   _svc_display_name_ = "name of the Winservice that will be displayed in scm"
   _svc_description_ = "description of the Winservice that will be displayed in scm"
3. Override the three main methods:
    def start(self) : if you need to do something at the service initialization.
                      A good idea is to put here the inizialization of the running condition
    def stop(self)  : if you need to do something just before the service is stopped.
                      A good idea is to put here the invalidation of the running condition
    def main(self)  : your actual run loop. Just create a loop based on your running condition
4. Define the entry point of your module calling the method "parse_command_line" of the new class
5. Enjoy
'''

import socket

import win32serviceutil

import servicemanager
import win32event
import win32service

from src.db_cred import save_google_sheet
from dotenv import load_dotenv, find_dotenv
from plyer import notification
from pystray import Icon, MenuItem
import firebirdsql
import os, datetime, time, sys
from Settings import WidgetGallery
from PyQt6.QtWidgets import *
from PIL import Image

class SMWinservice(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'weatherautoreporter'
    _svc_display_name_ = 'Weather Reporter'
    _svc_description_ = 'Automatic Weather Report Service'

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        self.dotenv_file = find_dotenv()
        load_dotenv(self.dotenv_file)
        if self.dotenv_file == "":
            with open(".env", "w") as f:
                f.write(f'DB_PATH={os.getenv("DB_PATH")}\nDB_USER={os.getenv("DB_USER")}\nDB_PASSWORD={os.getenv("DB_PASSWORD")}\nUPDATE_FORMAT={os.getenv("UPDATE_FORMAT")}\nUPDATE_SCHEDULE={os.getenv("UPDATE_SCHEDULE")}\nSHARE_USER{os.getenv("SHARE_USER")}=\nCREDJSON={os.getenv("CREDJSON")}\n')
            f.close()
            self.dotenv_file = find_dotenv()
            load_dotenv(self.dotenv_file)
        
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        print("__init__: Service initial step")
        self.app = QApplication(sys.argv)
        self.gallery = WidgetGallery(env_path=self.dotenv_file)
        

        self.day_of_week = ["Mon", "Thu", "Wed", "Thur", "Fri", "Sat", "Sun"]
        self.root_path = os.path.dirname(__file__)
        image_path = os.path.join(self.root_path,'src\\assets\icon.webp')  # change this path to the image file you have
        img_direct = Image.open(image_path)
        
        self.icon = Icon('My System Tray Icon', img_direct, 'My System',  menu=(
            MenuItem('Settings', self.show_from_taskbar),
            MenuItem('Quit', self.quit_action)))  

    def show_from_taskbar(self):
        self.icon.stop()
        self.gallery.show()
        self.app.exec()

    def quit_action(self):
        self.icon.stop()
        self.SvcStop()

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        print("Hello Here!!")
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.icon.run(self.main)

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        pass

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        '''
        pass

    def main(self, icon):
        print("Main Step")
        icon.visible = True
        while True:
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
                if second%unit < 60:
                    self.generate_sheet()
            elif update_method == 'Monthly':
                schedule = update_schedule.split("#")
                date = f'{current_time.year}-{current_time.month}-{schedule[0]} {schedule[1]}'
                time_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if abs((current_time - time_obj).total_seconds()) < 60:
                    self.generate_sheet()
            elif update_method == 'Weekly':
                schedule = update_schedule.split("#")
                delta = self.day_of_week.index(schedule[0]) - current_time.weekday()
                delta = delta + 7 if delta < 0 else 0
                day = current_time.date() + datetime.timedelta(days=delta)
                date = f'{day.strftime("%Y-%m-%d")} {schedule[1]}'
                time_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if abs((current_time - time_obj).total_seconds()) < 60:
                    self.generate_sheet()
            elif update_method == 'Daily':
                date = f'{current_time.year}-{current_time.month}-{current_time.day} {update_schedule}'
                time_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if abs((current_time - time_obj).total_seconds()) < 60:
                    self.generate_sheet()

            time.sleep(60)

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
            users = os.getenv("SHARE_USER").split(",")
            if users != ['']:
                url = save_google_sheet(year=year, month=month, db=conn, users=users, cred=os.getenv("CREDJSON"))
                try:
                    notification.notify(
                        title = f'Successfully!',
                        message = f'The {month} report was successfully updated.\n{url}',
                        timeout = 10,
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
                    timeout = 10,
                    app_icon = os.path.join(self.root_path,'src\\assets\warning.ico')
                )
            except Exception as E:
                pass

# entry point of the module: copy and paste into the new module
# ensuring you are calling the "parse_command_line" of the new created class
if __name__ == '__main__':
    SMWinservice.parse_command_line()