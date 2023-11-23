from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from dotenv import load_dotenv, set_key, find_dotenv
import os

class UserTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(UserTableModel, self).__init__()
        self._data = data


    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            try:
                return self._data[index.row()][index.column()]
            except:
                return None

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

class managerSharingUsers(QDialog):
    def __init__(self, parent=None, env_path=str):
        super(managerSharingUsers, self).__init__(parent)
        self.env_path = env_path
        data = self.load_data()
        self.data = UserTableModel(data)
        self.createmanageUsersDashboard()

    def createmanageUsersDashboard(self):
        self.manageUserDashboard = QWidget()

        layout = QVBoxLayout()

        title = QLabel("Users of weather report")
        self.add_user = QLineEdit()
        self.users = QTableView()
        
        # users.insertRow(1, Qt.Orientation.Horizontal, "hello")
        
        self.users.setModel(self.data)
        self.users.setColumnWidth(0, 200)
        self.users.horizontalHeader().setVisible(False)
        self.users.verticalHeader().setVisible(False)
        
        self.add_users = QPushButton(self)
        pixmapi = QStyle.StandardPixmap.SP_ArrowUp
        icon = self.style().standardIcon(pixmapi)
        self.add_users.setIcon(icon)
        self.add_users.setFixedSize(25, 25)
        self.add_users.clicked.connect(self.add_new_user)

        self.delete_users = QPushButton(self)
        pixmapi1 = QStyle.StandardPixmap.SP_ArrowDown
        icon1 = self.style().standardIcon(pixmapi1)
        self.delete_users.setIcon(icon1)
        self.delete_users.setFixedSize(25, 25)
        self.delete_users.clicked.connect(self.delete_new_users)

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.add_users)
        button_layout.addWidget(self.delete_users)

        layout.addWidget(title)
        layout.addWidget(self.users)
        layout.addLayout(button_layout)
        layout.addWidget(self.add_user)
        layout.setContentsMargins(0,5,5,5)

        self.manageUserDashboard.setLayout(layout)

    def add_new_user(self):
        try:
            user = self.add_user.text()
            if self.data._data == [[]]:
                self.data._data = [[user]]
            else:
                self.data._data.append([user]) if not [user] in self.data._data else True      
            self.users.model().layoutChanged.emit()
            self.users.setColumnWidth(0, 200)
            self.save_data()
        except:
            pass

    def delete_new_users(self):
        try:
            user = self.users.selectedIndexes()
            selected_user = user[0].data()
            k = self.data._data.index([selected_user])
            if self.data._data == [[selected_user]]:
                self.data._data = [[]]
            else:
                self.data._data.pop(k)
            self.users.model().layoutChanged.emit()
            self.add_user.setText(selected_user)
            self.users.setColumnWidth(0, 200)
            self.save_data()
        except:
            pass

    def load_data(self):
        user =  os.getenv("SHARE_USER")
        users = user if user else ""
        users = users.split(",")
        if users == ['']:
            return [[]]
        else:
            k = []
            for i in users:
                k.append([i])
            return k

    def save_data(self):
        if self.data._data == [[]]:
            os.environ["SHARE_USER"] = ""
        else:
            k = ''
            for i in self.data._data:
                k = k + "," + i[0]
            k = k.replace(",","", 1)
            os.environ["SHARE_USER"] = k
        set_key(self.env_path, "SHARE_USER", os.environ["SHARE_USER"])