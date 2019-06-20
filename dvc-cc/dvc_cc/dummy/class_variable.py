import numpy as np
import os
import re

class Variable:

    original_string = None
    varname = None
    vartype = None
    varvalue = None

    def __init__(self, original_string):
        self.original_string = original_string
        self.varname, vartype, varvalue = Variable.split_original_string(self.original_string)

        self.set_type_of_variable(vartype)
        self.set_constant_value(varvalue)

    def split_original_string(original_string):
        tmp = original_string.split(':')
        varname = re.sub(r"[^A-Za-z0-9_]+", '', tmp[0])
        if len(tmp) == 1:
            return [varname, None, None]
        elif  len(tmp) == 2:
            return [varname, tmp[1], None]
        else:
            return [varname, tmp[1], tmp[2]]


    def set_type_of_variable(self, name_of_type=None):
        '''
        Set a type for the variable. If the parameter type is not valid or is None than the user will get asked to set the parameter.
        :param name_of_type: string of the datatype.
        :return:
        '''
        self.vartype = None
        while self.vartype is None:

            if name_of_type is None or name_of_type != '' or name_of_type != 'None':
                name_of_type = input('What type of variable is the \''+self.varname+'\'? (int, float, file, one_of): ')

            name_of_type = name_of_type.lower()


            if name_of_type.startswith('i'):
                self.vartype = 'int'
            elif name_of_type.startswith('d') or name_of_type.startswith('fl'):
                self.vartype = 'float'
            elif name_of_type.startswith('fi'):
                self.vartype = 'file'
            elif name_of_type.startswith('o'):
                last_input = None
                self.vartype = '['
                while last_input != '':
                    if last_input == None:
                        last_input = input('Allowed Values: ')
                        if last_input == '':
                            print('Error: You need to set a value!')
                            last_input = None
                        else:
                            self.vartype = self.vartype + last_input
                    else:
                        last_input = input('Allowed Values (Enter for closing): ')
                        if last_input != '':
                            self.vartype = self.vartype + ',' + last_input
                self.vartype = ']'
            else:
                print('Warning: Did not understand the datatype.')
                self.vartype = None


    def set_constant_value(self, value):
        self.varvalue = None
        if value == None or value == '' or value.lower() == 'none':
            self.varvalue = None
        elif self.vartype == 'int':
            self.varvalue = int(value)
        elif self.vartype == 'float':
            self.varvalue = float(value)
        elif self.vartype == 'file':
            self.varvalue = str(value)
        else: # it is "one_of"
            possible_values = self.vartype[1:-1].split(',')
            for pv in possible_values:
                if pv == str(value):
                    self.varvalue = str(value)
            if self.varvalue == None:
                raise ValueError('The value ' + str(value) + ' is not in the list of allowed values ' + str(possible_values) + '.')


    def search_varname_in_list(list_of_variables, varname_to_check):
        if type(list_of_variables) == list:
            for v in list_of_variables:
                if v.varname == varname_to_check:
                    return v
            return None
        else:
            raise ValueError('ERROR: You used this function false. The first parameter must be a list!')
    def search_var_in_list(list_of_variables, var_to_check):
        if type(list_of_variables) == list:
            for v in list_of_variables:
                if v.varname == var_to_check.varname:
                    return v
            return var_to_check
        else:
            raise ValueError('ERROR: You used this function false. The first parameter must be a list!')
    def search_varname_in_dict(list_of_variables, varname_to_check):
        if type(list_of_variables) == dict:
            if varname_to_check in list_of_variables:
                return list_of_variables[varname_to_check]
            else:
                return None
        else:
            raise ValueError('ERROR: You used this function false. The first parameter must be a dict!')
    def search_var_in_dict(list_of_variables, var_to_check):
        if type(list_of_variables) == dict:
            if var_to_check.varname in list_of_variables:
                return list_of_variables[var_to_check.varname]
            else:
                return var_to_check
        else:
            raise ValueError('ERROR: You used this function false. The first parameter must be a dict!')

    def __pretty_str__(self):
        tmp = str(self)[2:-2].split(':')
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
    
        return '{{' + self.varname+':'+ vartype +':'+ str(self.varvalue) + '}}'


