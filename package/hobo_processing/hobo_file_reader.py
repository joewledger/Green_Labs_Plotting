import pandas as pd
import numpy
import numpy as np

class HoboDataContainer():

    legal_columns = {
        "light" : ['Light', 'Occupancy', 'Light On & Occ', 'Light On & Unocc', 'Light Off & Occ', 'Light Off & Unocc'],
        "state" : ['State'],
        "power" : ['RMS Voltage, V', 'RMS Voltage - Max, V', 'RMS Voltage - Min, V', 'RMS Voltage - Avg, V', 'RMS Current, A', 'RMS Current - Max, A', 'RMS Current - Min, A', 'RMS Current - Avg, A', 'Active Power, W', 'Active Power - Max, W', 'Active Power - Min, W', 'Active Power - Avg, W', 'Active Energy, Wh', 'Apparent Power, VA', 'Apparent Power - Max, VA', 'Apparent Power - Min, VA', 'Apparent Power - Avg, VA', 'Power Factor, PF', 'Power Factor - Max, PF', 'Power Factor - Min, PF', 'Power Factor - Avg, PF'],
        "temp" : ['Temp, °F', 'RH, %', 'DewPt, °F']
    }

    illegal_file_message = "File was not a vaild HOBO CSV file"

    def __init__(self):
        self.filename = None
        self.valid_datafile = False
        self.sensor_type = None
        self.fields = None
        self.dataframe = None
        self.missing_values = False
        self.boolean_valued = False
        self.even_time_increments = False
        self.date_range = None
        #Stored as a pandas TimeDelta object
        self.total_time = None

    def import_datafile(self,datafile):

        self.filename = datafile
        try:
            self.dataframe = self.read_data(datafile)
            self.trim_data()
            self.verify_valid_datafile()
        except:
            self.valid_datafile = False

        if(self.valid_datafile):
            self.update_fields()

    def update_fields(self):
        self.infer_sensor_type()
        self.fields = self.dataframe.columns
        self.infer_boolean_data()
        if(self.boolean_valued):
            self.convert_boolean_data()
        self.infer_even_time_increments()
        self.infer_missing_values()
        self.infer_date_range()
        self.infer_total_time()

    def update_dataframe(self,update_func):
        self.dataframe = update_func(self.dataframe)
        self.update_fields()
        
    def read_data(self,datafile):
        return pd.read_csv(datafile,header=1,index_col=1,parse_dates=True)

    #trim_data and all of its helper methods assume that self.dataframe is populated with a valid pandas dataframe
    def trim_data(self):
        self._clean_column_names()
        self._remove_dropable_columns()
        self._remove_nan_columns()
        self._remove_duplicate_index_labels()
        self._remove_logging_information()

    #Removes items in parenthesis from column names
    def _clean_column_names(self):
        renamed_columns = {c : c[:c.find("(") - 1] if "(" in c else c for c in self.dataframe.columns}
        self.dataframe.rename(columns=renamed_columns, inplace=True)

    #Removes columns with junk data from dataframe
    def _remove_dropable_columns(self):
        dropable_columns = ["#", "Internal Calibration", "Host Connected", "Stopped", "End Of File", 
                            "Line Resume","Line Loss", "Button Down", "Button Up"]
        self.dataframe.drop(labels=dropable_columns,axis=1,inplace=True,errors='ignore')

    #remove columns that only contain NaN values
    def _remove_nan_columns(self):
        nan_columns = [x for x in list(self.dataframe.columns) if self.dataframe[x].isnull().all()]
        return self.dataframe.drop(labels=nan_columns,axis=1,inplace=True)

    #drop rows with duplicated index labels
    #leaves the last occuring duplicate: reasoning is that if a value has changed within one second,
    #we want to trust the most recent recording
    def _remove_duplicate_index_labels(self):
        self.dataframe = self.dataframe.groupby(self.dataframe.index).last()

    #remove rows with logging information (e.g. all 0'd out rows in power file)
    #Strategy: keep the data within the biggest gap between null rows, throw rest of data out
    def _remove_logging_information(self):

        index = list(self.dataframe.index)

        def empty_row_num_generator(df, ind):
            for i,x in enumerate(index):
                if(df.ix[x].isnull().all()):
                    yield i

        gen = empty_row_num_generator(self.dataframe, index)
        null_indices = [x for x in gen]

        if(len(null_indices) >= 2):

            differences = [null_indices[i] - null_indices[i-1] for i in range(1,len(null_indices))]
            max_index = max([i for i in range(0,len(differences))],key=lambda x : differences[x])

            keep_range = range(null_indices[max_index] + 1,null_indices[max_index + 1])

            drop_indices = [x for x in range(0,len(index)) if x not in keep_range]
            self.dataframe.drop(self.dataframe.index[drop_indices],inplace=True)
        elif(len(null_indices) == 1):
            self.dataframe.drop(self.dataframe.index[null_indices],inplace=True)

    #assumes that self.dataframe is already populated with a valid pandas dataframe
    def verify_valid_datafile(self):
        #Checks to make sure all index entries are Timestamp objects
        check_timestamps = lambda df : all(type(x) == pd.tslib.Timestamp for x in list(df.index))
        #Checks to make sure at least some of the valid column names are represented
        check_legal_column_names = lambda df : True
        self.valid_datafile = check_timestamps(self.dataframe) and check_legal_column_names(self.dataframe)

    #Infers a sensor type from the dataframe by comparing the columns of the dataframe against the legal column names
    #for each of the sensor types predefined in self.legal_columns
    def infer_sensor_type(self):
        columns = list(self.dataframe.columns)

        num_matching_columns = lambda sensor_type : sum(1 for col_name in columns if col_name in self.legal_columns[sensor_type])
        normalized_matching_columns = lambda sensor_type : float(num_matching_columns(sensor_type)) / len(self.legal_columns[sensor_type])

        scores = {sensor_type : normalized_matching_columns(sensor_type) for sensor_type in self.legal_columns.keys()}

        self.sensor_type = max(scores.keys(),key = lambda x : scores[x])
        

    def infer_boolean_data(self):
        boolean_values = [np.float64(0),np.float64(1)]
        is_boolean_column = lambda col_name : all(x in boolean_values for x in self.dataframe[col_name].dropna())
        self.boolean_valued = all(is_boolean_column(x) for x in self.dataframe.columns)


    def convert_boolean_data(self):
        self.dataframe.fillna(method="ffill",inplace=True)
        self.dataframe = self.dataframe.astype('bool')

    def infer_even_time_increments(self):
        index = list(self.dataframe.index)
        if(len(index) > 1):
            first_diff = index[1] - index[0]
            self.even_time_increments = all(index[i] - index[i-1] == first_diff for i in range(2,len(index)))
        else:
            self.even_time_increments = False

    def infer_missing_values(self):
        self.missing_values = self.dataframe.isnull().any()

    def infer_date_range(self):
        index = self.dataframe.index
        if(len(index) > 1):
            self.date_range = index[0],index[-1]
        else:
            self.date_range = None

    def infer_total_time(self):
        if(self.date_range):
            self.total_time = pd.Timedelta(self.date_range[1] - self.date_range[0])
        else:
            self.total_time = None


    def buisness_hours(self,inplace=False,start_time='9:00',end_time='17:00'):
        dataframe = self.dataframe
        integer_index = dataframe.index.indexer_between_time(start_time,end_time)
        copy_dataframe = dataframe.iloc[integer_index]

        return self._updated_object(copy_dataframe,inplace=inplace)

    def non_buisness_hours(self,inplace=False,start_time='9:00',end_time='17:00'):
        dataframe = self.dataframe
        integer_index = dataframe.index.indexer_between_time(start_time,end_time)
        buisness_hours_labels = dataframe.index[integer_index]
        copy_dataframe = dataframe.drop(buisness_hours_labels)

        return self._updated_object(dataframe,inplace=inplace)

    def weekdays(self,inplace=False,start_day=0,end_day=5):
        dataframe = self._get_filtered_dataframe_by_weekday_status(lambda x : x in range(start_day,end_day))
        return self._updated_object(dataframe,inplace=inplace)

    def weekends(self,inplace=False,start_day=0,end_day=5):
        dataframe = self._get_filtered_dataframe_by_weekday_status(lambda x : x not in range(start_day,end_day))
        return self._updated_object(dataframe,inplace=inplace)

    def _get_filtered_dataframe_by_weekday_status(self,filter_func):
        dataframe = self.dataframe
        weekday = [filter_func(x) for x in dataframe.index.weekday]
        copy_dataframe = dataframe.ix[weekday]
        return copy_dataframe


    def _updated_object(self,dataframe,inplace=False):

        object = (self if inplace else HoboDataContainer())
        object.dataframe = dataframe
        object.update_fields()
        return object

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

    #Defined for Observation based data
    #Gives the percentage of time that an observation is True
    def series_time_percentage(self,series_name):
        time = pd.Timedelta('0 days')

        series = self.dataframe[series_name]
        time_stamps = pd.Series(series.index)
        time_differences = time_stamps.diff(periods=1).shift(periods=-1).fillna(pd.Timedelta('0 days'))

        for i,x in enumerate(series):
            if(x):
                time += time_differences[i]
        return time / self.total_time

    #Defined for Interval based data
    #Calculates a statistic for a column of data in a given time range
    def calculate_interval_statistic(self,series_name,interval_length,resampler,start_time=None,end_time=None):
        closest_start,closest_end = self.get_closest_start_end_times(start_time,end_time)
        dataframe = self.dataframe.ix[start_time:end_time]
        series = dataframe[series_name]
        return series.resample(interval_length).apply(resampler)

    def interval_averages(self, series_name, interval_length,start_time=None,end_time=None):
        mean = lambda array_like : np.mean(array_like)
        return self.calculate_interval_statistic(series_name, interval_length,mean,start_time=start_time,end_time=end_time)

    def interval_std(self, series_name, interval_length,start_time=None,end_time=None):
        std_dev = lambda array_like : np.std(array_like)
        return self.calculate_interval_statistic(series_name, interval_length,std_dev,start_time=start_time,end_time=end_time)

    def __str__(self):
        return self.dataframe.__str__()