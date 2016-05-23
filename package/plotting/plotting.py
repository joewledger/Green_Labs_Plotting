import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import pandas as pd
from datetime import timedelta
import numpy as np

import package.hobo_processing.hobo_file_reader as hfr
import package.hobo_processing.sensor_processing as sp
import package.utils.param_utils as param_utils
from collections import *

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
                                 "state" : [State_Bar_Chart_Plotter()],
                                 "light" : [Light_Occupancy_Pie_Chart_Plotter(),
                                            Light_Occupancy_Pie_Chart_Quad_Plotter()],
                                 "power" : [],
                                 "temp" : [Generic_Hourly_Average_Plotter("Temp, °F")]
                                }
                                
        power_columns = hfr.HoboDataContainer.legal_columns["power"]
        for column in power_columns:
            self.plotter_type_map["power"].append(Generic_Hourly_Average_Plotter(column))

    def initialize_blank_canvas_and_plotter(self):
        self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
        self.plotters.append(Plotter())
        self.plotters[0].plot(self.canvas_list[0])

    def update_hobo_data_container(self,hdc):
        self.initialize_plotters_and_canvases(hdc.sensor_type)
        self.update_plots(hdc)

    def initialize_plotters_and_canvases(self,hobo_data_type):
        self.canvas_list = [self.canvas_list[0]]
        self.plotters = [self.plotters[0]]
        plotter_objects = self.plotter_type_map[hobo_data_type]
        self.num_canvases = len(plotter_objects)

        for item in plotter_objects:
            self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
            self.plotters.append(item)

    def update_plots(self,hdc):
        self.hdc = hdc
        for i,plotter in enumerate(self.plotters):
            plotter.plot(self.canvas_list[i],hdc=self.hdc)
        self.view_canvas(1)

    def update_curr_plot_params(self,parameter_collection):
        curr_canvas = self.get_current_canvas()
        curr_plotter = self.get_current_plotter()

        curr_plotter.update_parameters(parameter_collection)
        curr_plotter.plot(curr_canvas,self.hdc)

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


class Plotter():

    def __init__(self):
        self.parameters = self.get_default_parameters()

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([]))

    def plot(self,canvas,hdc=None):
        self.plotting_function(canvas.figure,hdc=hdc)
        canvas.draw()

    def plotting_function(self,figure,hdc=None):

        axes = self.get_axes(figure)
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

    def get_axes(self,figure,subplot=111):
        axes = figure.add_subplot(subplot)
        axes.hold(False)
        return axes

    def update_parameters(self,parameter_collection):
        self.parameters.update_values_param_collection(parameter_collection)

class State_Bar_Chart_Plotter(Plotter):

    def __init__(self):
        Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Equipment Open/Closed Patterns"),
                                                              (x_label_param, "Status"),
                                                              (y_label_param, "Percentage of Time"),
                                                              (color_param, QColor(0,0,255))]))

    def plotting_function(self,figure,hdc=None):
    
        axes = self.get_axes(figure)
        obdp = sp.ObservationBasedDataProcessing(hdc)
        closed_percentage = obdp.series_time_percentage('State')
        open_percentage = 1 - closed_percentage
        width = .2
        x_pos = np.arange(2)
        axes.bar(x_pos,[open_percentage,closed_percentage],width,align="center",color=self.parameters[color_param].name())
        axes.set_xlim([-width,x_pos[-1] + width])
        axes.set_xticks(x_pos)
        axes.set_xticklabels(("Open","Closed"))
        axes.set_xlabel(self.parameters[x_label_param])
        axes.set_ylabel(self.parameters[y_label_param])
        axes.set_aspect(1)
        axes.set_title(self.parameters[title_param])

class Light_Occupancy_Pie_Chart_Plotter(Plotter):

    def __init__(self):
        self.color_param = color_param.copy_new_list_length(4)
        Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Lighting Patterns"),
                                                             (self.color_param,[QColor(Qt.yellow),QColor(Qt.red),QColor(Qt.blue),QColor(Qt.green)])]))

    def plotting_function(self,figure,hdc=None,params=None):
        axes = self.get_axes(figure)

        colors = self.parameters[self.color_param]

        color = lambda i : colors[i].name()

        labels = {"Light On & Occ" : "Light on &\nOccupied",
                  "Light On & Unocc" : "Light on &\nUnoccupied",
                  "Light Off & Occ" : "Light off &\nOccupied",
                  "Light Off & Unocc" : "Light off &\nUnoccupied"}

        colors = {"Light On & Occ" : color(0),
                  "Light On & Unocc" : color(1),
                  "Light Off & Occ" : color(2),
                  "Light Off & Unocc" : color(3)}

        obdp = sp.ObservationBasedDataProcessing(hdc)

        percentages = {x : obdp.series_time_percentage(x) for x in labels.keys()}

        self.pie_chart(axes,percentages,labels,colors)

    def pie_chart(self,axes,percentages,labels,colors):
        patches,text = axes.pie(list(percentages.values()),labels=list(labels.values()),colors=list(colors.values()))

        for t in text:
            t.set_fontsize(8)

        axes.set_aspect(1)
        axes.set_title(self.parameters[title_param])


class Light_Occupancy_Pie_Chart_Quad_Plotter(Plotter):

    def __init__(self):
        Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([]))

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

class Generic_Hourly_Average_Plotter(Plotter):

    def __init__(self,column_name):
        Plotter.__init__(self)
        self.column_name = column_name

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Average Hourly Value"),
                                                             (x_label_param, "Time"),
                                                             (y_label_param, "Value")]))

    def plotting_function(self,figure,hdc=None,params=None):
        
        axes = self.get_axes(figure)
        ibdp = sp.IntervalBasedDataProcessing(hdc)

        hourly_averages = ibdp.interval_averages(self.column_name,pd.Timedelta('1 hours'))
        hourly_std = ibdp.interval_std(self.column_name,pd.Timedelta('1 hours'))

        dates = pd.to_datetime(hourly_averages.index).strftime("%m/%d %I %p")
        indices = [x for x in range(0,len(dates))]

        means = list(hourly_averages.values)
        stds = list(hourly_std.values)


        axes.plot(indices,means)
        axes.errorbar(indices,means,stds)
        axes.set_xlabel(self.parameters[x_label_param])
        axes.set_ylabel(self.parameters[y_label_param])

        if(len(indices) > 50):
            mod_12 = lambda array : [x for i,x in enumerate(array) if i % 12 == 0]
            indices = mod_12(indices)
            dates = mod_12(dates)

        axes.set_xticks(indices)
        axes.set_xticklabels(dates,rotation="vertical")
        axes.set_xlim([0,len(indices)])
        figure.tight_layout()
        axes.set_title(self.parameters[title_param])

title_param = param_utils.Parameter_Expectation("Title",param_utils.Param_Type_Wrapper(str))
x_label_param = param_utils.Parameter_Expectation("X-Axis Label", param_utils.Param_Type_Wrapper(str))
y_label_param = param_utils.Parameter_Expectation("Y-Axis Label", param_utils.Param_Type_Wrapper(str))
color_param = param_utils.Parameter_Expectation("Color", param_utils.Param_Type_Wrapper(type(QColor())))