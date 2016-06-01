import package.plotting.plotting as plotting
import package.hobo_processing.hobo_file_reader as hfr

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


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

    plotter = plotting.Light_Occupancy_Pie_Chart_Plotter(0)
    plotter.plotting_function(fig,hdc=hdc)

    plt.show()

def test_light_occupancy_pie_chart_quad():
    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_light_data.csv")

    plotter = plotting.Light_Occupancy_Pie_Chart_Quad_Plotter()
    plotter.plotting_function(fig,hdc=hdc)

    plt.show()

def test_temp_avg_hourly_std_dev():

    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_temperature_data_truncated4.csv")

    plotting.temp_avg_hourly_std_dev(fig,hdc=hdc)

    plt.show()

def test_get_supported_filetypes():

    canvas = plotting.MplCanvas()
    print(canvas.get_supported_filetypes())