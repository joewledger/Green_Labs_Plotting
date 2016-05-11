import package.plotting.plotting as plotting
import package.hobo_processing.hobo_file_reader as hfr

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def test_light_occupancy_pie_chart_single():
	fig = plt.figure()
	axes = fig.add_subplot(111)

	hdc = hfr.HoboDataContainer()
	hdc.import_datafile("sample_data/sample_light_data.csv")

	plotting.light_occupancy_pie_chart_single(axes,hdc=hdc)
	plt.show()


