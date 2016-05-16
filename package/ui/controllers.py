from package.utils import fileUtils
from package.plotting import plotting as plt

import package.hobo_processing.hobo_file_reader as hfr
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import threading

import package.ui.graph_edit_dialog as ged

class Communicate(QObject):
    signal = pyqtSignal(hfr.HoboDataContainer)

class Communicate_Dict(QObject):
    signal = pyqtSignal(dict)

class Main_Controller():

    def __init__(self,app,ui):
        self.app = app
        self.ui = ui
        background_color = self.app.get_background_color()
        self.canvas_collection =  plt.CanvasCollection(self.ui.centralWidget,background_color)
        self.graph_edit = None

    def setup_controllers(self):
        self.ui.file_select.clicked.connect(self.recieve_file_selection)
        self.ui.select_save_loc.clicked.connect(self.recieve_save_loc_selection)
        self.ui.generate_graphs.clicked.connect(self.recieve_generate_graphs)
        self.ui.view_previous.clicked.connect(self.recieve_view_previous)
        self.ui.view_next.clicked.connect(self.recieve_view_next)
        self.ui.save.clicked.connect(self.recieve_save)
        self.ui.edit_graph.clicked.connect(self.recieve_edit_graph)

    def recieve_save(self):
        #If there are any canvases besides the blank canvas
        if(not self.canvas_collection.num_canvases >= 1):
            self.save_error("No graphs to save")
        elif(not self.app.save_directory):
            self.save_error("No save location selected")
        elif(self.ui.save_file.text() == ""):
            self.save_error("No save file selected")
        elif(not self.determine_save_format()):
            self.save_error("No save format selected")
        else:
            save_format = self.determine_save_format()
            save_file = self.ui.save_file.text()
            save_file = (save_file if save_file.endswith(save_format) else save_file + save_format)
            save_directory = self.ui.display_save_loc.text()
            save_location = "%s/%s" % (save_directory,save_file)
            self.canvas_collection.save_current(save_location)

    def recieve_edit_graph(self):
        #curr_plotter = self.canvas_collection.get_current_plotter()
        #plotting_func = curr_plotter.plotting_func
        #print(" ".join(str(x) for x in plt.expected_params[plotting_func]))
        if(not self.check_unsaved_changes()):

            comm = Communicate_Dict()
            comm.signal.connect(self.recieve_graph_changes)
            requested_params = ["Title","X Axis","Y Axis"]
            default_values = {"Title" : "T","X Axis" : "X","Y Axis" : "Y"}
            graph_edit = ged.GraphEditWidget(requested_params,default_values,comm)
            graph_edit.show()
            self.graph_edit = graph_edit

    def recieve_graph_changes(self,change_dict):
        self.canvas_collection.update_plotter_params(change_dict,hdc = self.app.hobo_data_container)

    def save_error(self,message):
        msg = QMessageBox()
        msg.setWindowTitle("Save Error")
        msg.setText(message)
        msg.exec_()

    def determine_save_format(self):
        for radio_button in self.ui.groupBox.children():
            if(radio_button.isChecked()):
                return radio_button.text()

    def recieve_file_selection(self):
        file = fileUtils.fileDialog()
        self.ui.file_display.setText(file)
        self.app.working_file = file

    def recieve_save_loc_selection(self):
        save_directory = fileUtils.directoryDialog()
        self.ui.display_save_loc.setText(save_directory)
        self.app.save_directory = save_directory

    def recieve_generate_graphs(self):
        comm = Communicate()
        comm.signal.connect(self.recieve_data_container)
        self.start_import(comm,self.app.working_file)        

    def recieve_view_previous(self):
        self.generic_change_view(lambda x : x - 1)

    def recieve_view_next(self):
        self.generic_change_view(lambda x : x + 1)
        
    def generic_change_view(self,change_func):
        if(change_func(self.app.curr_graph) in range(1,self.app.graph_count + 1)):
            if(not self.check_unsaved_changes()):
                self.app.curr_graph = change_func(self.app.curr_graph)
                self.canvas_collection.view_canvas(self.app.curr_graph)
                self.set_graph_count()

    #Function checks if there is a graph_edit dialog open with unsaved changes
    #If there is, it prompts the user whether to keep the changes or not
    def check_unsaved_changes(self):
        if(self.graph_edit):
            if(self.graph_edit.unsaved_changes() and graph_edit.prompt_discard_unsaved_changes()):
                return True
        self.graph_edit = None
        return False

    def set_graph_count(self):
        self.ui.graph_count.setText("%d/%d" % (self.app.curr_graph,self.app.graph_count))

    def start_import(self,comm,datafile):  
        thread = threading.Thread(target=self.import_datafile,args=(datafile,comm,))
        thread.start()

    def import_datafile(self,datafile,comm):
        self.ui.generate_graphs.setEnabled(False)
        self.ui.program_status.setText("Importing Datafile")
        hdc = hfr.HoboDataContainer()
        hdc.import_datafile(datafile)
        comm.signal.emit(hdc)

    def recieve_data_container(self,hdc):
        self.app.hobo_data_container = hdc
        self.ui.program_status.setText("Generating Graphs")
        self.canvas_collection.update_canvases(self.app.hobo_data_container)
        self.app.curr_graph = 1
        self.app.graph_count = self.canvas_collection.num_canvases
        self.set_graph_count()
        self.ui.program_status.setText("Done Generating Graphs")
        self.ui.save_status.setText("Unsaved graphs")
        self.ui.generate_graphs.setEnabled(True)