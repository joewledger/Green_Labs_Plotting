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

