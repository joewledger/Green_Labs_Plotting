import package.plotting.plotting as plotting
import package.hobo_processing.hobo_file_reader as hfr

import matplotlib.pyplot as plt

from nose.tools import nottest


#Tests a particular classes plotting_function with the specified datafile and arguments
#Any class that directly or indirectly subclasses Plotter can be tested using this method
@nottest
def generic_test_plot(datafile,class_template,args=None):

    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile(datafile)

    plotter = (class_template(args) if args else class_template())
    plotter.plotting_function(fig,hdc)

    plt.show()

#Tests plotting helper methods with dummy data
#To be tested using this method, the helper method must have the following parameter signature
#   method_call(self,axes,data,**kwargs)
#Some examples of methods that can be tested using this generic tester are below
#   Generic_Bar_Plotter.single_bar_plot
#   Generic_Bar_Plotter.twin_bar_plot
#   Generic_Bar_Plotter.twin_bar_plot_two_scales
#
#   Generic_Pie_Chart_Plotter.pie_chart <-- in the future
@nottest
def generic_test_dummy_data(data,plotting_function,**kwargs):

    fig = plt.figure()
    axes = fig.add_subplot(111)

    plotting_function(axes,data,**kwargs)

    plt.show()

#Tests Generic_Bar_Plotter.get_min_max_values()
def test_get_min_max_values():

    bar_plotter = plotting.Generic_Bar_Plotter()
    
    data = [(.56,.43),(.75,.25),(.82,.35)]
    assert(bar_plotter.get_min_max_values(data) == (.25,.82))

    data2 = [.45,.67,.54]
    assert(bar_plotter.get_min_max_values(data2) == (.45,.67))

##########################################################################################
#Bar Chart Tests
##########################################################################################

def test_state_plot():
    generic_test_plot("sample_data/sample_state_data.csv",plotting.State_Bar_Chart_Plotter)


def test_single_bar_subinterval_temperature():
    generic_test_plot("sample_data/sample_temperature_data_truncated3.csv",plotting.Single_Bar_Subinterval_Plotter,args='Temp, °F')


def test_all_bar_plots():
    test_twin_bar_plot_two_scales()
    test_twin_bar_plot()
    test_single_bar_plots()


def test_twin_bar_plot_two_scales():
    data = [(.56,.43),(.75,.25),(.82,.35),(.26,.89)]
    errors = [(.1,.05),(.12,.17),(.23,.32),(.45,.37)]
    y_labels = ["Label 1", "Label 2"]
    bar_plotter = plotting.Generic_Bar_Plotter()
    kwargs = dict(title = "Example",errors=errors,x_ticks=[1,2,3,4],y_labels=y_labels,x_label="Time")

    generic_test_dummy_data(data,bar_plotter.twin_bar_plot_two_scales,**kwargs)



def test_twin_bar_plot():

    data = [(.56,.43),(.75,.25),(.82,.35)]
    errors = [(.1,.05),(.12,.17),(.23,.32)]
    bar_plotter = plotting.Generic_Bar_Plotter()
    kwargs = dict(title = "Example",colors=("blue","red"),errors=errors,x_ticks=["Label 1", "Label 2", "Label 3"],
                  x_label="Time", y_label="Value", bar_labels=("Bar 1", "Bar 2"))

    generic_test_dummy_data(data,bar_plotter.twin_bar_plot,**kwargs)


def test_single_bar_plots():

    data = [75.4,76.3,78.2,74.9]
    bar_plotter = plotting.Generic_Bar_Plotter()
    kwargs = dict(x_ticks=["A","B","C","D"])
    generic_test_dummy_data(data,bar_plotter.single_bar_plot,**kwargs)


##########################################################################################
#Temperature and RH Tests
##########################################################################################

def test_generic_scatter_plot():
    generic_test_plot("sample_data/sample_temperature_data_truncated4.csv",plotting.Generic_Scatter_Plotter,args=['Temp, °F','RH, %'])


def test_average_temperature():
    generic_test_plot("sample_data/sample_temperature_data_truncated4.csv",plotting.Generic_Hourly_Average_Plotter,args='Temp, °F')


##########################################################################################
#Lighting and Occupancy Tests
##########################################################################################
def test_light_occupancy_pie_chart_single():
    generic_test_plot("sample_data/sample_light_data.csv",plotting.Light_Occupancy_Pie_Chart_Plotter,args=3)


def test_light_occupancy_pie_chart_quad():
    generic_test_plot("sample_data/sample_light_data.csv",plotting.Light_Occupancy_Pie_Chart_Quad_Plotter)