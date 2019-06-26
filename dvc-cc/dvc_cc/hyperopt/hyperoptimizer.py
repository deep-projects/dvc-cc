import os
import itertools
import uuid
import random
from dvc_cc.hyperopt.variable import *
import re
import numpy as np

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class HyperOptimizerBase:
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

class HyperOptimizerGridSearch(HyperOptimizerBase):
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

class HyperOptimizerRandomSearch(HyperOptimizerBase):
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

class HyperOptimizerRandomSearchLocal(HyperOptimizerRandomSearch):
    name = 'RandomSearch-Local'
    shortname = 'rsl'
    is_global = False

    def __init__(self, dtype, seed=None):
        super().__init__(dtype, seed)
class HyperOptimizerRandomSearchGlobal(HyperOptimizerRandomSearch):
    name = 'RandomSearch-Global'
    shortname = 'rs'
    is_global = True

    def __init__(self, dtype, seed=None):
        super().__init__(dtype, seed)
    

class Constant(HyperOptimizerBase):
    name = 'Constant'
    shortname = 'c'
    allowed_types = ['float', 'ufloat', 'int', 'uint', 'file']

    def set_data(self,data):
        data = str(data).replace(' ', '').split(',')
        self.num_of_draws = len(data)
        self.value = data

    def draw(self,):
        return self.value

    def set_settings(self,):
        self.set_data(input('Set one or comma seperated values: '))
        return

    read_value

class RegexFileSearch(HyperOptimizerBase):
    name = 'FileSearch'
    shortname = 'fs'
    allowed_types = ['file']

    def __init__(self, dtype):
        super().__init__(dtype)

    def draw(self,):
        return self.matched_files

    def set_settings(self,):
        regex = None
        while regex is None:
            regex = input('Set regex value that describes the Files: ')

            matched_files = []
            for root, dirs, files in os.walk('', topdown=True):
                root = root[2:]

                for f in files:
                    if root == '':
                        if re.match(regex, f):
                            matched_files.append(f)
                    else:
                        f = root + '/' + f
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
        return [HyperOptimizerGridSearch, HyperOptimizerRandomSearchLocal, HyperOptimizerRandomSearchGlobal]



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



def combine_combinations(combinations, is_global):
    r = np.array([[0]])
    one_global_hyperopt_was_set=False

    for i in range(len(combinations)):
        shape = r.shape
        if not is_global[i] or not one_global_hyperopt_was_set:
            print(i)
            r = np.tile(r, len(combinations[i])).reshape(-1, shape[1])
            next_draw = np.tile(combinations[i], shape[0]).reshape(-1, 1)
            if is_global[i]:
                one_global_hyperopt_was_set = True
        else:
            next_draw = np.tile(combinations[i], shape[0]//len(combinations[i])).reshape(-1, 1)


        r = np.append(r, next_draw , axis=1)

    return r[:,1:]

def create_hyperopt_variables(vc): # vc == VariableCache

    num_of_global_draws = None

    for v in vc.list_of_all_variables:
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
            if type(selected_hyper) is not Constant:
                selected_hyper = selected_hyper(v.vartype)
                selected_hyper.set_settings()


            if selected_hyper.is_global:
                if num_of_global_draws is None:
                    num_of_global_draws = read_value('How many global draws do you want to make?: ', int)
                selected_hyper.num_of_draws = num_of_global_draws

            v.hyperoptimizer = selected_hyper

        else:
            c = Constant()
            c.set_data(v.varvalue)
            v.hyperoptimizer = c

            #TODO: USING GLOBAL RANDOM SEARCH !!!
    # create a product over all variants
    is_global = [v.hyperoptimizer.is_global for v in vc.list_of_all_variables]
    draws = [v.hyperoptimizer.draw() for v in vc.list_of_all_variables]

    return combine_combinations(draws, is_global)



































