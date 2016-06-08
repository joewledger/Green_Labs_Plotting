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
import package.utils.param_utils as param_utils
from collections import *
import itertools

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
                                 "state" : self.initialize_state_plotters(),
                                 "light" : self.initialize_light_plotters(),
                                 "power" : self.initialize_power_plotters(),
                                 "temp" : self.initialize_temp_plotters()
                                }
                                
    def initialize_state_plotters(self):
        plotters = [State_Bar_Chart_Plotter()]
        return plotters

    def initialize_light_plotters(self):
        plotters = [Light_Occupancy_Pie_Chart_Plotter(i) for i in range(0,len(Plotter.subset_functions))]
        plotters.append(Light_Occupancy_Pie_Chart_Quad_Plotter())
        return plotters

    def initialize_power_plotters(self):
        power_columns = hfr.HoboDataContainer.legal_columns["power"]
        plotters = [Generic_Hourly_Average_Plotter(column) for column in power_columns]
        plotters.extend([Single_Bar_Subinterval_Plotter(column) for column in power_columns])
        return plotters

    def initialize_temp_plotters(self):
        temp_columns = hfr.HoboDataContainer.legal_columns["temp"]
        plotters = [Generic_Hourly_Average_Plotter(column) for column in temp_columns]
        plotters.extend([Generic_Scatter_Plotter(list(x)) for x in itertools.combinations(temp_columns,2)])
        plotters.extend([Single_Bar_Subinterval_Plotter(column) for column in temp_columns])
        return plotters


    def initialize_blank_canvas_and_plotter(self):
        self.canvas_list.append(MplCanvas(parent=self.parent,color=self.color))
        self.plotters.append(Plotter())
        self.plotters[0].plot(self.canvas_list[0],None)

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
        faulty_plotters = []
        for i,plotter in enumerate(self.plotters):
            try:
                plotter.plot(self.canvas_list[i],self.hdc)
            except:
                faulty_plotters.append(i)
        self.remove_faulty_plotters(faulty_plotters)
        self.view_canvas(1)

    def remove_faulty_plotters(self,faulty_plotters):
        for index in reversed(faulty_plotters):
            del(self.canvas_list[index])
            del(self.plotters[index])
            self.num_canvases -= 1

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

    subset_functions = OrderedDict([(lambda hdc : hdc, "Entire Study Period"),
                                    (lambda hdc : hdc.buisness_hours().weekdays(), "Weekdays during Buisness Hours"),
                                    (lambda hdc : hdc.non_buisness_hours().weekdays(), "Weekdays during Non-Buisness Hours"),
                                    (lambda hdc : hdc.buisness_hours().weekends(), "Weekends during Buisness Hours"),
                                    (lambda hdc : hdc.non_buisness_hours().weekends(), "Weekends during Non-Buisness Hours")])


    def __init__(self):
        self.parameters = self.get_default_parameters()

    def get_subset_functions(self):
        return list(self.subset_functions.keys())
        
    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([]))

    def plot(self,canvas,hdc):
        self.plotting_function(canvas.figure,hdc)
        canvas.draw()

    def plotting_function(self,figure,hdc):
        self.blank_canvas(figure)
        

    def blank_canvas(self,figure):
        axes = self.get_axes(figure)
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

    def get_axes(self,figure,subplot=111):
        axes = figure.add_subplot(subplot)
        axes.hold(False)
        return axes

    def update_parameters(self,parameter_collection):
        self.parameters.update_values_param_collection(parameter_collection)


