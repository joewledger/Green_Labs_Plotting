from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import package.hobo_processing.hobo_file_reader as hfr
import package.plotting.implemented_plotters as imp_plt

from collections import *
import itertools


class CanvasCollection():

    def __init__(self, parent, color):
        self.parent = parent
        self.color = color
        self.hdc = None
        self.num_canvases = 0
        self.curr_canvas = 0

        self.canvas_list = []
        self.plotters = []

        self.initialize_plotter_type_map()
        self.initialize_blank_canvas_and_plotter()
        self.view_canvas(0)

    def initialize_plotter_type_map(self):
        self.plotter_type_map = {"state": self.initialize_state_plotters(),
                                 "light": self.initialize_light_plotters(),
                                 "power": self.initialize_power_plotters(),
                                 "temp": self.initialize_temp_plotters()}

    def initialize_state_plotters(self):
        plotters = [imp_plt.State_Bar_Chart_Plotter()]
        return plotters

    def initialize_light_plotters(self):
        plotters = [imp_plt.Light_Occupancy_Pie_Chart_Plotter(i) for i in range(0, len(imp_plt.Plotter.subset_functions))]
        plotters.append(imp_plt.Light_Occupancy_Pie_Chart_Quad_Plotter())
        return plotters

    def initialize_power_plotters(self):
        power_columns = hfr.HoboDataContainer.legal_columns["power"]
        plotters = [imp_plt.Hourly_Average_Plotter(column) for column in power_columns]
        plotters.extend([imp_plt.Single_Bar_Subinterval_Plotter(column) for column in power_columns])
        return plotters

    def initialize_temp_plotters(self):
        temp_columns = hfr.HoboDataContainer.legal_columns["temp"]
        plotters = [imp_plt.Hourly_Average_Plotter(column) for column in temp_columns]
        plotters.extend([imp_plt.Scatter_Plotter(list(x)) for x in itertools.combinations(temp_columns, 2)])
        plotters.extend([imp_plt.Single_Bar_Subinterval_Plotter(column) for column in temp_columns])
        return plotters

    def initialize_blank_canvas_and_plotter(self):
        self.canvas_list.append(MplCanvas(parent=self.parent, color=self.color))
        self.plotters.append(imp_plt.Plotter())
        self.plotters[0].plot(self.canvas_list[0], None)

    def update_hobo_data_container(self, hdc):
        self.initialize_plotters_and_canvases(hdc.sensor_type)
        self.update_plots(hdc)

    def initialize_plotters_and_canvases(self, hobo_data_type):
        self.canvas_list = [self.canvas_list[0]]
        self.plotters = [self.plotters[0]]
        plotter_objects = self.plotter_type_map[hobo_data_type]
        self.num_canvases = len(plotter_objects)

        for item in plotter_objects:
            self.canvas_list.append(MplCanvas(parent=self.parent, color=self.color))
            self.plotters.append(item)

    def update_plots(self, hdc):
        self.hdc = hdc
        faulty_plotters = []
        for i, plotter in enumerate(self.plotters):
            try:
                plotter.plot(self.canvas_list[i], self.hdc)
            except:
                faulty_plotters.append(i)
        self.remove_faulty_plotters(faulty_plotters)
        self.view_canvas(1)

    def remove_faulty_plotters(self, faulty_plotters):
        for index in reversed(faulty_plotters):
            del(self.canvas_list[index])
            del(self.plotters[index])
            self.num_canvases -= 1

    def update_curr_plot_params(self, parameter_collection):
        curr_canvas = self.get_current_canvas()
        curr_plotter = self.get_current_plotter()

        curr_plotter.update_parameters(parameter_collection)
        curr_plotter.plot(curr_canvas, self.hdc)

    def view_canvas(self, n):
        self.canvas_list[self.curr_canvas].setVisible(False)
        self.curr_canvas = n
        self.canvas_list[self.curr_canvas].setVisible(True)

    def save_current(self, save_location):
        self.canvas_list[self.curr_canvas].figure.savefig(save_location)

    def get_current_canvas(self):
        return self.canvas_list[self.curr_canvas]

    def get_current_plotter(self):
        return self.plotters[self.curr_canvas]


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4.5, height=3.5, dpi=100, color="#F2EEEE"):

        self.fig = Figure(figsize=(width, height), dpi=dpi, frameon=True)
        self.fig.patch.set_facecolor(color)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setGeometry(QtCore.QRect(10, 30, 787, 590))
        self.setVisible(False)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
