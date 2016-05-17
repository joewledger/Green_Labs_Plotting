import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import pandas as pd
from datetime import timedelta
import numpy as np

import package.hobo_processing.sensor_processing as sp
import package.utils.param_utils as param_utils

class CanvasCollection():

    def __init__(self,parent,color):
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
        self.plotter_type_map = {
                                 "state" : [State_Bar_Chart_Plotter],
                                 "light" : [Light_Occupancy_Pie_Chart_Single_Plotter,
                                            Light_Occupancy_Pie_Chart_Quad_Plotter]
                                }

    def initialize_blank_canvas_and_plotter(self):
        self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
        self.plotters.append(Plotter(self.canvas_list[-1]))
        self.plotters[-1].plot()

    #def add_canvas(self,plotting_func=None,hdc=None):
    #    self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
    #    self.plotters.append(Plotter(self.canvas_list[-1],plotting_func))
    #    self.plotters[-1].plot(hdc=hdc)
    #    self.num_canvases += 1

    #def update_canvases(self,hdc):
    #    self.canvas_list = [self.canvas_list[0]]
    #    self.plotters = [self.plotters[0]]
    #    self.num_canvases = 0
    #    self.curr_canvas = 0
    #    for key in graph_definitions.keys():
    #        if(hdc.sensor_type == key):
    #            for plotting_function in [x for x in graph_definitions[key]]:
    #                self.add_canvas(plotting_func=plotting_function,hdc=hdc)
    #    self.view_canvas(1)

    def update_hobo_data_container(self,hdc):
        self.canvas_list = [self.canvas_list[0]]
        self.plotters = [self.plotters[0]]
        self.hdc = hdc

        plotter_objects = self.plotter_type_map[self.hdc.sensor_type]
        self.num_canvases = len(plotter_objects)

        for item in plotter_objects:
            self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
            self.plotters.append(item(self.canvas_list[-1]))
            self.plotters[-1].plot(hdc=self.hdc)
        
        self.view_canvas(1)


    #def update_plotter_params(self,new_params,hdc=None):
    #    self.canvas_list[self.curr_canvas] = MplCanvas(parent=self.parent,color=self.color)
    #    self.plotters[self.curr_canvas].canvas = self.canvas_list[self.curr_canvas]
    #    self.plotters[self.curr_canvas].add_params(new_params)
    #    self.plotters[self.curr_canvas].plot(hdc=hdc)
    #    self.view_canvas(self.curr_canvas)

    def view_canvas(self,n):
        self.canvas_list[self.curr_canvas].setVisible(False)
        self.curr_canvas = n
        self.canvas_list[self.curr_canvas].setVisible(True)

    def save_current(self,save_location):
        self.canvas_list[self.curr_canvas].figure.savefig(save_location)

    def get_current_canvas(self):
        return self.canvas_list[self.curr_canvas]

    def get_current_plotter(self):
        return self.plotters[self.curr_canvas]


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
"""
class Plotter():

    def __init__(self,canvas,plotting_func):
        self.canvas = canvas
        self.plotting_func = plotting_func
        self.params = self.get_default_parameters()

    def get_default_parameters(self):
        return expected_params[self.plotting_func]

    def plot(self,hdc=None):
        self.plotting_func(self.canvas.figure,hdc=hdc,params=self.params)
        self.canvas.draw()
        print("Plotted")

    def add_params(self,new_params):
        for key in new_params:
            self.params.update_value(key,new_params[key])
"""

class Plotter():

    def __init__(self,canvas):
        self.canvas = canvas
        self.parameters = self.get_default_parameters()

    def get_plotting_function(self):
        return self.blank_canvas

    def get_default_parameters(self):
        return param_utils.Parameter_Collection({})

    def plot(self,hdc=None):
        self.plotting_function(self.canvas.figure,hdc=hdc,params = self.parameters)

    def plotting_function(self,figure,hdc=None,params=None):

        axes = figure.add_subplot(111)
        axes.hold(False)
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

    def add_params(self,new_params):
        for key in new_params:
            self.params.update_value(key,new_params[key])

class State_Bar_Chart_Plotter(Plotter):

    def __init__(self,canvas):
        Plotter.__init__(self,canvas)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection({title_param : "Equipment Open/Closed Patterns",
                                                           x_label_param : "Status",
                                                           y_label_param : "Percentage of Time"})

    def plotting_function(self,figure,hdc=None,params=None):
    
        axes = figure.add_subplot(111)
        obdp = sp.ObservationBasedDataProcessing(hdc)
        closed_percentage = obdp.series_time_percentage('State')
        open_percentage = 1 - closed_percentage
        width = .2
        x_pos = np.arange(2)
        axes.bar(x_pos,[open_percentage,closed_percentage],width,align="center")
        axes.set_xticks(x_pos)
        axes.set_xticklabels(("Open","Closed"))
        axes.set_xlabel(self.parameters[x_label_param])
        axes.set_ylabel(self.parameters[y_label_param])
        axes.set_aspect(1)
        axes.set_title(self.parameters[title_param])

class Light_Occupancy_Pie_Chart_Single_Plotter(Plotter):

    def __init__(self,canvas):
        Plotter.__init__(self,canvas)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection({})

    def plotting_function(self,figure,hdc=None,params=None):
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

class Light_Occupancy_Pie_Chart_Quad_Plotter(Plotter):

    def __init__(self,canvas):
        Plotter.__init__(self,canvas)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection({})

    def plotting_function(self,figure,hdc=None,params=None):
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

title_param = param_utils.Parameter_Expectation("Title",param_utils.Param_Type_Wrapper(str))
x_label_param = param_utils.Parameter_Expectation("X-Axis Label", param_utils.Param_Type_Wrapper(str))
y_label_param = param_utils.Parameter_Expectation("Y-Axis Label", param_utils.Param_Type_Wrapper(str))
color_param = param_utils.Parameter_Expectation("Color", param_utils.Param_Type_Wrapper(str))







"""
#Draws a blank canvas
def blank_canvas(figure,hdc=None,params=None):

    axes = figure.add_subplot(111)
    axes.hold(False)
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
"""

"""
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
    axes.set_xlabel(params[y_label_param])
    axes.set_ylabel(params[x_label_param])
    axes.set_aspect(1)
    axes.set_title(params[title_param])


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

expected_params = {blank_canvas : param_utils.Parameter_Collection({}),
                   state_bar_chart : param_utils.Parameter_Collection({title_param : "Equipment Open/Closed Patterns",
                                                           x_label_param : "Status",
                                                           y_label_param : "Percentage of Time"})
                   }
"""