class Light_Occupancy_Pie_Chart_Plotter(Plotter):

    def __init__(self,n):
        self.color_param = color_param.copy_new_list_length(4)
        self.hdc_labels = ['Light On & Occ', 'Light On & Unocc', 'Light Off & Occ', 'Light Off & Unocc']
        self.graph_labels = ["Light on &\nOccupied","Light on &\nUnoccupied","Light off &\nOccupied","Light off &\nUnoccupied"]
        self.base_title = "Lighting Patterns"
        self.title_gen = lambda n : "%s, %s" % (self.base_title, list(self.subset_functions.values())[n])
        self.subset_index = n
        
        Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, self.title_gen(self.subset_index)),
                                                             (self.color_param,[QColor(Qt.yellow),QColor(Qt.red),QColor(Qt.blue),QColor(Qt.green)])]))

    def plotting_function(self,figure,hdc):
        axes = self.get_axes(figure)
        subset_function = list(self.subset_functions.keys())[self.subset_index]
        patches,texts = self.subset_pie_chart(axes,hdc,self.parameters[title_param],self.graph_labels,subset_func = subset_function)


    def subset_pie_chart(self,axes,hdc,title,labels,subset_func= lambda hdc : hdc,autopct=True):
        
        copy_hdc = subset_func(hdc)

        colors = [c.name() for c in self.parameters[self.color_param]]
        percentages = [copy_hdc.series_time_percentage(x) for x in self.hdc_labels]


        if(autopct):
            patches,texts,autotexts = axes.pie(percentages,labels=labels,autopct='%1.1f%%',colors=colors,startangle=90)
            for patch,text,autotext,percent in zip(patches,texts,autotexts,percentages):
                self.reposition_texts(patch,text,autotext,percent)
        else:
            patches,texts = axes.pie(percentages,labels=labels,colors=colors,startangle=90)

        for t in texts:
            t.set_fontsize(8)

        axes.set_aspect(1)
        axes.set_title(title,fontsize=12)

        return patches,texts

    #Rotate texts and autotexts so they do not overlap with lines in the piecharts
    #Also Remove autotexts and texts if their corresponding percentage is less than 1%
    def reposition_texts(self,patch,text,autotext,percent):

        text_height = 1.1
        text_adjust = 8
        autotext_height = .6
        autotext_adjust = 15

        angle = lambda p : (p.theta2 + p.theta1) / 2
        new_x = lambda p,height,adjust : p.r * height * np.cos((angle(p) - adjust)*np.pi / 180)
        new_y = lambda p,height,adjust : p.r * height * np.sin((angle(p) - adjust)*np.pi / 180)
        new_position = lambda p,height,adjust : (new_x(p,height,adjust), new_y(p,height,adjust))
        patch_width = lambda p : p.theta2 - p.theta1

        if(patch_width(patch) < 10):
            a_x,a_y = new_position(patch,autotext_height,autotext_adjust)
            t_x,t_y = new_position(patch,text_height,text_adjust)

            autotext.set_position((a_x,a_y))
            text.set_position((t_x,t_y))

        autotext.set_fontsize(10)

        if(percent < .01):
            autotext.set_visible(False)
            text.set_visible(False)
        


class Light_Occupancy_Pie_Chart_Quad_Plotter(Light_Occupancy_Pie_Chart_Plotter):

    def __init__(self):
        self.subplot_titles = title_param.copy_new_list_length(4)
        Light_Occupancy_Pie_Chart_Plotter.__init__(self,0)
        
    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Lighting Patterns"),
                                                             (self.color_param,[QColor(Qt.yellow),QColor(Qt.red),QColor(Qt.blue),QColor(Qt.green)]),
                                                             (self.subplot_titles,["Weekdays, Buisness Hours","Weekdays, Non Buisness Hours","Weekends, Buisness Hours","Weekends, Non Buisness Hours"])]))

    def plotting_function(self,figure,hdc):

        colors = [c.name() for c in self.parameters[self.color_param]]
        subplot_titles = self.parameters[self.subplot_titles]

        axes = [figure.add_subplot(2,2,x) for x in range(1,5)]

        invisible_labels = ["" for x in range(0,4)]

        for i,ax in enumerate(axes):

            subset_func = list(self.subset_functions.keys())[i + 1]
            patches,texts = self.subset_pie_chart(ax,hdc,subplot_titles[i],invisible_labels,subset_func = subset_func,autopct=False)

        figure.legend(patches,labels=self.graph_labels,loc='upper left',prop={'size':8})

        figure.suptitle(self.parameters[title_param],fontsize=16)

