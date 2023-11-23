from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from dotenv import load_dotenv, set_key, find_dotenv
from datetime import datetime
import os

class UpdateScheduleSet(QDialog):
    
    def __init__(self, parent=None, env_path = str):
        super(UpdateScheduleSet, self).__init__(parent)
        self.env_path = env_path

        # Database Settings
        self.update_fromat = os.getenv('UPDATE_FORMAT')
        self.update_schedule = os.getenv('UPDATE_SCHEDULE')

        self.update_day()
        self.update_week()
        self.update_month()
        self.update_hours()
        self.update_day_week_month()

        self.createUpdateScheduleSettingGroupbox()
        self.init_set()

    def update_day(self):
        self.update_daily = QWidget()

        layout = QHBoxLayout()
        
        self.daliy_time = QTimeEdit(self.update_daily)
        self.daliy_time.timeChanged.connect(self.schedule_encode)

        layout.addWidget(self.daliy_time)
        layout.setContentsMargins(0,0,0,0)
        self.update_daily.setLayout(layout)

    def update_week(self):
        self.update_weekly = QWidget()
        layout = QHBoxLayout()

        self.days = QComboBox(self.update_weekly)
        self.days.addItems(["Mon", "Thu", "Wed", "Thur", "Fri", "Sat", "Sun"])
        self.days.currentTextChanged.connect(self.schedule_encode)

        self.week_time = QTimeEdit(self.update_weekly)
        self.week_time.timeChanged.connect(self.schedule_encode)
        layout.addWidget(self.days)
        layout.addWidget(self.week_time)

        self.update_weekly.setLayout(layout)
        self.update_weekly.setVisible(False)
    
    def update_month(self):
        self.update_monthly = QWidget()
        layout = QHBoxLayout()

        self.date = QSpinBox(self.update_monthly)
        self.date.setMinimum(1)
        self.date.setMaximum(30)
        self.date.valueChanged.connect(self.schedule_encode)

        self.month_time = QTimeEdit(self.update_weekly)
        self.month_time.timeChanged.connect(self.schedule_encode)

        layout.addWidget(self.date)
        layout.addWidget(self.month_time)

        self.update_monthly.setLayout(layout)
        self.update_monthly.setVisible(False)
    
    def choose_period(self, s):
        self.schedule_encode()
        if s == "Every Day":
            self.update_daily.setVisible(True)
            self.update_weekly.setVisible(False)
            self.update_monthly.setVisible(False)
        elif s == "Every Week":
            self.update_daily.setVisible(False)
            self.update_weekly.setVisible(True)
            self.update_monthly.setVisible(False)
        elif s == "Every Month":
            self.update_daily.setVisible(False)
            self.update_weekly.setVisible(False)
            self.update_monthly.setVisible(True)

    def update_day_week_month(self):
        self.update_daily_weekly_monthly = QWidget()
        
        layout = QGridLayout()

        self.methodComboBox = QComboBox(self.update_daily_weekly_monthly)
        self.methodComboBox.addItems(["Every Day", "Every Week", "Every Month"])
        self.methodComboBox.currentTextChanged.connect(self.choose_period)

        layout.addWidget(self.methodComboBox, 0, 0)
        layout.addWidget(self.update_daily, 0 , 1)
        layout.addWidget(self.update_weekly, 0, 1)
        layout.addWidget(self.update_monthly, 0, 1)
        layout.setHorizontalSpacing(0)
        layout.setContentsMargins(0,0,0,0)    

        self.update_daily_weekly_monthly.setLayout(layout)
        self.update_daily_weekly_monthly.setFixedWidth(250)

    def choose_unit(self):
        self.schedule_encode()
        if self.unitComboBox.currentText() == "hours":
            self.hourly_time.setMaximum(23)
        elif self.unitComboBox.currentText() == "minutes":
            self.hourly_time.setMaximum(59)

    def update_hours(self):
        self.update_hourly = QWidget()
        
        layout = QHBoxLayout()

        self.hourly_time = QSpinBox(self.update_hourly)
        self.hourly_time.setMinimum(1)
        self.hourly_time.setMaximum(23)
        self.hourly_time.valueChanged.connect(self.schedule_encode)

        self.unitComboBox = QComboBox(self.update_hourly)
        self.unitComboBox.addItems(["hours", "minutes"])
        self.unitComboBox.currentTextChanged.connect(self.choose_unit)

        layout.addWidget(self.hourly_time)
        layout.addWidget(self.unitComboBox)
        layout.setContentsMargins(0,0,0,0)

        self.update_hourly.setLayout(layout)

    def choose_method(self):
        self.schedule_encode()
        if self.radioButton1.isChecked():
            self.update_daily_weekly_monthly.setDisabled(False)
            self.update_hourly.setDisabled(True)
        elif self.radioButton2.isChecked():
            self.update_daily_weekly_monthly.setDisabled(True)
            self.update_hourly.setDisabled(False)
        else:
            self.update_daily_weekly_monthly.setDisabled(True)
            self.update_hourly.setDisabled(True)

    def createUpdateScheduleSettingGroupbox(self):
        self.topRightGroupBox = QGroupBox("Update Schedule")

        self.layout1 = QHBoxLayout()
        self.radioButton1 = QRadioButton("Update every")
        self.radioButton1.toggled.connect(self.choose_method)
        self.radioButton1.setChecked(True)

        self.layout1.addWidget(self.radioButton1)
        self.layout1.addWidget(self.update_daily_weekly_monthly)
        self.layout1.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.layout2 = QHBoxLayout()
        self.radioButton2 = QRadioButton("Update every")
        self.radioButton2.toggled.connect(self.choose_method)

        self.layout2.addWidget(self.radioButton2)
        self.layout2.addWidget(self.update_hourly)
        self.layout2.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.radioButton3 = QRadioButton("Never Update")
        self.radioButton3.toggled.connect(self.choose_method)

        layout = QVBoxLayout()
        layout.addLayout(self.layout1)
        layout.addLayout(self.layout2)
        layout.addWidget(self.radioButton3)

        self.topRightGroupBox.setLayout(layout)
        self.topRightGroupBox.setFixedHeight(150)

    def schedule_encode(self):
        if self.radioButton1.isChecked():
            sub_format = self.methodComboBox.currentText()
            if sub_format == "Every Day":
                os.environ["UPDATE_FORMAT"] = "Daily"
                time = str(self.daliy_time.time().toPyTime())
                os.environ["UPDATE_SCHEDULE"] = time
            elif sub_format == "Every Week":
                os.environ["UPDATE_FORMAT"] = "Weekly"
                days = self.days.currentText()  
                time = str(self.week_time.time().toPyTime())
                os.environ["UPDATE_SCHEDULE"] = f'{days}#{time}'
            elif sub_format == "Every Month":
                os.environ["UPDATE_FORMAT"] = "Monthly"
                days = self.date.value()  
                time = str(self.month_time.time().toPyTime())
                os.environ["UPDATE_SCHEDULE"] = f'{days}#{time}'
        elif self.radioButton2.isChecked():
            os.environ["UPDATE_FORMAT"] = "Hourly"
            currenttime = datetime.now()
            unit = self.unitComboBox.currentText()  
            time = str(self.hourly_time.value())
            os.environ["UPDATE_SCHEDULE"] = f'{unit}#{time}#{currenttime}'
            self.update_daily_weekly_monthly.setDisabled(True)
            self.update_hourly.setDisabled(False)
        else:
            os.environ["UPDATE_FORMAT"] = "None"
            os.environ["UPDATE_SCHEDULE"] = ""
            self.update_daily_weekly_monthly.setDisabled(True)
            self.update_hourly.setDisabled(True)
        set_key(self.env_path, "UPDATE_FORMAT", os.getenv("UPDATE_FORMAT"))
        set_key(self.env_path, "UPDATE_SCHEDULE", os.getenv("UPDATE_SCHEDULE"))

    def init_set(self):
        if self.update_fromat == 'None':
            self.radioButton3.setChecked(True)
        elif self.update_fromat == 'Hourly':
            self.radioButton2.setChecked(True)
            schedule = self.update_schedule.split("#")
            self.unitComboBox.setCurrentText(schedule[0])
            self.hourly_time.setValue(int(schedule[1]))
        elif self.update_fromat == 'Monthly':
            self.methodComboBox.setCurrentText("Every Month")
            schedule = self.update_schedule.split("#")
            self.date.setValue(int(schedule[0]))
            time_obj = datetime.strptime(schedule[1], '%H:%M:%S')
            self.month_time.setTime(time_obj.time())
        elif self.update_fromat == 'Weekly':
            self.methodComboBox.setCurrentText("Every Week")
            schedule = self.update_schedule.split("#")
            self.days.setCurrentText(schedule[0])
            time_obj = datetime.strptime(schedule[1], '%H:%M:%S')
            self.week_time.setTime(time_obj.time())
        elif self.update_fromat == 'Daily':
            self.methodComboBox.setCurrentText("Every Day")
            time_obj = datetime.strptime(self.update_schedule, '%H:%M:%S')
            self.daliy_time.setTime(time_obj.time())
            