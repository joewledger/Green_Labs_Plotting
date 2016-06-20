from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from package.ui import mainwindow, controllers
import package.hobo_processing.hobo_file_reader as hfr


class Application_Test:

    def __init__(self):
        self.window = None
        self.working_file = None
        self.save_directory = None
        self.curr_graph = 0
        self.graph_count = 0
        self.hobo_data_container = None

    def get_background_color(self):
        return "#F2EEEE"


def test_integration():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = mainwindow.Ui_MainWindow()
    ui.setupUi(window)

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_state_data.csv")


    main_controller = controllers.Main_Controller(Application_Test(), ui)
    main_controller.setup_controllers()
    main_controller.recieve_data_container(hdc)
    window.show()
    app.exec_()