#Line Plot with Hourly Averages for Interval Based Data
class Generic_Hourly_Average_Plotter(Plotter):

    def __init__(self,column_name):
        self.column_name = column_name
        Plotter.__init__(self)
        

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Average Hourly %s" % self.column_name),
                                                             (x_label_param, "Time"),
                                                             (y_label_param, self.column_name),
                                                             (color_param, QColor(Qt.blue))]))

    def plotting_function(self,figure,hdc):
        
        axes = self.get_axes(figure)

        hourly_averages = hdc.interval_averages(self.column_name,pd.Timedelta('1 hours'))
        hourly_std = hdc.interval_std(self.column_name,pd.Timedelta('1 hours'))

        dates = pd.to_datetime(hourly_averages.index).strftime("%m/%d %I %p")
        indices = [x for x in range(0,len(dates))]

        means = list(hourly_averages.values)
        stds = list(hourly_std.values)

        color = self.parameters[color_param].name()
        axes.errorbar(indices,means,yerr=stds,color=color,ecolor=color)

        axes.set_xlabel(self.parameters[x_label_param])
        axes.set_ylabel(self.parameters[y_label_param])

        if(len(indices) > 20):
            n_candidates = (x * 6 for x in range(1,10) if len(indices) / (x * 6) < 20)
            n = next(n_candidates)
            mod_n = lambda array,n : [x for i,x in enumerate(array) if i % n == 0]
            mod_indices = mod_n(indices,n)
            mod_dates = mod_n(dates,n)

        axes.set_xticks(mod_indices)
        axes.set_xticklabels(mod_dates,rotation="vertical")
        axes.set_xlim([0,len(indices)])
        figure.tight_layout()
        axes.set_title(self.parameters[title_param])

class Generic_Scatter_Plotter(Plotter):

    def __init__(self,columns):
        self.columns = columns
        Plotter.__init__(self)

    def get_default_parameters(self):
        default_title = "Scatter Plot: %s vs %s" % (self.columns[0],self.columns[1])
        return param_utils.Parameter_Collection(OrderedDict([(title_param, default_title),
                                                             (x_label_param, self.columns[0]),
                                                             (y_label_param, self.columns[1]),
                                                             (color_param, QColor(Qt.green))]))

    def plotting_function(self,figure,hdc):

        axes = self.get_axes(figure)

        averages = [hdc.interval_averages(c,pd.Timedelta('1 hours')) for c in self.columns]

        axes.scatter(averages[0],averages[1],color=self.parameters[color_param].name())

        axes.set_xlabel(self.parameters[x_label_param])
        axes.set_ylabel(self.parameters[y_label_param])
        axes.set_title(self.parameters[title_param])


class Generic_Bar_Plotter(Plotter):

    def __init__(self):
        Plotter.__init__(self)

    def single_bar_plot(self,axes,values,errors=None,title=None,title_fontsize=12,x_ticks=None,x_tick_fontsize=12,x_label=None,y_label=None,color="blue",rotation="horizontal"):

        min_y,max_y = self.get_min_max_values(values)
        ind = np.arange(len(values)) * (max_y / len(values))
        margin = .05
        width = ind[1] / 2

        if(errors):
            axes.bar(ind,values,width,align="center",color=color,yerr=errors,error_kw=dict(ecolor='black'))
        else:
            axes.bar(ind,values,width,align="center",color=color)

        axes.set_xlim([-width,ind[-1] + width])
        axes.set_xticks(ind)

        if(x_ticks): axes.set_xticklabels(x_ticks,rotation=rotation,fontsize=x_tick_fontsize)
        if(x_label): axes.set_xlabel(x_label)
        if(y_label): axes.set_ylabel(y_label)
        if(title): axes.set_title(title,fontsize=title_fontsize)
        axes.set_aspect(1)

    #Values and errors expect a list of tuples, of which each tuple contains two values (one for each of the twin bars)
    #bar_labels expects a tuple containing two strings
    def twin_bar_plot(self,axes,values,errors=None,title=None,title_fontsize=12,x_ticks=None,x_ticks_fontsize=12,rotation="horizontal",
                      x_label=None,y_label=None,bar_labels=None,colors=("blue","red")):
        
        min_y,max_y = self.get_min_max_values(values)
        ind = np.arange(len(values)) * (max_y / len(values))
        margin = .05
        width = ind[1] / 4

        unpack_tuples = lambda l,index : [x[index] for x in l]

        kwarg_list = [dict(align="center",color=colors[x]) for x in range(0,2)]
        if(errors):
            for x in range(0,2):
                kwarg_list[x]["yerr"] = unpack_tuples(errors,x)
                kwarg_list[x]["error_kw"] = dict(ecolor='black')

        rect1 = axes.bar(ind,unpack_tuples(values,0),width,**kwarg_list[0])
        rect2 = axes.bar(ind + width,unpack_tuples(values,1),width,**kwarg_list[1])

        axes.set_xticks(ind + width / 2)

        if(x_ticks): axes.set_xticklabels(x_ticks,rotation=rotation,fontsize=x_ticks_fontsize)
        if(x_label): axes.set_xlabel(x_label)
        if(y_label): axes.set_ylabel(y_label)
        if(title): axes.set_title(title,fontsize=title_fontsize)
        if(bar_labels): axes.legend((rect1[0], rect2[0]), bar_labels)
        axes.set_aspect(1)


    def twin_bar_plot_two_scales(self,axes,values,errors=None,title=None,title_fontsize=12,x_ticks=None,x_ticks_fontsize=12,rotation="horizontal"
                                  x_label=None,y_label=None,bar_labels=None,colors=("blue","red")):

        axes2 = axes.twinx()

        min_y,max_y = self.get_min_max_values(values)
        ind = np.arange(len(values)) * (max_y / len(values))
        margin = .05
        width = ind[1] / 4

        unpack_tuples = lambda l,index : [x[index] for x in l]

        kwarg_list = [dict(align="center",color=colors[x]) for x in range(0,2)]


        rect1 = axes.bar(ind,unpack_tuples(values,0),width,**kwarg_list[0])
        rect2 = axes2.bar(ind + width,unpack_tuples(values,1),width,**kwarg_list[1])

        if(x_ticks): axes.set_xticklabels(x_ticks,rotation=rotation,fontsize=x_ticks_fontsize)
        if(x_label): axes.set_xlabel(x_label)






    #Returns a tuple containing the highest and lowest numbers in a list of values
    #Can handle two cases: a list of floats, or a list of tuples of floats
    def get_min_max_values(self,values):
        if(all(type(x) in [float,np.float64] for x in values)):
            return min(values),max(values)
        elif(all(type(x) == tuple for x in values)):
            tuple_op = lambda l,op : op([op(item) for item in values])
            return tuple_op(values,min),tuple_op(values,max)


