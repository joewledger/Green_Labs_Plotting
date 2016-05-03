import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from package.ui import mainwindow,controllers
import package.hobo_processing.hobo_file_reader as hfr

class Application:

    def __init__(self):
        self.working_file = None
        self.save_directory = None

    def run(self):
        app = QApplication(sys.argv)
        window = QMainWindow()
        ui = mainwindow.Ui_MainWindow()
        ui.setupUi(window)
        controllers.setup_controllers(self,ui)

        h = hfr.HoboFileReader()


        window.show()
        app.exec_()


