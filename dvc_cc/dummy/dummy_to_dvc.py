import os
import itertools
import uuid
import random
from dvc_cc.dummy.class_variable import * 
import re
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class VariableOptimizerBase:
    is_global = False
    allowed_types = []
    num_of_draws = 1
    variable = None
    name = None
    shortname = None

    def draw(self,):
        return None
    def set_settings(self,):
        return
    def help(self,):
        return ''

def read_value(text,typeofvalue, order=2):
    user_input = None
    while user_input == None:
        try:
            user_input = typeofvalue(input('\t'*order+text))
        except ValueError:
            print('\t'*order+'Wrong datatype: Your input must be the dataype ' + str(typeofvalue) + '.')
            user_input = None
    return user_input

class VariableOptimizerGridSearch(VariableOptimizerBase):
    value = None
    minimum_value = None
    maximum_value = None
    allowed_types = ['float', 'ufloat', 'int', 'uint']      
    name = 'GridSearch'
    shortname = 'gs'
    is_global = False 
 
    def __init__(self, dtype, seed=None):
        self.dtype = dtype
        self.seed = seed

    def draw(self,):
        if self.dtype == 'int' or self.dtype == 'uint' or self.dtype == np.int or self.dtype == np.uint:
            return np.linspace(self.minimum_value,self.maximum_value,self.num_of_draws,dtype=int)
        else:
            return np.linspace(self.minimum_value,self.maximum_value,self.num_of_draws)

    def set_settings(self,):
        self.minimum_value = read_value('Min value: ', float)
        self.maximum_value = read_value('Max value: ', float)
        self.num_of_draws = read_value('Num of draws: ', int)

class VariableOptimizerRandomSearch(VariableOptimizerBase):
    value = None
    minimum_value = None
    maximum_value = None
    allowed_types = ['float', 'ufloat', 'int', 'uint']

    def __init__(self,dtype, seed=None):
        self.dtype = dtype
        self.seed = seed

    def draw(self,num_of_draws=None):
        if num_of_draws is not None:
            self.num_of_draws = num_of_draws
        if self.num_of_draws is None:
            r = np.random.beta(self.a,self.b)
        else:
            r = np.random.beta(self.a,self.b,self.num_of_draws)
        if self.dtype == 'int' or self.dtype == 'uint' or self.dtype == np.int or self.dtype == np.uint:
            r *= self.maximum_value - self.minimum_value + 1
        else:
            r *= self.maximum_value - self.minimum_value
        r += self.minimum_value
        if self.dtype == 'int' or self.dtype == 'uint' or self.dtype == np.int or self.dtype == np.uint:
            r = np.array(r,dtype=np.int)
        return r

    def set_settings(self,):
        self.minimum_value = read_value('Min value: ', float)
        self.maximum_value = read_value('Max value: ', float)
        self.a = read_value('A value of Beta-Distribution: ', float)
        self.b = read_value('B value of Beta-Distribution: ', float)
        
        if self.is_global == False:
            self.num_of_draws = read_value('How many draws do you want to make?: ', int)
        else:
            self.num_of_draws = None
        return

class VariableOptimizerRandomSearchLocal(VariableOptimizerRandomSearch):
    name = 'RandomSearch-Local'
    shortname = 'rsl'
    is_global = False

    def __init__(self, dtype, seed=None):
        super().__init__(dtype, seed)
class VariableOptimizerRandomSearchGlobal(VariableOptimizerRandomSearch):
    name = 'RandomSearch-Global'
    shortname = 'rs'
    is_global = True

    def __init__(self, dtype, seed=None):
        super().__init__(dtype, seed)
    

class Constant(VariableOptimizerBase):
    name = 'Constant'
    shortname = 'c'
    allowed_types = ['float', 'ufloat', 'int', 'uint', 'file']

    def set_data(self,data):
        data = data.split(',')
        self.num_of_draws = len(data)
        self.value = data

    def draw(self,):
        return self.value

    def set_settings(self,):
        self.set_data(input('Set one or comma seperated values: '))
        return

    read_value

