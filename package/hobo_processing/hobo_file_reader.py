import pandas as pd
import numpy
import package.utils.exceptions as ex

class HoboDataContainer():

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
        self.illegal_file_message = "File was not a vaild HOBO CSV file"

    def import_datafile(self,datafile):
        self.filename = datafile
        self.dataframe = self.read_data(datafile)
        self.valid_datafile = self.verify_valid_datafile()
        if(self.valid_datafile):
            self.sensor_type = self.infer_sensor_type()
            self.fields = self.dataframe.columns
            self.boolean_valued = self.infer_boolean_data()
            self.even_time_increments = self.infer_even_time_increments()
            self.missing_values = self.check_missing_values()
            self.date_range = self.get_date_range()
        else:
            raise ex.InvalidDatafileException(self.illegal_file_message)
        

    def read_data(self,datafile):
        try:
            return pd.from_csv(datafile)
        except:
            raise ex.InvalidDatafileException(self.illegal_file_message)

    def verify_valid_datafile(self):
        return None

    def infer_sensor_type(self):
        return None

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

