import package.plotting.plotting as plotting
import package.hobo_processing.hobo_file_reader as hfr

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def test_light_occupancy_pie_chart_single():
    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_light_data_truncated.csv")

    plotting.light_occupancy_pie_chart_single(fig,hdc=hdc)
    plt.show()

def test_light_occupancy_pie_chart_quad():
    fig = plt.figure()

    hdc = hfr.HoboDataContainer()
    hdc.import_datafile("sample_data/sample_light_data_truncated.csv")

    plotting.light_occupancy_pie_chart_quad(fig,hdc=hdc)
    #print(fig.canvas.get_supported_filetypes())
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