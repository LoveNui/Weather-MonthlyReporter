from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from dotenv import load_dotenv, set_key, find_dotenv
import firebirdsql
import os

class DatabaseSet(QDialog):
 
    def __init__(self, parent=None, env_path=str):
        super(DatabaseSet, self).__init__(parent)
        self.env_path = env_path
        # Database Settings
        self.db_path = QLineEdit()
        self.db_user = QLineEdit()
        self.db_pass = QLineEdit()
        self.db_path.setText(os.getenv('DB_PATH'))
        self.db_path.textChanged[str].connect(self.update_setting)
        self.db_user.setText(os.getenv('DB_USER'))
        self.db_user.textChanged[str].connect(self.update_setting)
        self.db_pass.setText(os.getenv('DB_PASSWORD'))
        self.db_pass.textChanged[str].connect(self.update_setting)
        self.parent = parent
        
        
        self.createDataBaseSettingGroupbox()
    
    def open_dialog(self):
        fname = QFileDialog.getOpenFileName(parent=self.parent)
        self.db_path.setText(fname[0])

    def createDataBaseSettingGroupbox(self):
        self.databaseSetGroupBox = QGroupBox("Database")

        title1 = QLabel("Database Path: ")
        choose_btn = QPushButton("...", self)
        choose_btn.setFixedSize(20,20)
        choose_btn.clicked.connect(self.open_dialog)

        title2 = QLabel("User Name: ")
        self.db_user.setFixedSize(100, 23)
        
        title3 = QLabel("Password: ")
        self.db_pass.setFixedSize(100, 23)

        test_connect = QPushButton("Test", self)
        test_connect.clicked.connect(self.test_db_connection)

        checkBox = QCheckBox("Tri-state check box")
        checkBox.setTristate(True)
        checkBox.setCheckState(Qt.CheckState.PartiallyChecked)
        QBoxLayout
        layout = QGridLayout()
        layout.addWidget(title1, 0, 0)
        layout.addWidget(self.db_path, 0, 1, 1, 4)
        layout.addWidget(choose_btn, 0, 5)

        layout.addWidget(title2, 1, 0)
        layout.addWidget(self.db_user, 1, 1, 1, 2)
        layout.addWidget(title3, 1, 3)
        layout.addWidget(self.db_pass, 1, 4, 1, 2)

        layout.addWidget(test_connect, 4, 4)
        self.databaseSetGroupBox.setLayout(layout)
        self.databaseSetGroupBox.setFixedHeight(150)

    def update_setting(self):
        db_path = self.db_path.text()
        db_user = self.db_user.text()
        db_pass = self.db_pass.text()

        os.environ["DB_PATH"] = db_path
        os.environ["DB_USER"] = db_user
        os.environ["DB_PASSWORD"] = db_pass

        set_key(self.env_path, "DB_PATH", os.environ["DB_PATH"])
        set_key(self.env_path, "DB_USER", os.environ["DB_USER"])
        set_key(self.env_path, "DB_PASSWORD", os.environ["DB_PASSWORD"])

    def test_db_connection(self):
        try:
            conn = firebirdsql.connect(
                host='localhost',
                database=os.environ["DB_PATH"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"]
            )
            cur = conn.cursor()

            query =f'SELECT r.STATIONID, r.STATIONNAME FROM WEATHERSTATIONS r'
            cur.execute(query=query).fetchall()
            conn.close()
            dlg = QMessageBox(self.parent)
            dlg.setWindowTitle("Successfully!")
            dlg.setText("Connection to database successfully!")
            dlg.setIcon(QMessageBox.Icon.Information)
            dlg.exec()
        except Exception as e:
            print(e)
            dlg = QMessageBox(self.parent)
            dlg.setWindowTitle("Failed!")
            dlg.setText("Failed to connect to database.")
            dlg.setIcon(QMessageBox.Icon.Critical)
            dlg.exec()

