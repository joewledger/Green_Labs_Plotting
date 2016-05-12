import pandas as pd
import math


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
    #Interval length takes a pandas TimeDelta object
    def interval_averages(self, series_name, interval_length,start_time=None,end_time=None):

        if(start_time):
            curr_time = get_closest_timestamp(start_time)
        else:
            curr_time = self.hdc.dataframe.date_range[0]

        if(end_time):
            closest_end = get_closest_timestamp(self, end_time,before=False)
        else:
            closest_end = self.hdc.dataframe.date_range[1]

        return None

    def interval_std_devs(self, series_name, interval_length,start_time=None,end_time=None):
        return None


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