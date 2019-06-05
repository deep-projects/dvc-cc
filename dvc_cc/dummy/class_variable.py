import numpy as np

class Variable:
    original_value = None
    varname = None
    vartype = None
    varvalue = None


    def __init__(self, original_value):
        self.original_value = original_value
        tmp = self.original_value.split(':')
        self.varname = tmp[0]
        if len(tmp) > 1:
            self.vartype = tmp[1]
        self.set_type_of_variable()
        if len(tmp) > 2:
            self.varvalue = self.set_constant_value(tmp[2])


    def set_constant_value(self, value):
        if self.varvalue != '' and self.varvalue != 'None':
            self.varvalue = None
        elif self.vartype == 'file':
            self.varvalue = str(value)
        elif self.vartype == 'ufloat':
            self.varvalue = np.cast[np.float](value)
            if self.varvalue < 0.0:
                raise ValueError('Only positive values are allowed for the datatype \'ufloat\'.')
        else:
            self.varvalue = np.cast[self.vartype](value)
       

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

    def find_all_variables(text):
        if type(text) is not list:
            text = [text]

        variables = []
        for subc in text:
            start_pos = 0
            while start_pos >= 0:
                start_pos = subc.find('<<<', start_pos)
                if start_pos is not -1:
                    end_pos = subc.find('>>>', start_pos)
                    start_pos += 3
                    variables.append(Variable(subc[start_pos:end_pos]))
                    
        return variables

    def update_variables_in_text(text, variables):
        convert_to_string = False
        if type(text) is not list:
            convert_to_string = True
            text = [text]

        result = []
        for subc in text:
            for v in variables:
                subc = subc.replace('<<<'+v.original_value+'>>>', str(v))
            result.append(subc)

        if convert_to_string:
            return result[0]
        else:
            return result
    

def test_the_variable_class():
    command = "<<<pre:i>>> <<<pre>>>Hallo meine liebe<<<r_or_not>>> <<<name:FI>>>, I have<<<not_or_not>>>asdsad asdsa asdsad<<<post>>> asd<<<first:ui>>>asdsad<<<second:fl>>>asdads <<<post2>>>".split(' ')

    variables = Variable.find_all_variables(command)

    for v in variables:
        print(v)

    print()
    print(command)
    print()
    updated_command = Variable.update_variables_in_text(command, variables)
    print(updated_command)
    print()
    variables2 = Variable.find_all_variables(updated_command)
    updated_command2 = Variable.update_variables_in_text(updated_command, variables2)
    print(updated_command2)

