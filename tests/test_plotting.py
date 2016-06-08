import package.plotting.plotting as plotting
import package.hobo_processing.hobo_file_reader as hfr

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def generic_test_plot(datafile,class_template,args=None):

    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile(datafile)


    if(args):
        plotter = class_template(args)
    else:
        plotter = class_template()

    plotter.plotting_function(fig,hdc=hdc)

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


def test_state_plot():

    generic_test_plot("sample_data/sample_state_data.csv",plotting.State_Bar_Chart_Plotter)

def test_single_bar_subinterval_temperature():

    generic_test_plot("sample_data/sample_temperature_data_truncated3.csv",plotting.Single_Bar_Subinterval_Plotter,args='Temp, °F')


def test_twin_bar_plot():

    data = [(.56,.43),(.75,.25),(.82,.35)]
    bar_plotter = plotting.Generic_Bar_Plotter()
    kwargs = {"title" : "Example"}

    generic_test_dummy_data(data,bar_plotter.twin_bar_plot,**kwargs)


def test_single_bar_subinterval():

    data = [75.4,76.3,78.2,74.9]
    bar_plotter = plotting.Generic_Bar_Plotter()
    generic_test_dummy_data(data,bar_plotter.single_bar_plot)



def test_generic_scatter_plot():

    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_temperature_data_truncated4.csv")

    plotter = plotting.Generic_Scatter_Plotter(['Temp, °F','RH, %'])
    plotter.plotting_function(fig,hdc=hdc)

    plt.show()




def test_average_temperature():
    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_temperature_data_truncated4.csv")

    plotter = plotting.Generic_Hourly_Average_Plotter('Temp, °F')
    plotter.plotting_function(fig,hdc=hdc)

    plt.show()



def test_light_occupancy_pie_chart_single():
    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_light_data.csv")

    plotter = plotting.Light_Occupancy_Pie_Chart_Plotter(3)
    plotter.plotting_function(fig,hdc=hdc)

    plt.show()

def test_light_occupancy_pie_chart_quad():
    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_light_data.csv")

    plotter = plotting.Light_Occupancy_Pie_Chart_Quad_Plotter()
    plotter.plotting_function(fig,hdc=hdc)

    plt.show()


def test_bar_plots():
    test_state_plot()
    test_single_bar_subinterval_temperature()

