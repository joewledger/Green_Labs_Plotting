

def light_occupancy_pie_chart_single():
    return None

def light_occupancy_pie_chart_quad():
    return None

def state_bar_chart():
    return None

def active_energy_hourly_std_dev():
    return None

def temp_avg_hourly_std_dev():
    return None

def temp_avg_hourly_std_err():
    return None



graph_definitions = {"light" : [light_occupancy_pie_chart_single,light_occupancy_pie_chart_quad],
                     "state" : [state_bar_chart],
                     "power" : [active_energy_hourly_std_dev],
                     "temp" : [temp_avg_hourly_std_dev,temp_avg_hourly_std_err]
                     }


def determine_num_graphs(hobo_data_container):
    num_graphs_dict = {x : len(graph_definitions[x]) for x in graph_definitions.keys()}
    return num_graphs_dict[hobo_data_container.sensor_type]


def generate_graphs(hobo_data_container):
    return None