class RegexFileSearch(VariableOptimizerBase):
    name = 'FileSearch'
    shortname = 'fs'
    allowed_types = ['file']

    def __init__(self, root_dir):
        self.root_dir = root_dir

    def draw(self,):
        return self.matched_files

    def set_settings(self,):
        regex = None
        while regex is None:
            regex = input('Set regex value that describes the Files: ')

            matched_files = []
            for root, dirs, files in os.walk(self.root_dir, topdown=True):
                root = self.root_dir[len(self.root_dir):]

                for f in files:
                    if root == '':
                        if re.match(regex, f):
                            matched_files.append(f)
                    else:
                        f = root[len(self.root_dir):] + '/' + f
                        if re.match(regex, f):
                            matched_files.append(f)
            if len(matched_files) == 0:
                print('   Warning the regex does not match any file.')
                regex = None
            else:
                print('Your regex match '+ str(len(matched_files)) + ' Files. 5 Examples: ')
                for s in range(5):
                    print('\t\t- ' + random.sample(matched_files, 1)[0])
                if input('Do you want use another regex? (yes,no): ').lower().startswith('y'):
                    regex = None
        self.num_of_draws = len(matched_files)
        self.matched_files = matched_files

    read_value

def get_possible_hyperparameter(variabletype):
    if variabletype == 'file':
        return [RegexFileSearch]
    else:
        return [VariableOptimizerGridSearch, VariableOptimizerRandomSearchLocal, VariableOptimizerRandomSearchGlobal]



def select_hyperparameteroptimizer(user_input, possible_hyperparameter):
    if user_input.startswith('--'):
        for h in possible_hyperparameter:
            if h.shortname == user_input[2:].lower():
                return h
        return None
    else:
        m = Constant()
        m.set_data(user_input)
        return m

def dummy_to_dvc(current_path):
    # get all variables:
    variables = get_all_already_defined_variables()

    if len(variables) > 0:
        print('Found variables in dummy file.')

    # loop over all variables and save the hyperparameterclass
    hyperparameterclass = []

    num_of_global_draws = None

    for key in variables:
        v = variables[key]
        if v.varvalue is None:
            hyper = get_possible_hyperparameter(v.vartype)
            selected_hyper = None
            while selected_hyper is None:
                print('Specifie the variable ' + v.varname)
                print('\tYou can set one or multiple comma sebarated values directly.')
                print('\tOr do hyperoptimization with one of the following options:')
                for h in hyper:
                    print('\t\t- ' + h.name + ' (with --' + h.shortname + ')')

                user_input = input('\t'+ v.varname + ': ')

                selected_hyper = select_hyperparameteroptimizer(user_input, hyper)
                if selected_hyper is None:
                    print('Warning: did not understand which Hyperoptimizer you want to use.')
            if selected_hyper is RegexFileSearch:
                selected_hyper = selected_hyper(current_path)
                selected_hyper.set_settings()
            elif type(selected_hyper) is not Constant:
                selected_hyper = selected_hyper(v.vartype)
                selected_hyper.set_settings()
            selected_hyper.variable = v
            if selected_hyper.is_global:
                if num_of_global_draws is None:
                    num_of_global_draws = read_value('How many global draws do you want to make?: ', int)
                selected_hyper.num_of_draws = num_of_global_draws
            hyperparameterclass.append(selected_hyper)
        else:
            m = Constant()
            m.variable = v
            m.set_data(v.varvalue)
            hyperparameterclass.append(m)

    # create a product over all variants
    all_variants = [list(v.draw()) for v in hyperparameterclass]
    all_variants = list(itertools.product(*all_variants))

    # find and read all dummy files.
    if os.path.exists('dvc/.dummy'):
        dummy_files = ['dvc/.dummy/' + f for f in os.listdir('dvc/.dummy') if f.find('.dummy') > -1]
    else:
        dummy_files = []

    variables = {h.variable.varname: h.variable for h in hyperparameterclass}

    created_dvc_files = []

    for variant in all_variants:
        for v_i in range(len(variables)):
            variables[list(variables.keys())[v_i]].varvalue = variant[v_i]
        for f in dummy_files:
            with open(f,"r") as file_to_read:
                txt = file_to_read.read()
            txt , used_varval = update_variables_in_text(txt, variables, only_varvalue = True, return_var_used=True)
            used_varval = '_'.join(used_varval)
            dest = 'dvc/'+f[11:f[11:].find('.dummy')+11-4]+'_'+used_varval+'.dvc'
            if not os.path.exists(dest):
                created_dvc_files.append(dest)
                with open(dest,"w") as dest_file:
                    print(txt, file=dest_file)

    return created_dvc_files






































