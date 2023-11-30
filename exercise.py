import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        style = self.style()

        # Set the window and tray icon to something
        icon = style.standardIcon(QStyle.SP_MediaSeekForward)
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(icon))
        self.setWindowIcon(QIcon(icon))

        # Restore the window when the tray icon is double clicked.
        self.tray_icon.activated.connect(self.restore_window)

        # why this doesn't work?
        self.hide()
        self.setWindowFlags(self.windowFlags() & ~Qt.Tool)

    def event(self, event):
        if (event.type() == QEvent.WindowStateChange and 
                self.isMinimized()):
            # The window is already minimized at this point.  AFAIK,
            # there is no hook stop a minimize event. Instead,
            # removing the Qt.Tool flag should remove the window
            # from the taskbar.
            self.setWindowFlags(self.windowFlags() & ~Qt.Tool)
            self.tray_icon.show()
            return True
        else:
            return super(Example, self).event(event)

    # def closeEvent(self, event):
    #     reply = QMessageBox.question(
    #         self,
    #         'Message',"Are you sure to quit?",
    #         QMessageBox.DialogCode.Yes | QMessageBox.No,
    #         QMessageBox.No)

    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         self.tray_icon.show()
    #         self.hide()
    #         event.ignore()

    def restore_window(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.tray_icon.hide()
            # self.showNormal will restore the window even if it was
            # minimized.
            self.showNormal()

def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()