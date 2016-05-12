import package.hobo_processing.sensor_processing as sp
import package.hobo_processing.hobo_file_reader as hfr

import pandas as pd
import math
import numpy as np

def test_interval_averages():
	ibdp = setup_interval_processing()
	start_time = pd.Timestamp("2/25/2016 10:45:23 AM")
	end_time = pd.Timestamp("2/25/2016 10:47:53 AM")
	print(ibdp.interval_averages('Temp, °F',pd.Timedelta('1 minutes'),start_time=start_time,end_time=end_time))
	print(ibdp.interval_std('Temp, °F',pd.Timedelta('1 minutes'),start_time=start_time,end_time=end_time))

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
