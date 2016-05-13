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

        self.canvas_list = []
        self.plotters = []

        self.add_canvas(plotting_func=blank_canvas)
        self.view_canvas(0)
        self.num_canvases = 0

    def add_canvas(self,plotting_func=None,hdc=None):
        self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
        self.plotters.append(Plotter(self.canvas_list[-1],plotting_func))
        self.plotters[-1].plot(hdc=hdc)
        self.num_canvases += 1

    def update_canvases(self,hdc):
        self.canvas_list = [self.canvas_list[0]]
        self.plotters = [self.plotters[0]]
        self.num_canvases = 0
        self.curr_canvas = 0
        for key in graph_definitions.keys():
            if(hdc.sensor_type == key):
                for plotting_function in [x for x in graph_definitions[key]]:
                    self.add_canvas(plotting_func=plotting_function,hdc=hdc)
        self.view_canvas(1)

    def update_plotter_params(self,new_params,hdc=None):
        self.canvas_list[self.curr_canvas] = MplCanvas(parent=self.parent,color=self.color)
        self.plotters[self.curr_canvas].canvas = self.canvas_list[self.curr_canvas]
        self.plotters[self.curr_canvas].add_params(new_params)
        self.plotters[self.curr_canvas].plot(hdc=hdc)
        self.view_canvas(self.curr_canvas)

    def view_canvas(self,n):
        self.canvas_list[self.curr_canvas].setVisible(False)
        self.curr_canvas = n
        self.canvas_list[self.curr_canvas].setVisible(True)

    def save_current(self,save_location):
        self.canvas_list[self.curr_canvas].figure.savefig(save_location)


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4.5, height=3.5, dpi=100,color="#F2EEEE"):
   
        self.fig = Figure(figsize=(width, height), dpi=dpi,frameon=True)
        self.fig.patch.set_facecolor(color)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setGeometry(QtCore.QRect(10, 30, 787, 590))
        self.setVisible(False)
        
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

#Class that executes plotting functions on canvases and stores plot parameters
class Plotter():

    def __init__(self,canvas,plotting_func,params=None):
        self.canvas = canvas
        self.plotting_func = plotting_func
        self.params = (params if params else {})

    def plot(self,hdc=None):
        self.plotting_func(self.canvas.figure,hdc=hdc,params=self.params)
        self.canvas.draw()

    def add_params(self,new_params):
        for key in new_params:
            self.params[key] = new_params[key]

#Draws a blank canvas
def blank_canvas(figure,hdc=None,params=None):

    axes = figure.add_subplot(111)
    axes.hold(False)
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)


def light_occupancy_pie_chart_single(figure,hdc=None,params=None):

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

def light_occupancy_pie_chart_quad(figure,hdc=None,params=None):

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

def state_bar_chart(figure,hdc=None,params=None):
    
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



def temp_avg_hourly_std_dev(figure, hdc=None,params=None):

    axes = figure.add_subplot(111)

    ibdp = sp.IntervalBasedDataProcessing(hdc)

    hourly_averages = ibdp.interval_averages('Temp, °F',pd.Timedelta('1 hours'))
    hourly_std = ibdp.interval_std('Temp, °F',pd.Timedelta('1 hours'))

    dates = pd.to_datetime(hourly_averages.index).strftime("%m/%d %I %p")
    indices = [x for x in range(0,len(dates))]

    means = list(hourly_averages.values)
    stds = list(hourly_std.values)


    axes.plot(indices,means)
    axes.errorbar(indices,means,stds)
    axes.set_xlabel("Time")
    axes.set_ylabel("Average Temperature")
    if(len(indices) > 50):
        mod_12 = lambda array : [x for i,x in enumerate(array) if i % 12 == 0]
        indices = mod_12(indices)
        dates = mod_12(dates)
    axes.set_xticks(indices)
    axes.set_xticklabels(dates,rotation="vertical")
    axes.set_xlim([0,len(indices)])
    figure.tight_layout()
    axes.set_title(params.get("Title","Average Temperature in ThinkBox"))

def temp_average_by_time_of_day_bar_plot(figure,hdc=None,params=None):
    axes = figure.add_subplot(111)

def active_energy_hourly_std_dev(figure, hdc=None,params=None):
    axes = figure.add_subplot(111)

def temp_avg_hourly_std_err(figure, hdc=None,params=None):
    axes = figure.add_subplot(111)



graph_definitions = {"light" : [light_occupancy_pie_chart_single,light_occupancy_pie_chart_quad],
                     "state" : [state_bar_chart],
                     "power" : [active_energy_hourly_std_dev],
                     "temp" : [temp_avg_hourly_std_dev,temp_avg_hourly_std_err]
                     }


params_requested = {
    

}