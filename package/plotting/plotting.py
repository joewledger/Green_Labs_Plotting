import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import pandas as pd
from datetime import timedelta
import package.hobo_processing.sensor_processing as sp
import numpy as np

class CanvasCollection():

    def __init__(self,parent,color):
        self.parent = parent
        self.color = color
        self.num_canvases = 0
        self.curr_canvas = 0
        self.canvas_list = [MplCanvas(parent=parent,color=color)]
        self.canvas_list[0].blank_canvas()


    def add_canvas(self,visible=False,plotting_func=None):
        self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
        self.num_canvases += 1
        return self.canvas_list[-1]

    def update_canvases(self,hdc):
        for key in graph_definitions.keys():
            if(hdc.sensor_type == key):
                for plotting_function in [x for x in graph_definitions[key]]:
                    self.add_canvas(visible=False).update_canvas(plotting_function,hdc=hdc)
        self.view_canvas(1)

    def view_canvas(self,n):
        self.canvas_list[self.curr_canvas].setVisible(False)
        self.curr_canvas = n
        self.canvas_list[self.curr_canvas].setVisible(True)


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4.5, height=3.5, dpi=100,color="#F2EEEE"):
   
        self.fig = Figure(figsize=(width, height), dpi=dpi,frameon=True)
        self.fig.patch.set_facecolor(color)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setGeometry(QtCore.QRect(10, 30, 800, 600))
        self.setVisible(False)
        
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def blank_canvas(self):
        
        self.setVisible(True)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

    def update_canvas(self, plotting_func,hdc=None):
        plotting_func(self.fig,hdc=hdc)
        self.draw()

def light_occupancy_pie_chart_single(figure,hdc=None):

    axes = figure.add_subplot(111)

    labels = {"Light On & Occ" : "Light on &\nOccupied",
              "Light On & Unocc" : "Light on &\nUnoccupied",
              "Light Off & Occ" : "Light off &\nOccupied",
              "Light Off & Unocc" : "Light off &\nUnoccupied"}

    colors = {"Light On & Occ" : "orange",
              "Light On & Unocc" : "red",
              "Light Off & Occ" : "green",
              "Light Off & Unocc" : "grey"}

    obdp = sp.ObservationBasedDataProcessing(hdc)

    percentages = {x : obdp.series_time_percentage(x) for x in labels.keys()}

    patches,text = axes.pie(list(percentages.values()),labels=list(labels.values()),colors=list(colors.values()))

    for t in text:
        t.set_fontsize(8)

    axes.set_aspect(1)
    axes.set_title("Thinkbox Light Usage Patterns")

def light_occupancy_pie_chart_quad(figure,hdc=None):

    colors = ["orange","red","green","grey"]
    legend_labels = ["Light on &\nOccupied","Light on &\nUnoccupied","Light off &\nOccupied","Light off &\nUnoccupied"]


    ax1 = figure.add_subplot(2,2,1)
    ax2 = figure.add_subplot(2,2,2)
    ax3 = figure.add_subplot(2,2,3)
    ax4 = figure.add_subplot(2,2,4)

    titles = {ax1 : "Weekdays, Buisness Hours", ax2 : "Weekdays, Non Buisness Hours", ax3 : "Weekends, Buisness Hours", ax4 : "Weekends, Non Buisness Hours"}

    for ax in [ax1,ax2,ax3,ax4]:


        patches,texts = ax.pie([.25,.25,.25,.25],colors=colors)
        ax.set_aspect(1)
        ax.set_title(titles[ax])
    figure.legend(patches,labels=legend_labels,loc='upper left',prop={'size':10})

    ax1.set_aspect(1)
    ax1.set_title("Buisness Hours")
    figure.suptitle("Thinkbox Light Usage Patterns",fontsize=16)

def state_bar_chart(figure,hdc=None):
    
    axes = figure.add_subplot(111)

    obdp = sp.ObservationBasedDataProcessing(hdc)
    
    closed_percentage = obdp.series_time_percentage('State')
    open_percentage = 1 - closed_percentage

    width = .2
    x_pos = np.arange(2)
    axes.bar(x_pos,[open_percentage,closed_percentage],width,align="center")

    axes.set_xticks(x_pos)
    axes.set_xticklabels(("Open","Closed"))
    axes.set_xlabel("Status")
    axes.set_ylabel("Percentage of Time")
    axes.set_aspect(1)
    axes.set_title("Thinkbox Laser Cutter Open/Closed Patterns")

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