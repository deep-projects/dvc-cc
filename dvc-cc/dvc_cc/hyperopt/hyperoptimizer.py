import random
from dvc_cc.hyperopt.variable import *
import re
import numpy as np
from dvc_cc.bcolors import *
from pathlib import Path

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
            print(bcolors.FAIL+'\t'*order+'Wrong datatype: Your input must be from the datatype ' + str(typeofvalue) + '.'+bcolors.ENDC)
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
        self.a = read_value('Value A of the Beta-Distribution: ', float)
        self.b = read_value('Value B of the Beta-Distribution: ', float)
        
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
    allowed_types = ['float', 'int', 'file']

    def set_data(self,data, dtype_of_variable):
        data = str(data).replace(' ', '').split(',')
        self.num_of_draws = len(data)
        self.value = data
        if dtype_of_variable == 'int':
            [int(val) for val in self.value]
        elif dtype_of_variable == 'int':
            [float(val) for val in self.value]
        elif dtype_of_variable.startswith('['):
            dtype_of_variable = dtype_of_variable[1:-1].split(',')
            tmp = np.array([val in dtype_of_variable or (val.isdigit() and int(val) < len(dtype_of_variable)) for val in self.value])
            if len(tmp[tmp==False]) > 0:
                raise  ValueError('You need to set one of the following types: '+ str(self.value))
        if len(np.unique(self.value)) != len(self.value):
            raise ValueError('It is not allowed to use the same value twice: ' + str(self.value))

    def draw(self,):
        return self.value

    def set_settings(self,):
        self.set_data(input('Set one or comma seperated values: '))
        return

class One_Of(HyperOptimizerBase):
    name = 'one_of'
    shortname = 'o'
    allowed_types = ['one_of']
    v = None

    def set_data(self,inputdata, vartype):
        vartypes = vartype[1:-1].split(',')
        inputdata = str(inputdata).replace(' ', '').split(',')
        data = []
        for d in inputdata:
            if d in vartypes:
                data.append(d)
            elif d.isdigit():
                data.append(vartypes[int(d)])
            else:
                raise ValueError('The user data did not match any of the parameter.')

        self.num_of_draws = len(data)
        if self.num_of_draws == 0:
            raise ValueError('The user data did not match any of the parameter.')
        self.value = data

    def draw(self,):
        return self.value

    def set_settings(self,vartype):
        self.set_data(input('Set one or comma seperated values: '), vartype)
        return

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
                        f = str(Path(root + '/' + f))
                        if re.match(regex, f):
                            matched_files.append(f)

            if len(matched_files) == 0:
                print(bcolors.FAIL+'   Warning the regex does not match any file.'+bcolors.ENDC)
                regex = None
            else:
                print('Your regex match '+bcolors.OKGREEN+ str(len(matched_files)) + ' Files'+bcolors.ENDC+'. here are 5 random Examples: ')
                for s in range(5):
                    print('\t\t- ' + random.sample(matched_files, 1)[0])
                if not input('Do you want to use this regex? [y,n]: ').lower().startswith('y'):
                    regex = None
        self.num_of_draws = len(matched_files)
        self.matched_files = matched_files


def get_possible_hyperparameter(variabletype):
    if variabletype == 'file':
        return [RegexFileSearch]
    elif variabletype.startswith('[') and variabletype.endswith(']'):
        return []
    else:
        return [HyperOptimizerGridSearch, HyperOptimizerRandomSearchLocal, HyperOptimizerRandomSearchGlobal]



def select_hyperparameteroptimizer(user_input, possible_hyperparameter, dtype_of_variable):
    if user_input.startswith('--'):
        for h in possible_hyperparameter:
            if h.shortname == user_input[2:].lower():
                return h
        return None
    else:
        m = Constant()
        try:
            m.set_data(user_input, dtype_of_variable)
        except:
            return None
        return m


def combine_combinations(combinations, is_global):
    r = np.array([[0]])
    one_global_hyperopt_was_set=False

    for i in range(len(combinations)):
        shape = r.shape
        if not is_global[i] or not one_global_hyperopt_was_set:
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
        print()
        if v.varvalue is None:
            hyper = get_possible_hyperparameter(v.vartype)
            selected_hyper = None
            while selected_hyper is None:
                print('Specifie the variable ' + v.varname)
                print('\tSet one or multiple comma sebarated values directly.')
                if len(hyper) > 0:
                    print('\tOr do hyperoptimization with one of the following options:')
                    for h in hyper:
                        print('\t\t- ' + h.name + ' (with '+bcolors.OKGREEN+'--' + h.shortname + bcolors.ENDC +')')

                user_input = input('\t'+ str(v.varname) + ' (' + bcolors.OKGREEN+str(v.vartype) + bcolors.ENDC+'): ')

                if v.vartype.startswith('[') and v.vartype.endswith(']'):
                    try:
                        selected_hyper = One_Of()
                        selected_hyper.set_data(user_input, v.vartype)
                    except:
                        print(bcolors.FAIL+'\t\tError: Your input did not match one of the possible values.'+bcolors.ENDC)
                        print('\t\tPlease use one of the values ' + bcolors.OKGREEN+str(v.vartype) + bcolors.ENDC + ' or use an index.')
                        selected_hyper = None
                else:
                    selected_hyper = select_hyperparameteroptimizer(user_input, hyper, v.vartype)
                if selected_hyper is None:
                    print(bcolors.FAIL+'\t\tWarning: did not understand which Hyperoptimizer you want to use.'+bcolors.ENDC)
            if type(selected_hyper) is not Constant and type(selected_hyper) is not One_Of:
                selected_hyper = selected_hyper(v.vartype)
                selected_hyper.set_settings()


            if selected_hyper.is_global:
                if num_of_global_draws is None:
                    num_of_global_draws = read_value('\tHow many global draws do you want to make?: ', int)
                selected_hyper.num_of_draws = num_of_global_draws

            v.hyperoptimizer = selected_hyper

        else:
            c = Constant()
            c.set_data(v.varvalue, v.vartype)
            v.hyperoptimizer = c

    # create a product over all variants
    is_global = [v.hyperoptimizer.is_global for v in vc.list_of_all_variables]
    draws = [v.hyperoptimizer.draw() for v in vc.list_of_all_variables]

    return combine_combinations(draws, is_global)



































