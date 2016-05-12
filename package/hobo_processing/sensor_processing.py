import pandas as pd
import math
import numpy as np

#This class is used for State and Lighting&Occupancy Data, i.e. data that is:
#   Taken whenever a new observation is made (not at even time increments)
#   Contains boolean data as opposed to real number data
#   Originally contained missing data, although this should be taken care of in pre-processing
class ObservationBasedDataProcessing():

    def __init__(self,hobo_data_container):
        self.hdc = hobo_data_container

    def series_time_percentage(self,series_name):
        time = pd.Timedelta('0 days')

        series = self.hdc.dataframe[series_name]
        time_stamps = pd.Series(series.index)
        time_differences = time_stamps.diff(periods=1).shift(periods=-1).fillna(pd.Timedelta('0 days'))

        for i,x in enumerate(series):
            if(x):
                time += time_differences[i]
        return time / self.hdc.total_time


#This class is used for Temperature and Power data, i.e. data that is:
#   Taken at even-time-increments
#   Contains no missing data (although after pre-processing the observation based data also should not have missing data)
#   Contains real number data as opposed to boolean data
class IntervalBasedDataProcessing():

    def __init__(self,hobo_data_container):
        self.hdc = hobo_data_container

    #Returns the list of the average value of a series within a given time interval (i.e. 1 hour)
    #Series name is the series from which to draw data (i.e. 'Temp, °F')
    #Interval length takes a pandas Timedelta object
    def calculate_interval_statistic(self,series_name,interval_length,resampler,start_time=None,end_time=None):
        closest_start,closest_end = self.get_closest_start_end_times(start_time,end_time)
        dataframe = self.hdc.dataframe.ix[start_time:end_time]
        series = dataframe[series_name]
        return series.resample(interval_length).apply(resampler)


    def interval_averages(self, series_name, interval_length,start_time=None,end_time=None):
        mean = lambda array_like : np.mean(array_like)
        return self.calculate_interval_statistic(series_name, interval_length,mean,start_time=start_time,end_time=end_time)

    def interval_std(self, series_name, interval_length,start_time=None,end_time=None):
        std_dev = lambda array_like : np.std(array_like)
        return self.calculate_interval_statistic(series_name, interval_length,std_dev,start_time=start_time,end_time=end_time)


    #Gets the start and end times closest to the provided start and end times in the dataframe
    #For the start time, it looks for the closest time before if there isn't an exact match
    #For the end time, it looks for the closest time after if there isn't an exact match
    #If either start_time or end_time are None, the start and end times of the entire dataframe are used
    def get_closest_start_end_times(self,start_time,end_time):

        if(start_time):
            closest_start = self.get_closest_timestamp(start_time)
        else:
            closest_start = self.hdc.date_range[0]

        if(end_time):
            closest_end = self.get_closest_timestamp(end_time,before=False)
        else:
            closest_end = self.hdc.date_range[1]

        return closest_start,closest_end


    #Returns the closest timestamp in the Hobo Data Container to the provided timestamp.
    #If there is an exact match, the exact match will be returned.
    #Otherwise:
    #   If the before flag is True, return the closest timestamp BEFORE the provided timestamp
    #   If the before flag is False, return the closest timestamp AFTER the provided timestamp
    #Returns nan if before is specified and there are no values before,
    #or if after is specified and there are no values after
    def get_closest_timestamp(self,time_stamp,before=True):
        if(time_stamp in self.hdc.dataframe.index):
            return time_stamp
        else:
            if(before):
                return self.hdc.dataframe.index.asof(time_stamp)
            else:
                prev = self.hdc.dataframe.index.asof(time_stamp)
                try:
                    location = self.hdc.dataframe.index.get_loc(prev)
                    return hdc.dataframe.iloc[location + 1]
                except:
                    return math.nan