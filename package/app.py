import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from package.ui import mainwindow,controllers

class Application:

    def __init__(self):
        self.application_state = {}

    def run(self):
        app = QApplication(sys.argv)
        window = QMainWindow()
        ui = mainwindow.Ui_MainWindow()
        ui.setupUi(window)
        controllers.setup_controllers(ui)

        window.show()
        app.exec_()