class VariableAndTextFileCorrelation:
    list_of_all_variables = []
    filename_dict = {} # saves all variables related to the files
    varname_dict = {} # saves all related files

    def register_dvccc_file(self, name_of_textfile):
        """

        :param name_of_textfile:
        :return:
        """
        with open(name_of_textfile, 'r') as f:
            content = f.read()

        if name_of_textfile not in self.filename_dict:
            self.filename_dict[name_of_textfile] = []

        start_pos = 0
        while start_pos >= 0:
            start_pos = content.find('{{', start_pos)
            if start_pos is not -1:
                end_pos = content.find('}}', start_pos)
                start_pos += 2
                varvalue = content[start_pos:end_pos]
                v = Variable(varvalue)
                r = Variable.search_varname_in_list(self.list_of_all_variables, v.varname)
                if r is None:
                    self.list_of_all_variables.append(v)
                    self.varname_dict[v.varname] = [name_of_textfile]
                else:
                    v = r
                    self.varname_dict[v.varname].append(name_of_textfile)

                if v.varname not in self.filename_dict[name_of_textfile]:
                    self.filename_dict[name_of_textfile].append(v.varname)

    def update_dvccc_files(self):
        """

        :return:
        """
        for f in self.filename_dict:
            #TODO: DO SOMETHING!!!
            print('Hallo Welt')



def find_all_variables(list_of_text, variables = {}):
    if type(list_of_text) is not list:
        list_of_text = [list_of_text]

    founded_var = {}
    for subc in list_of_text:
        start_pos = 0
        while start_pos >= 0:
            start_pos = subc.find('{{', start_pos)
            if start_pos is not -1:
                end_pos = subc.find('}}', start_pos)
                start_pos += 2
                varvalue = subc[start_pos:end_pos]
                varname = Variable.split_original_string(varvalue)[0]

                if varname not in variables:
                    variables[varname] = Variable(varvalue)

                founded_var[varname] = variables[varname]

    return variables, founded_var


def update_variables_in_text(list_of_text, variables):
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

            varstart_pos = subc.find('{{')
            while varstart_pos > -1:
                varend_pos = subc.find('}}', varstart_pos)
                if subc[varstart_pos+2:varend_pos].split(':')[0] == v.varname:
                    if only_varvalue:
                        subc = subc[:varstart_pos] + str(v.varvalue) + subc[varend_pos+2:]
                        if this_var_not_used:
                            var_used.append(str(v.varvalue))
                            this_var_not_used = False
                    else:
                        subc = subc[:varstart_pos] + str(v) + subc[varend_pos+2:]
                        if this_var_not_used:
                            var_used.append(str(v))
                            this_var_not_used = False
                varstart_pos = subc.find('{{', varstart_pos+2)
        result.append(subc)

    if convert_to_string:
        result =  result[0]
    if return_var_used:
        return result, var_used
    else:
        return result

def get_all_already_defined_variables():
    # find and read all dummy files.
    if os.path.exists('dvc/.dummy'):
        dummy_files = ['dvc/.dummy/' + f for f in os.listdir('dvc/.dummy') if f.find('.dummy') > -1]
    else:
        dummy_files = []
    
    # search for all variables
    variables = {}
    for f in dummy_files:
        with open(f, 'r') as filepath:
            text = filepath.read()
        variables = find_all_variables([text], variables)
    return variables

def update_all_dummyfiles(variables_to_update):
    # find and read all dummy files.
    if os.path.exists('dvc/.dummy'):
        dummy_files = ['dvc/.dummy/' + f for f in os.listdir('dvc/.dummy') if f.find('.dummy') > -1]
    else:
        dummy_files = []
    
    # search for all variables
    for f in dummy_files:
        with open(f, 'r') as filepath:
            text = filepath.read()
        text = update_variables_in_text(text,variables_to_update)
        with open(f, 'w') as filepath:
            print(text,file=filepath)

def test_the_variable_class():
    command = "{{pre:i}} {{pre}}Hallo meine liebe{{r_or_not}} {{name:FI}}, I have{{not_or_not}}asdsad asdsa asdsad{{post}} asd{{first:ui}}asdsad{{second:fl}}asdads {{post2}}".split(' ')

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

