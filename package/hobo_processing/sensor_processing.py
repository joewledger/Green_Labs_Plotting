import pandas as pd

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


class IntervalBasedDataProcessing():

    def __init__(self,hobo_data_container):
        self.hdc = hobo_data_container