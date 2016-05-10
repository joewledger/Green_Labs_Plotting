from package.utils import fileUtils
from package.plotting import plotting as plt
from functools import partial

import package.hobo_processing.hobo_file_reader as hfr
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import threading


class Communicate(QObject):
    signal = pyqtSignal(hfr.HoboDataContainer)

class Main_Controller():

    def __init__(self,app,ui):
        self.app = app
        self.ui = ui

    def setup_controllers(self):
        self.ui.file_select.clicked.connect(self.recieve_file_selection)
        self.ui.select_save_loc.clicked.connect(self.recieve_save_loc_selection)
        self.ui.generate_graphs.clicked.connect(self.recieve_generate_graphs)
        self.ui.view_previous.clicked.connect(self.recieve_view_previous)
        self.ui.view_next.clicked.connect(self.recieve_view_next)

    def recieve_file_selection(self):
        file = fileUtils.fileDialog()
        self.ui.file_display.setText(file)
        self.app.working_file = file

    def recieve_save_loc_selection(self):
        save_loc = fileUtils.directoryDialog()
        self.ui.display_save_loc.setText(save_loc)
        self.app.save_loc = save_loc

    def recieve_generate_graphs(self):
        comm = Communicate()
        comm.signal.connect(self.recieve_data_container)
        self.start_import(comm,self.app.working_file)
    
    def recieve_view_previous(self):
        if(self.app.curr_graph in range(2,self.app.graph_count + 1)):
            self.app.curr_graph -= 1
            self.set_graph_count()

    def recieve_view_next(self):
        if(self.app.curr_graph in range(1,self.app.graph_count)):
            self.app.curr_graph += 1
            self.set_graph_count()

    def set_graph_count(self):
        self.ui.graph_count.setText("%d/%d" % (self.app.curr_graph,self.app.graph_count))

    def start_import(self,comm,datafile):  
        thread = threading.Thread(target=self.import_datafile,args=(datafile,comm,))
        thread.start()

    def import_datafile(self,datafile,comm):
        hdc = hfr.HoboDataContainer()
        hdc.import_datafile(datafile)
        comm.signal.emit(hdc)

    def recieve_data_container(self,hdc):
        self.app.hobo_data_container = hdc
        self.app.curr_graph = 1
        self.app.graph_count = plt.determine_num_graphs(self.app.hobo_data_container)
        self.set_graph_count()