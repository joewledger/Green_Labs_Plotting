class Plotter():

    subset_functions = OrderedDict([(lambda hdc : hdc, "Entire Study Period"),
                                    (lambda hdc : hdc.buisness_hours().weekdays(), "Weekdays\nBuisness Hours"),
                                    (lambda hdc : hdc.non_buisness_hours().weekdays(), "Weekdays\nNon-Buisness Hours"),
                                    (lambda hdc : hdc.buisness_hours().weekends(), "Weekends\nBuisness Hours"),
                                    (lambda hdc : hdc.non_buisness_hours().weekends(), "Weekends\nNon-Buisness Hours")])


    def __init__(self):
        self.parameters = self.get_default_parameters()

    def get_subset_functions(self):
        return list(self.subset_functions.keys())

    def get_subinterval_labels(self):
        return [self.subset_functions[f] for f in self.get_subset_functions()[1:]]

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


class Hourly_Average_Plotter(Plotter):

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


class Scatter_Plotter(Plotter):

    def __init__(self,columns):
        self.columns = columns
        Plotter.__init__(self)

    def get_default_parameters(self):
        default_title = "Scatter Plot: %s vs %s" % (self.columns[0],self.columns[1])
        return param_utils.Parameter_Collection(OrderedDict([(title_param, default_title),
                                                             (x_label_param, self.columns[0]),
                                                             (y_label_param, self.columns[1]),
                                                             (color_param, QColor(Qt.green))]))

    def get_data(self,hdc):
        return [hdc.interval_averages(c,pd.Timedelta('1 hours')) for c in self.columns]


    def plotting_function(self,figure,hdc):

        axes = self.get_axes(figure)

        data = self.get_data(hdc)

        axes.scatter(data[0],data[1],color=self.parameters[color_param].name())

        axes.set_xlabel(self.parameters[x_label_param])
        axes.set_ylabel(self.parameters[y_label_param])
        axes.set_title(self.parameters[title_param])

class State_Bar_Chart_Plotter(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return param_utils.Parameter_Collection(OrderedDict([(title_param, "Equipment Open/Closed Patterns"),
                                                              (x_label_param, "Status"),
                                                              (y_label_param, "Percentage of Time"),
                                                              (color_param, QColor(0,0,255))]))

    def get_data(self,hdc):
        closed_percentage = hdc.series_time_percentage('State')
        open_percentage = 1 - closed_percentage
        return [open_percentage,closed_percentage]


    def plotting_function(self,figure,hdc):

        axes = self.get_axes(figure)
        data = self.get_data(hdc)
        self.single_bar_plot(axes,data,title=self.parameters[title_param],
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

    def get_data(self,hdc):
        values,errors = [],[]
        for subset_function in self.get_subset_functions()[1:]:
            copy_hdc = subset_function(hdc)
            values.append(copy_hdc.series_average(self.column_name))
            errors.append(copy_hdc.series_std(self.column_name))
        return values,errors


    def plotting_function(self,figure,hdc):

        axes = self.get_axes(figure)

        values,errors = self.get_data(hdc)
        x_ticks = self.get_subinterval_labels()

        kwargs = dict(errors=errors, title=self.parameters[title_param], x_ticks=x_ticks, x_tick_fontsize=8, 
                      x_label=self.parameters[x_label_param], y_label=self.parameters[y_label_param], 
                      color=self.parameters[color_param].name(), rotation="vertical")

        self.single_bar_plot(axes,values, **kwargs)
        figure.tight_layout()

#Creates a subinterval bar plot, where each subinterval has two bars.
#The two bars can represent different quantities, but they should be plotted on the same scale
#Examples:
#   1) Bar 1: Light On Percentage, Bar 2: Occupied Percentage
#   2) Bar 1: Door Open, Bar 2: Door Closed
class Twin_Bar_Subinterval_Plotter(Generic_Bar_Plotter):

    def __init__(self,columns):
        self.columns = columns
        self.color_params = color_param.copy_new_list_length(2)
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return None

    def get_data(self):
        return None

    def plotting_function(self,figure,hdc):
        axes = self.get_axes(figure)


#Creates an hourly average bar plot, for which each hour has two bars.
#The two bars can represent different quantities, but they should be plotted on the same scale
#Examples:
#   1) Bar 1: Light On Percentage, Bar 2: Occupied Percentage
#   2) Bar 1: Door Open, Bar 2: Door Closed
class Twin_Bar_24_Hour_Average(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return None

    def get_data(self):
        return None

    def plotting_function(self,figure,hdc):
        axes = self.get_axes(figure)

#Creates an hourly bar plot
#The bar quantity can come from any interval based data reading
#   -> Temperature and Power data
class Single_Bar_Hourly_Average(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return None

    def get_data(self):
        return None

    def plotting_function(self,figure,hdc):
        axes = self.get_axes(figure)


#Creates a subinterval bar plot, where each subinterval has two bars
#Bars do NOT need to be quantities on the same scale, but must come from the same datafile
#Examples:
#   1) Temperature and RH
#   2) Voltage and Current
class Twin_Bar_Subinterval_Two_Scales_Plotter(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return None

    def get_data(self):
        return None

    def plotting_function(self,figure,hdc):
        axes = self.get_axes(figure)

#Creates a subinterval hourly average plot, where each subinterval has two bars
#Bars do NOT need to be quantities on the same scale, but must come from the same datafile
#Examples:
#   1) Temperature and RH
#   2) Voltage and Current
class Twin_Bar_Hourly_Average_Two_Scales_Plotter(Generic_Bar_Plotter):

    def __init__(self):
        Generic_Bar_Plotter.__init__(self)

    def get_default_parameters(self):
        return None

    def get_data(self):
        return None

    def plotting_function(self,figure,hdc):
        axes = self.get_axes(figure)

title_param = param_utils.Parameter_Expectation("Title",param_utils.Param_Type_Wrapper(str))
label_param = param_utils.Parameter_Expectation("Label",param_utils.Param_Type_Wrapper(str))
x_label_param = param_utils.Parameter_Expectation("X-Axis Label", param_utils.Param_Type_Wrapper(str))
y_label_param = param_utils.Parameter_Expectation("Y-Axis Label", param_utils.Param_Type_Wrapper(str))
color_param = param_utils.Parameter_Expectation("Color", param_utils.Param_Type_Wrapper(type(QColor())))