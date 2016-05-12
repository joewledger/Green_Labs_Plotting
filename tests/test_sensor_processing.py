import package.hobo_processing.sensor_processing as sp
import package.hobo_processing.hobo_file_reader as hfr

import pandas as pd
import math

def test_interval_averages():
	ibdp = setup_interval_processing()
	print(hdc.interval_averages('Temp, °F',pd.TimeDelta('1 hours')))

def test_closest_timestamp():
	
	ibdp = setup_interval_processing()

	assert math.isnan(ibdp.get_closest_timestamp(pd.Timestamp("2/25/2016 10:43:00 AM")))
	assert ibdp.get_closest_timestamp(pd.Timestamp("2/25/2016 10:44:53 AM")) == pd.Timestamp("2/25/2016 10:44:53 AM")
	assert ibdp.get_closest_timestamp(pd.Timestamp("2/25/2016 10:45:00 AM")) == pd.Timestamp("2/25/2016 10:44:53 AM")
	assert math.isnan(ibdp.get_closest_timestamp(pd.Timestamp("2/25/2016 10:45:00 AM"),before=False))
	pass

def setup_interval_processing():
	hdc = hfr.HoboDataContainer()
	hdc.import_datafile("sample_data/sample_temperature_data_truncated.csv")

	return sp.IntervalBasedDataProcessing(hdc)
