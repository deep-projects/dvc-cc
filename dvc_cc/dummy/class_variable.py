import numpy as np
import os

class Variable:
    original_value = None
    varname = None
    vartype = None
    varvalue = None


    def __init__(self, original_value, variables=None):
        self.original_value = original_value
        tmp = self.original_value.split(':')
        self.varname = tmp[0]

        if len(tmp) > 1:
            self.vartype = tmp[1]
        self.set_type_of_variable()
        if len(tmp) > 2:
            self.set_constant_value(tmp[2])

        if variables is not None and  self.varname in variables:
            return variables[self.varname]

    def set_constant_value(self, value):
        if value == None or value == '' or value.lower() == 'none':
            self.varvalue = None
        elif self.vartype == 'file':
            self.varvalue = str(value)
        elif self.vartype == 'ufloat':
            self.varvalue = np.cast[np.float](value)
            if self.varvalue < 0.0:
                print('Error: Only positive values are allowed for the datatype \'ufloat\'.')
        elif self.vartype == np.uint:
            if np.int(value) < 0.0:
                print('Error: Only positive values are allowed for the datatype \'uint\'.')
            else:
                self.varvalue = np.uint(value)
        else:
            try:
                self.varvalue = np.cast[self.vartype](value)
            except:
                print('Error: The value and the type does not match.')
       

    def set_type_of_variable(self):
        type_of_variable = None
        while type_of_variable is None:
            if self.vartype is None and self.vartype != '' and self.vartype != 'None':
                type_of_variable = input('What type of variable is the \''+self.varname+'\'? (float, ufloat, int, uint, file): ')
            else:
                type_of_variable = self.vartype
            type_of_variable = type_of_variable.lower()
            if type_of_variable.startswith('i'):
                type_of_variable = np.int
            elif type_of_variable.startswith('ui'):
                type_of_variable = np.uint
            elif type_of_variable.startswith('d'):
                type_of_variable = np.float
            elif type_of_variable.startswith('fl'):
                type_of_variable = np.float
            elif type_of_variable.startswith('ufl'):
                type_of_variable = 'ufloat'
            elif type_of_variable.startswith('ud'):
                type_of_variable = 'ufloat'
            elif type_of_variable.startswith('fi'):
                type_of_variable = 'file'
            else:
                print('Warning: Did not understand the datatype.')
                type_of_variable = None
        self.vartype = type_of_variable


    def __pretty_str__(self):
        tmp = str(self)[3:-3].split(':')
        return '%25s%8s%6s'%(tmp[0],tmp[1],tmp[2])

    def __str__(self):
        if self.vartype == 'file' or self.vartype == 'ufloat':
            vartype = self.vartype
        elif self.vartype is np.float:
            vartype = 'float'
        elif self.vartype is np.uint:
            vartype = 'uint'
        elif self.vartype is np.int:
            vartype = 'int'
    
        return '<<<' + self.varname+':'+ vartype +':'+ str(self.varvalue) + '>>>'

def find_all_variables(text, variables = {}, return_founded_variables=False):
    if type(text) is not list:
        text = [text]
    founded_var = {}
    for subc in text:
        start_pos = 0
        while start_pos >= 0:
            start_pos = subc.find('<<<', start_pos)
            if start_pos is not -1:
                end_pos = subc.find('>>>', start_pos)
                start_pos += 3
                varvalue = subc[start_pos:end_pos]
                varname = varvalue.split(':')[0]
                if varname not in variables:
                    variables[varname] = Variable(varvalue)
                founded_var[varname] = variables[varname]
    if return_founded_variables:
        return variables, founded_var
    else:
        return variables


def update_variables_in_text(text, variables, only_varvalue = False, return_var_used = False):
    convert_to_string = False
    if type(text) is not list:
        convert_to_string = True
        text = [text]

    result = []
    var_used = []
    for subc in text:
        for v_key in variables:
            this_var_not_used = True
            v = variables[v_key]

            varstart_pos = subc.find('<<<')
            while varstart_pos > -1:
                varend_pos = subc.find('>>>', varstart_pos)
                if subc[varstart_pos+3:varend_pos].split(':')[0] == v.varname:
                    if only_varvalue:
                        subc = subc[:varstart_pos] + str(v.varvalue) + subc[varend_pos+3:]
                        if this_var_not_used:
                            var_used.append(str(v.varvalue))
                            this_var_not_used = False
                    else:
                        subc = subc[:varstart_pos] + str(v) + subc[varend_pos+3:]
                        if this_var_not_used:
                            var_used.append(str(v))
                            this_var_not_used = False
                varstart_pos = subc.find('<<<', varstart_pos+3)
        result.append(subc)

    if convert_to_string:
        result =  result[0]
    if return_var_used:
        return result, var_used
    else:
        return result

def get_all_already_defined_variables():
    # find and read all dummy files.
    dummy_files = ['dvc/.dummy/' + f for f in os.listdir('dvc/.dummy') if f.find('.dummy') > -1]
    
    # search for all variables
    variables = {}
    for f in dummy_files:
        with open(f, 'r') as filepath:
            text = filepath.read()
        variables = find_all_variables([text], variables)
    return variables

def update_all_dummyfiles(variables_to_update):
    # find and read all dummy files.
    dummy_files = ['dvc/.dummy/' + f for f in os.listdir('dvc/.dummy') if f.find('.dummy') > -1]
    
    # search for all variables
    for f in dummy_files:
        with open(f, 'r') as filepath:
            text = filepath.read()
        text = update_variables_in_text(text,variables_to_update)
        with open(f, 'w') as filepath:
            print(text,file=filepath)

def test_the_variable_class():
    command = "<<<pre:i>>> <<<pre>>>Hallo meine liebe<<<r_or_not>>> <<<name:FI>>>, I have<<<not_or_not>>>asdsad asdsa asdsad<<<post>>> asd<<<first:ui>>>asdsad<<<second:fl>>>asdads <<<post2>>>".split(' ')

    variables = find_all_variables(command)

    for v in variables:
        print(variables[v].__pretty_str__())

    print()
    print(command)
    print()
    updated_command = update_variables_in_text(command, variables)
    print(updated_command)
    print()
    variables2 = find_all_variables(updated_command)
    updated_command2 = update_variables_in_text(updated_command, variables2)
    print(updated_command2)

