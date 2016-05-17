import sys
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from package.ui import mainwindow,controllers
import package.hobo_processing.hobo_file_reader as hfr

class Application:

    def __init__(self):
        self.window = None
        self.working_file = None
        self.save_directory = None
        self.curr_graph = 0
        self.graph_count = 0
        self.hobo_data_container = hfr.HoboDataContainer()
        self.graphs = []

    def run(self):
        app = QApplication(sys.argv)
        window = QMainWindow()
        self.window = window
        ui = mainwindow.Ui_MainWindow()
        ui.setupUi(window)
        main_controller = controllers.Main_Controller(self,ui)
        main_controller.setup_controllers()
        window.setWindowTitle("CWRU Green Labs Plotting Utility")
        window.show()
        app.exec_()

    def get_background_color(self):
        return self.window.palette().color(QtGui.QPalette.Background).name()