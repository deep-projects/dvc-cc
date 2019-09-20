import re
from dvc_cc.bcolors import *
from pathlib import Path

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

            if name_of_type is None or name_of_type == '' or name_of_type.lower() == 'none':
                name_of_type = input('What type of variable is \''+str(self.varname)+'\'? (int, float, file, one_of): ')

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
                        print('\tPlease set all allowed values for the variable ' + self.varname)
                        last_input = input('\t\tAllowed Values: ')
                        if last_input == '':
                            print(bcolors.FAIL+'\t\t\   Error: You need to set a value!'+bcolors.ENDC)
                            last_input = None
                        else:
                            self.vartype = self.vartype + last_input
                    else:
                        last_input = input('\t\tAllowed Values (Enter for closing): ')
                        if last_input != '':
                            self.vartype = self.vartype + ',' + last_input
                self.vartype = self.vartype + ']'
            # it is one_of with the values already set.
            elif name_of_type.startswith('[') and name_of_type.endswith(']'):
                self.vartype = name_of_type
            else:
                print(bcolors.FAIL+'\tError: Did not understand the datatype you want to set.'+bcolors.ENDC)
                self.vartype = None
                name_of_type = None
        self.varvalue = None


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
            raise ValueError('You used this function wrong. The first parameter must be a list!')

    def search_varname_in_list_return_index(list_of_variables, varname_to_check):
        if type(list_of_variables) == list:
            for i in range(len(list_of_variables)):
                if list_of_variables[i].varname == varname_to_check:
                    return i
            return None
        else:
            raise ValueError('You used this function wrong. The first parameter must be a list!')

    def search_var_in_list(list_of_variables, var_to_check):
        if type(list_of_variables) == list:
            for v in list_of_variables:
                if v.varname == var_to_check.varname:
                    return v
            return var_to_check
        else:
            raise ValueError('You used this function wrong. The first parameter must be a list!')
    def search_varname_in_dict(list_of_variables, varname_to_check):
        if type(list_of_variables) == dict:
            if varname_to_check in list_of_variables:
                return list_of_variables[varname_to_check]
            else:
                return None
        else:
            raise ValueError('You used this function wrong. The first parameter must be a dict!')
    def search_var_in_dict(list_of_variables, var_to_check):
        if type(list_of_variables) == dict:
            if var_to_check.varname in list_of_variables:
                return list_of_variables[var_to_check.varname]
            else:
                return var_to_check
        else:
            raise ValueError('You used this function wrong. The first parameter must be a dict!')

    def __pretty_str__(self):
        tmp = str(self)[2:-2].split(':')
        return '%25s%8s%6s'%(tmp[0],tmp[1],tmp[2])

    def __str__(self):
        return '{{' + self.varname+':'+ self.vartype + ':'+ str(self.varvalue) + '}}'


class VariableCache:
    """
    This class saves the relation between the hyperopt files and the variables in the files.
    """

    list_of_all_variables = []
    filename_dict = {} # saves all variables related to the files
    varname_dict = {} # saves all related files

    def register_dvccc_file(self, name_of_textfile):
        """

        :param name_of_textfile:
        :return:
        """
        with open(str(Path(name_of_textfile)),'r') as f:
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
                varname, _, _ = Variable.split_original_string(varvalue)
                #v = Variable(varvalue)
                r = Variable.search_varname_in_list(self.list_of_all_variables, varname)
                if r is None:
                    v = Variable(varvalue)
                    self.list_of_all_variables.append(v)
                    self.varname_dict[v.varname] = [name_of_textfile]
                else:
                    v = r
                    self.varname_dict[r.varname].append(name_of_textfile)

                if v.varname not in self.filename_dict[name_of_textfile]:
                    self.filename_dict[name_of_textfile].append(v.varname)


    def update_dvccc_files(self):
        """

        :return:
        """
        for filename in self.filename_dict:
            with open(str(Path(filename)), 'r') as f:
                content = f.read()

            start_pos = 0
            while start_pos >= 0:
                start_pos = content.find('{{', start_pos)
                if start_pos is not -1:
                    end_pos = content.find('}}', start_pos)
                    varvalue = content[start_pos+2:end_pos]

                    varname,_,_ = Variable.split_original_string(varvalue)
                    v = Variable.search_varname_in_list(self.list_of_all_variables, varname)
                    content = content[:start_pos] + str(v) + content[end_pos+2:]
                    start_pos += 2
            with open(str(Path(filename)), 'w') as f:
                print(content, file=f)



    def set_values_for_hyperopt_files(self, values_to_set):
        """

        :return:
        """
        for filename in self.filename_dict:
            with open(str(Path(filename)), 'r') as f:
                content = f.read()

            start_pos = 0
            while start_pos >= 0:
                start_pos = content.find('{{', start_pos)
                if start_pos is not -1:
                    end_pos = content.find('}}', start_pos)
                    varvalue = content[start_pos+2:end_pos]

                    varname,_,_ = Variable.split_original_string(varvalue)
                    index = Variable.search_varname_in_list_return_index(self.list_of_all_variables, varname)
                    if self.list_of_all_variables[index].vartype == 'int':
                        #TODO: Find better solution for str(int(float(...)))
                        content = content[:start_pos] + str(int(float(values_to_set[index]))) + content[end_pos+2:]
                    else:
                        content = content[:start_pos] + str(values_to_set[index]) + content[end_pos+2:]
                    start_pos += 2

            with open(str(Path('dvc/'+filename[14:-9]+'.dvc')), 'w') as f:
                print(content, file=f)

