#Takes a dictionary mapping Parameter Expectation objects to their default values
class Parameter_Collection():

    def __init__(self,param_dictionary):
        self.param_dict = param_dictionary

    def get_param_name_to_value_dict(self):
        return {x.param_name : self.param_dict[x] for x in self.param_dict.keys()}

    def unpack_names(self):
        return [x.param_name for x in self.param_dict.keys()]

    def unpack_values(self):
        return [x for x in self.param_dict.values()]

    def update_value(self,key,value):
        self.param_dict[key] = value

    def __getitem__(self,key):
        return self.param_dict[key]

    def __len__(self):
        return len(self.param_dict)

    def __str__(self):
        return str(self.param_dict)

    def __copy__(self):
        new = type(self)(self.param_dict)
        new.__dict__.update(sekf.__dict__)
        return new


class Parameter_Expectation():

    def __init__(self,param_name,param_type):
        self.param_name = param_name
        self.param_type = param_type

    def copy_new_list_length(self,n):
        return Parameter_Expectation(self.param_name,self.param_type.copy_new_list_length(n))

    def __str__(self):
        return self.param_name

class Param_Type_Wrapper():

    def __init__(self,_type,is_list=False,length=1):
        self._type = _type
        self.is_list = is_list
        self.length = length

    def copy_new_list_length(self,n):
        return Param_Type_Wrapper(self._type, is_list=self.is_list,length=n)