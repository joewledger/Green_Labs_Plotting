import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import pandas as pd
from datetime import timedelta

class CanvasCollection():

    def __init__(self,parent,color):
        self.parent = parent
        self.color = color
        self.canvas_list = []
        self.num_canvases = 0
        self.curr_canvas = 0
        self.add_canvas(visible=True)

    def add_canvas(self,visible=False,plotting_func=None):
        self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color,visible=visible,plotting_func=plotting_func))
        self.num_canvases += 1
        return self.canvas_list[-1]

    def update_canvases(self,hdc):
        for key in graph_definitions.keys():
            if(hdc.sensor_type == key):
                plotting_functions = [x for x in graph_definitions[key]]
                self.canvas_list[0].update_axes(plotting_functions[0],hdc=hdc)
                for pf in plotting_functions[1:]:
                    self.add_canvas(visible=False).update_axes(pf,hdc=hdc)

    def view_canvas(self,n):
        self.canvas_list[self.curr_canvas].setVisible(False)
        self.curr_canvas = n
        self.canvas_list[self.curr_canvas].setVisible(True)


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4.5, height=3.5, dpi=100,color="#F2EEEE",visible=False,plotting_func=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        rect = fig.patch
        rect.set_facecolor(color)

        self.axes = fig.add_subplot(111)

        self.axes.hold(False)

        self.compute_initial_figure(plotting_func)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.setGeometry(QtCore.QRect(10, 30, 451, 331))
        self.setVisible(visible)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self,plotting_func):
        if(plotting_func):
            plotting_func(self.axes)
        else:
            self.axes.get_xaxis().set_visible(False)
            self.axes.get_yaxis().set_visible(False)

    def update_axes(self, plotting_func,hdc=None):
        plotting_func(self.axes,hdc=hdc)
        self.draw()

def light_occupancy_pie_chart_single(axes,hdc=None):

    labels = {"Light On & Occ" : "Light on and Occupied",
              "Light On & Unocc" : "Light on and Unoccupied",
              "Light Off & Occ" : "Light off and Occupied",
              "Light Off & Unocc" : "Light off and Unoccupied"}

    total_time = pd.Timedelta(hdc.date_range[1] - hdc.date_range[0])

    

    def series_time_percentage(series):
        time = pd.Timedelta('0 days')
        time_stamps = pd.Series(series.index)
        time_differences = time_stamps.diff(periods=1).shift(periods=-1).fillna(pd.Timedelta('0 days'))

        for i,x in enumerate(series):
            if(x):
                time += time_differences[i]
        return time / total_time

    percentages = {x : series_time_percentage(hdc.dataframe[x]) for x in labels.keys()}

    axes.pie(list(percentages.values()),labels=labels.keys())

def light_occupancy_pie_chart_quad(axes,hdc=None):
    axes.get_xaxis().set_visible(True)
    axes.get_yaxis().set_visible(True)
    axes.plot([1,2,3],[1,2,3])

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