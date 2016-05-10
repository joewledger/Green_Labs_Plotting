import pandas as pd
import numpy
import package.utils.exceptions as ex

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
        self.date_range = None
        self.dataframe = None
        self.missing_values = False
        self.boolean_valued = False
        self.even_time_increments = False

    def import_datafile(self,datafile,debug=False):
        self.filename = datafile
        if(debug):
            self.dataframe = self.read_data(datafile)
            self.trim_data()
            self.valid_datafile = self.verify_valid_datafile()
        else:
            try:
                self.dataframe = self.read_data(datafile)
                self.trim_data()
                self.valid_datafile = self.verify_valid_datafile()
            except:
                self.valid_datafile = False
        if(self.valid_datafile):
            self.sensor_type = self.infer_sensor_type()
            self.fields = self.dataframe.columns
            self.boolean_valued = self.infer_boolean_data()
            self.even_time_increments = self.infer_even_time_increments()
            self.missing_values = self.check_missing_values()
            self.date_range = self.get_date_range()
        

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
        check_timestamps = lambda df : all(type(x) == pandas.tslib.Timestamp for x in list(df.index))
        #Checks to make sure at least some of the valid column names are represented
        check_legal_column_names = lambda df : True
        return check_timestamps(self.dataframe) and check_legal_column_names(self.dataframe)

    #Infers a sensor type from the dataframe by comparing the columns of the dataframe against the legal column names
    #for each of the sensor types predefined in self.legal_columns
    def infer_sensor_type(self):
        columns = list(self.dataframe.columns)

        num_matching_columns = lambda sensor_type : sum(1 for col_name in columns if col_name in self.legal_columns[sensor_type])
        normalized_matching_columns = lambda sensor_type : float(num_matching_columns(sensor_type)) / len(self.legal_columns[sensor_type])

        scores = {sensor_type : normalized_matching_columns(sensor_type) for sensor_type in self.legal_columns.keys()}

        self.sensor_type = max(scores.keys(),key = lambda x : scores[x])
        

    def infer_boolean_data(self):
        return None

    def infer_even_time_increments(self):
        return None

    def check_missing_values(self):
        return None

    def get_date_range(self):
        return None

    def get_time_series(self,field_names, time_range, all_dates=False,
                        insert_even_time_increments=False,only_even_time_increments=False,even_time_increments=None):
        return None


class HoboTimeSeries():
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.field_names = []
        self.series_dict = {}
        self.boolean_valued = False
        self.inserted_values = False
        self.full = False