import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure



class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4.5, height=3.5, dpi=100,color="#F2EEEE"):
        fig = Figure(figsize=(width, height), dpi=dpi)
        rect = fig.patch
        rect.set_facecolor(color)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.setGeometry(QtCore.QRect(10, 30, 451, 331))

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

    def compute_new_figures(self, hdc):
        if(hdc.sensor_type == "light"):
            self.axes.plot([1,2,3],[3,2,1])
            self.draw()

def light_occupancy_pie_chart_single():
    return None

def light_occupancy_pie_chart_quad():
    return None

def state_bar_chart():
    return None

def active_energy_hourly_std_dev():
    return None

def temp_avg_hourly_std_dev():
    return None

def temp_avg_hourly_std_err():
    return None



graph_definitions = {"light" : [light_occupancy_pie_chart_single,light_occupancy_pie_chart_quad],
                     "state" : [state_bar_chart],
                     "power" : [active_energy_hourly_std_dev],
                     "temp" : [temp_avg_hourly_std_dev,temp_avg_hourly_std_err]
                     }


def determine_num_graphs(hobo_data_container):
    num_graphs_dict = {x : len(graph_definitions[x]) for x in graph_definitions.keys()}
    return num_graphs_dict[hobo_data_container.sensor_type]


def generate_graphs(hobo_data_container):
    return None