from PyQt6.QtWidgets import *
from .db_cred import collecting_data, save_google_sheet, save_csv
from .preViewTable import TableModel
from .userTable import managerSharingUsers
from dotenv import load_dotenv, find_dotenv, set_key
import firebirdsql
import pandas as pd
import os, datetime
import webbrowser

class PreViewDatabase(QDialog):
    
    def __init__(self, parent=None, env_path=str):
        super(PreViewDatabase, self).__init__(parent)
        self.env_path = env_path

        # Database Settings
        self.parent = parent

        self.usersdashboard = managerSharingUsers(parent=self, env_path=self.env_path)
        
        self.dashboardWidget()
        self.previewTableWidget()

        self.createPreViewGroupBox()
    
    def createPreViewGroupBox(self):
        self.bottomLeftTabWidget = QGroupBox("PreView Data")

        layout = QHBoxLayout()

        layout.addWidget(self.table)
        layout.addWidget(self.setDashboard)

        self.bottomLeftTabWidget.setLayout(layout)
        pass
    
    def previewTableWidget(self):
        self.table = QTableView()
        year = self.year.value()
        month = self.month.value()
        try:
            conn = firebirdsql.connect(
                host='localhost',
                database=os.environ["DB_PATH"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"]
            )
            data = collecting_data(year=year, month=month, db=conn)
            data.pop('Time Period of observation')
        except:
            data = pd.DataFrame(data={'Date':[],'Max Temp':[], 'Min Temp':[], 'Temp at 7:00':[], 'Rain':[]})
        self.model = TableModel(data)
        self.table.setModel(self.model)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

    def dashboardWidget(self):
        self.setDashboard = QWidget()
        
        layout = QVBoxLayout()
        layout1 = QHBoxLayout()

        title_year = QLabel("Year: ")
        title_month = QLabel("Month: ")
        self.year = QSpinBox(self.setDashboard)
        self.year.setMinimum(2020)
        self.year.setMaximum(2023)
        self.year.setValue(datetime.datetime.now().year)

        self.month = QSpinBox(self.setDashboard)
        self.month.setMinimum(1)
        self.month.setMaximum(12)
        self.month.setValue(datetime.datetime.now().month)
        
        self.refresh_btn = QPushButton(self)
        pixmapi1 = QStyle.StandardPixmap.SP_BrowserReload
        icon1 = self.style().standardIcon(pixmapi1)
        self.refresh_btn.setIcon(icon1)
        self.refresh_btn.setFixedSize(25, 25)
        self.refresh_btn.clicked.connect(self.refresh_data)

        self.generate_gsheet = QPushButton("G.Sheet", self)
        self.generate_gsheet.clicked.connect(self.generate_report)

        self.generate_CSV_file = QPushButton("CSV", self)
        self.generate_CSV_file.clicked.connect(self.open_save_file)

        layout1.addWidget(title_year)
        layout1.addWidget(self.year)
        layout1.addWidget(title_month)
        layout1.addWidget(self.month)
        layout1.addWidget(self.refresh_btn)
        
        layout2 = QHBoxLayout()

        title = QLabel("Google Credential Key:")
        self.cred_json = QLineEdit()
        self.cred_json.setText(os.getenv("CREDJSON"))
        choose_btn = QPushButton("...", self)
        choose_btn.setFixedSize(20,20)
        choose_btn.clicked.connect(self.open_dialog)

        layout2.addWidget(self.cred_json)
        layout2.addWidget(choose_btn)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.generate_CSV_file)
        layout3.addWidget(self.generate_gsheet)

        layout.addLayout(layout1)
        layout.addWidget(title)
        layout.addLayout(layout2)
        layout.addWidget(self.usersdashboard.manageUserDashboard)
        layout.addLayout(layout3)

        self.setDashboard.setLayout(layout)
        self.setDashboard.setFixedWidth(220)

    def refresh_data(self):
        year = self.year.value()
        month = self.month.value()
        try:
            conn = firebirdsql.connect(
                host='localhost',
                database=os.environ["DB_PATH"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"]
            )
            data = collecting_data(year=year, month=month, db=conn)
            data.pop('Time Period of observation')
        except:
            data = pd.DataFrame(data={'Date':[],'Max Temp':[], 'Min Temp':[], 'Temp at 7:00':[], 'Rain':[]})

        self.model._data = data
        self.table.model().layoutChanged.emit()

    def generate_report(self):
        year = self.year.value()
        month = self.month.value()
        dlg = QMessageBox(self.parent)
        try:
            conn = firebirdsql.connect(
                host='localhost',
                database=os.environ["DB_PATH"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"]
            )
            users = os.getenv("SHARE_USER").split(",")
            if users != ['']:
                self.url = save_google_sheet(year=year, month=month, db=conn, users=users, cred=os.getenv("CREDJSON"))
                dlg.setWindowTitle("Successfully!")
                dlg.setText(f'Generated Google Sheet successfully!')
                dlg.setIcon(QMessageBox.Icon.Information)
                open_btn = dlg.addButton("Open", dlg.ButtonRole.ActionRole)
                open_btn.clicked.connect(self.open_url)
                dlg.exec()
            else:
                raise Exception("You don't input ueser of the weather report")
        except Exception as e:
            dlg.setWindowTitle("Failed!")
            dlg.setText(str(e))
            dlg.setIcon(QMessageBox.Icon.Critical)
            dlg.exec()
    
    def generate_csv(self, file_path):
        year = self.year.value()
        month = self.month.value()
        dlg = QMessageBox(self.parent)
        try:
            conn = firebirdsql.connect(
                host='localhost',
                database=os.environ["DB_PATH"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"]
            )
            if file_path != "":
                self.url = save_csv(year=year, month=month, db=conn, f_path=file_path)
                dlg.setWindowTitle("Successfully!")
                dlg.setText(f'Generated CSV successfully!')
                dlg.setIcon(QMessageBox.Icon.Information)
                open_btn = dlg.addButton("Open", dlg.ButtonRole.ActionRole)
                open_btn.clicked.connect(self.show_save_file)
                dlg.exec()
            else:
                raise Exception("You don't input ueser of the weather report")
        except Exception as e:
            dlg.setWindowTitle("Failed!")
            dlg.setText(str(e))
            dlg.setIcon(QMessageBox.Icon.Critical)
            dlg.exec()

    
    def open_dialog(self):
        fname = QFileDialog.getOpenFileName(parent=self.parent)
        os.environ["CREDJSON"] = fname[0]
        set_key(self.env_path, "CREDJSON", os.environ["CREDJSON"])
        self.cred_json.setText(fname[0])

    def open_save_file(self):
        file_filter = 'Data File (*.xlsx *.csv);'
        fname = QFileDialog.getSaveFileName(
            parent=self.parent,
            caption='Select a file',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='Excel File (*.xlsx *.xls *.csv)'
        )
        if fname[0]:
            self.save_file = fname[0]
            self.generate_csv(file_path=fname[0])
    
    def open_url(self):
        webbrowser.open(self.url)
    
    def show_save_file(self):
        os.startfile(self.save_file)