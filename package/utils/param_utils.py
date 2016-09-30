from copy import *


"""
The classes in this module are designed to allow plotters to specify what types of parameters they
want to request from the Graph Edit Widget, as well as to store the default values of these parameters.

For example, the Light_Occupancy_Pie_Chart_Plotter requests a title parameter (which is a string),
and a colors parameter (which is a list of 4 colors).

"""


class Parameter_Collection():

    #Initializes the parameter collection, using a dictionary that maps parameter expectations -> default values
    def __init__(self, param_dictionary):
        self.param_dict = param_dictionary
        self.expectation_list = list(self.param_dict.keys())
        self.current = 0
        self.high = len(self.expectation_list)

    #Returns a dictionary mapping parameter expectation names to the current value of that parameter expectation
    def get_param_name_to_value_dict(self):
        return {x.param_name: self.param_dict[x] for x in self.param_dict.keys()}

    #Returns a list of all the names of the parameter expectations
    def unpack_names(self):
        return [x.param_name for x in self.param_dict.keys()]

    #Returns a list of all the current values
    def unpack_values(self):
        return [x for x in self.param_dict.values()]

    #Updates the values of this parameter collection through the use of a dictionary
    #that maps parameter expectations -> new values
    #param_dict can be either a dictionary or an ordered_dictionary
    def update_values(self, param_dict):
        for key in param_dict.keys():
            self.param_dict[key] = param_dict[key]

    #Updates the values of this parameter collection through the use of another parameter_collection
    #
    def update_values_param_collection(self, parameter_collection):
        for key in parameter_collection.param_dict.keys():
            self.param_dict[key] = parameter_collection[key]

    #Gets default value for a given parameter expectation
    def __getitem__(self, key):
        return self.param_dict[key]

    def __len__(self):
        return len(self.param_dict)

    def __str__(self):
        return str(self.param_dict)

    def __iter__(self):
        return self

    def __next__(self):
        if(self.current >= self.high):
            self.current = 0
            raise StopIteration
        else:
            self.current += 1
            return self.expectation_list[self.current - 1]

    def __copy__(self):
        new = type(self)(self.param_dict)
        new.__dict__.update(self.__dict__)
        return new


#The Parameter Expectation class contains a the parameter name, and the type of parameter
class Parameter_Expectation():

    def __init__(self, param_name, param_type_wrapper):
        self.param_name = param_name
        self.param_type_wrapper = param_type_wrapper

    def copy_new_list_length(self, n):
        try:
            return Parameter_Expectation(self.param_name, self.param_type_wrapper.copy_new_list_length(n))
        except:
            return self

    def get_type(self):
        return self.param_type_wrapper._type

    def is_list(self):
        return self.param_type_wrapper.is_list

    def __str__(self):
        return self.param_name

    def __len__(self):
        return self.param_type_wrapper.length


#This class is used to 'wrap' the type of a given parameter
#For instance, if a given plotter is expecting 4 colors, a parameter expectation could be initialized as follows:
#param_utils.Parameter_Expectation("Color", param_utils.Param_Type_Wrapper(type(QColor()), is_list=True, length=4))
class Param_Type_Wrapper():

    def __init__(self, _type, is_list=False, length=1):
        self._type = _type
        self.is_list = is_list
        self.length = length

    def copy_new_list_length(self, n):
        return Param_Type_Wrapper(self._type, is_list=True, length=n)