class State_Bar_Chart_Plotter(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Equipment Open/Closed Patterns"),
                                                              (x_label_param, "Status"),
                                                              (y_label_param, "Percentage of Time"),
                                                              (color_param, QColor(0,0,255))]))

    def plotting_function(self,figure,hdc):

        axes = self.get_axes(figure)
        closed_percentage = hdc.series_time_percentage('State')
        open_percentage = 1 - closed_percentage
        self.single_bar_plot(axes,[open_percentage,closed_percentage],title=self.parameters[title_param],
                                                                      x_ticks=("Open","Closed"),
                                                                      x_label=self.parameters[x_label_param],
                                                                      y_label=self.parameters[y_label_param],
                                                                      color=self.parameters[color_param].name()
                                                                      )


class Single_Bar_Subinterval_Plotter(Generic_Bar_Plotter):

    def __init__(self,column_name):
        self.column_name = column_name
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Recorded Patterns: %s" % self.column_name),
                                                              (x_label_param, "Time Period"),
                                                              (y_label_param, "Average Value: %s" % self.column_name),
                                                              (color_param, QColor(0,0,255))]))

    def plotting_function(self,figure,hdc):

        axes = self.get_axes(figure)

        values = []
        errors = []
        x_ticks = []

        x_tick_format = lambda label : label.replace(" during ","\n")

        for subset_function in self.get_subset_functions()[1:]:
            copy_hdc = subset_function(hdc)
            values.append(copy_hdc.series_average(self.column_name))
            errors.append(copy_hdc.series_std(self.column_name))
            x_ticks.append(x_tick_format(self.subset_functions[subset_function]))

        self.single_bar_plot(axes,values,errors=errors,
                                         title=self.parameters[title_param],
                                         x_ticks=x_ticks,
                                         x_tick_fontsize=8,
                                         x_label=self.parameters[x_label_param],
                                         y_label=self.parameters[y_label_param],
                                         color=self.parameters[color_param].name(),
                                         rotation="vertical"
                                         )
        figure.tight_layout()


class Twin_Bar_Subinterval_Plotter(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Equipment Open/Closed Patterns"),
                                                              (x_label_param, "Status"),
                                                              (y_label_param, "Percentage of Time"),
                                                              (color_param, QColor(0,0,255))]))


class Twin_Bar_24_Hour_Average(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)



title_param = param_utils.Parameter_Expectation("Title",param_utils.Param_Type_Wrapper(str))
label_param = param_utils.Parameter_Expectation("Label",param_utils.Param_Type_Wrapper(str))
x_label_param = param_utils.Parameter_Expectation("X-Axis Label", param_utils.Param_Type_Wrapper(str))
y_label_param = param_utils.Parameter_Expectation("Y-Axis Label", param_utils.Param_Type_Wrapper(str))
color_param = param_utils.Parameter_Expectation("Color", param_utils.Param_Type_Wrapper(type(QColor())))