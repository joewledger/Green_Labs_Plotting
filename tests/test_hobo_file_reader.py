import package.hobo_processing.hobo_file_reader as hfr


def test_read_data():
    hdc = hfr.HoboDataContainer()

    light_df = hdc.read_data("sample_data/sample_light_data.csv")
    assert list(light_df.columns) == ['Light', 'Occupancy', 'Light On & Occ', 'Light On & Unocc', 'Light Off & Occ', 'Light Off & Unocc']

    power_df = hdc.read_data("sample_data/sample_power_data.csv")
    assert list(power_df.columns) == ['RMS Voltage, V', 'RMS Voltage - Max, V', 'RMS Voltage - Min, V', 'RMS Voltage - Avg, V', 'RMS Current, A', 'RMS Current - Max, A', 'RMS Current - Min, A', 'RMS Current - Avg, A', 'Active Power, W', 'Active Power - Max, W', 'Active Power - Min, W', 'Active Power - Avg, W', 'Active Energy, Wh', 'Apparent Power, VA', 'Apparent Power - Max, VA', 'Apparent Power - Min, VA', 'Apparent Power - Avg, VA', 'Power Factor, PF', 'Power Factor - Max, PF', 'Power Factor - Min, PF', 'Power Factor - Avg, PF']

    state_df = hdc.read_data("sample_data/sample_state_data.csv")
    assert list(state_df.columns) == ["State"]

    temp_df = hdc.read_data("sample_data/sample_temperature_data.csv")
    assert list(temp_df.columns) == ['Temp, °F', 'RH, %', 'DewPt, °F']
    pass