#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

from typing import Optional
from PyQt6 import QtGui
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from src.dbset import DatabaseSet
from src.updateset import UpdateScheduleSet
from src.preview import PreViewDatabase
from src.db_cred import save_google_sheet
from dotenv import load_dotenv, find_dotenv
from plyer import notification
from pystray import Icon, MenuItem
from PIL import Image

import firebirdsql
import os, datetime, time, sys

class WidgetGallery(QDialog):
    
    def __init__(self, parent=None, env_path=str):
        super(WidgetGallery, self).__init__(parent)
        self.env_path = env_path
        # Database Settings
        DBSet = DatabaseSet(parent=self, env_path=self.env_path)
        UpdateSet = UpdateScheduleSet(parent=self, env_path=self.env_path)
        PreView = PreViewDatabase(parent=self, env_path=self.env_path)
        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)


        styleComboBox.textActivated.connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        topLayout.addWidget(self.useStylePaletteCheckBox)
        
        firstRow = QHBoxLayout()
        firstRow.addWidget(DBSet.databaseSetGroupBox)
        firstRow.addWidget(UpdateSet.topRightGroupBox)

        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(firstRow)
        mainLayout.addWidget(PreView.bottomLeftTabWidget)
        self.setLayout(mainLayout)

        this_path = os.path.dirname(__file__)
        self.setWindowTitle("Weather Reporter v1.1")
        self.setWindowIcon(QIcon(os.path.join(this_path,'src/assets/icon.ico')))
        self.changeStyle('Windows')

        self.day_of_week = ["Mon", "Thu", "Wed", "Thur", "Fri", "Sat", "Sun"]
        self.root_path = os.path.dirname(__file__)
        self.main_flag = True
        
        image_path = os.path.join(self.root_path,'src\\assets\icon.ico')  # change this path to the image file you have
        img_direct = Image.open(image_path)
        
        self.icon = Icon('My System Tray Icon', img_direct, 'My System',  menu=(
            MenuItem('Settings', self.show_from_taskbar),
            MenuItem('Quit', self.quit_action)))
        
        self.start_trayicon()
    
    def show_from_taskbar(self):
        self.icon.visible = False
        self.show()

    def quit_action(self):
        self.main_flag = False
        self.icon.stop()
    
    def main(self, icon):
        print("Main Step")
        self.icon.visible = True
        while self.main_flag:
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
    
    def start_trayicon(self):
        self.icon.run(self.main)

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)
        
    def hideEvent(self, a0:Optional[QHideEvent]=None) -> None:
        
        self.icon.visible = True
        return super().hideEvent(a0)
    
    def closeEvent(self, a0: Optional[QCloseEvent]=None) -> None:
        self.icon.visible = True
        return super().closeEvent(a0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)
    if dotenv_file == "":
        with open(".env", "w") as f:
            f.write("DB_PATH=\nDB_USER=\nDB_PASSWORD=\nUPDATE_FORMAT=\nUPDATE_SCHEDULE=\nSHARE_USER=\nCREDJSON=")
        f.close()
        dotenv_file = find_dotenv()
        load_dotenv(dotenv_file)
        gallery = WidgetGallery(env_path=dotenv_file)
        gallery.show()
        app.exec()
    else:
        gallery = WidgetGallery(env_path=dotenv_file)
        app.exec()    