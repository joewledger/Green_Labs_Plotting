import package.hobo_processing.hobo_file_reader as hfr
import package.plotting.implemented_plotters as imp_plt

import matplotlib.pyplot as plt

from nose.tools import nottest


@nottest
def generic_test_plot(datafile, class_template, args=None):

    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile(datafile)

    plotter = (class_template(*args) if args else class_template())
    plotter.plotting_function(fig, hdc)

    plt.show()


def test_hourly_average_plotter():
    datafile = "sample_data/sample_temperature_data_truncated3.csv"
    class_template = imp_plt.Hourly_Average_Plotter
    args = ["RH, %"]
    generic_test_plot(datafile, class_template, args=args)


def test_scatter_plot():
    generic_test_plot("sample_data/sample_temperature_data_truncated4.csv", imp_plt.Scatter_Plotter, args=['Temp, °F', 'RH, %'])


def test_light_occupancy_pie_chart_single():
    generic_test_plot("sample_data/sample_light_data.csv", imp_plt.Light_Occupancy_Pie_Chart_Plotter, args=[3])


def test_light_occupancy_pie_chart_quad():
    generic_test_plot("sample_data/sample_light_data.csv", imp_plt.Light_Occupancy_Pie_Chart_Quad_Plotter)


def test_state_plot():
    generic_test_plot("sample_data/sample_state_data.csv", imp_plt.State_Bar_Chart_Plotter)


def test_single_bar_subinterval_temperature():
    generic_test_plot("sample_data/sample_temperature_data_truncated3.csv", imp_plt.Single_Bar_Subinterval_Plotter, args=['Temp, °F'])
