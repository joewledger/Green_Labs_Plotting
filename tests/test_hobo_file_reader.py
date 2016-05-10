import package.hobo_processing.hobo_file_reader as hfr
import pandas
import numpy as np

def test_trim_data():

    def test_dataframe(filename,col_list):
        hdc = hfr.HoboDataContainer()
        hdc.dataframe = hdc.read_data(filename)
        hdc.trim_data()
        #Check to make sure _clean_column_names and _remove_dropable_columns worked correctly
        assert list(hdc.dataframe) == col_list
        #Check to make sure _remove_nan_columns worked
        assert not any(hdc.dataframe[x].isnull().all() for x in hdc.dataframe.columns)
        #Check to make sure _remove_duplicate_index_labels worked
        assert not hdc.dataframe.index.duplicated().any()
        #Check to make sure _remove_logging_information worked
        assert True

    light_file = "sample_data/sample_light_data.csv"
    state_file = "sample_data/sample_state_data.csv"
    power_file = "sample_data/sample_power_data_truncated.csv"
    temp_file = "sample_data/sample_temperature_data.csv"

    hdc = hfr.HoboDataContainer()

    test_dataframe(light_file,hdc.legal_columns["light"])
    test_dataframe(state_file,hdc.legal_columns["state"])
    test_dataframe(power_file,hdc.legal_columns["power"])
    test_dataframe(temp_file,hdc.legal_columns["temp"])


def test_remove_duplicate_index_labels():
    hdc = hfr.HoboDataContainer()

    hdc.dataframe = hdc.read_data("sample_data/sample_light_data.csv").head()
    assert hdc.dataframe.index.duplicated().any()
    hdc._remove_duplicate_index_labels()
    assert not hdc.dataframe.index.duplicated().any()


def test_remove_logging_information():

    hdc = hfr.HoboDataContainer()

    hdc.dataframe = hdc.read_data("sample_data/sample_power_data_truncated.csv")
    hdc._clean_column_names()
    hdc._remove_dropable_columns()
    hdc._remove_duplicate_index_labels()

    #Assert that the datafile has zero rows or null rows
    assert True
    hdc._remove_logging_information()
    #Assert that every row in the datafile is not-null and non-zero
    assert not False
    pass

def test_verify_valid_datafile():
    pass

def test_infer_sensor_type():

    def test_datafile(filename,label):
        hdc = hfr.HoboDataContainer()

        hdc.dataframe = hdc.read_data(filename)
        hdc._clean_column_names()
        hdc._remove_dropable_columns()
        hdc.infer_sensor_type()
        assert hdc.sensor_type == label

    test_datafile("sample_data/sample_power_data_truncated.csv","power")
    test_datafile("sample_data/sample_light_data.csv","light")
    test_datafile("sample_data/sample_temperature_data.csv","temp")
    test_datafile("sample_data/sample_state_data.csv","state")

def test_infer_boolean_data():

    def test_datafile(filename,label):

        hdc = hfr.HoboDataContainer()

        hdc.dataframe = hdc.read_data(filename)
        hdc.trim_data()
        hdc.infer_boolean_data()

        assert hdc.boolean_valued == label

    test_datafile("sample_data/sample_power_data_truncated.csv",False)
    test_datafile("sample_data/sample_light_data.csv",True)
    test_datafile("sample_data/sample_temperature_data.csv",False)
    test_datafile("sample_data/sample_state_data.csv",True)
    pass

def test_convert_boolean_data():

    def test_datafile(filename):
        hdc = hfr.HoboDataContainer()

        hdc.dataframe = hdc.read_data(filename)
        hdc.trim_data()
        hdc.convert_boolean_data()

        assert all(type(x) == np.dtype for x in list(hdc.dataframe.dtypes))

    test_datafile("sample_data/sample_light_data.csv")
    test_datafile("sample_data/sample_state_data.csv")

    pass

def test_infer_even_time_increments():
    pass

def test_infer_missing_values():
    hdc = hfr.HoboDataContainer()
    hdc.dataframe = hdc.read_data("sample_data/sample_temperature_data.csv")
    hdc.trim_data()
    hdc.infer_even_time_increments()
    print(hdc.even_time_increments)



def test_infer_date_range():
    hdc = hfr.HoboDataContainer()

    hdc.dataframe = hdc.read_data("sample_data/sample_light_data.csv")
    hdc.trim_data()
    hdc.infer_date_range()

    is_timestamp = lambda ts : type(ts) == pandas.tslib.Timestamp

    date_range = hdc.date_range
    assert is_timestamp(date_range[0]) and is_timestamp(date_range[1])
    pass

def test_import_datafile():
    hdc = hfr.HoboDataContainer()

    #hdc.import_datafile("sample_data/sample_light_data.csv") 
    #print(hdc.dataframe)

    hdc.import_datafile("sample_data/sample_temperature_data.csv") 
    print(hdc.dataframe)


