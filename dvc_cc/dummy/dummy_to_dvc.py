#!/usr/bin/env python3

import os
from dvc_cc.dummy.class_variable import Variable

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class HyperparameterBase:
    is_global = False
    allowed_types = []
    num_of_draws = 1
    variable = None
    name = None
    shortname = None

    def show(self,):
        return
    def draw(self,):
        return None
    def set_settings(self,):
        return
    def help(self,):
        return ''

class HyperparameterRandomSearch(HyperparameterBase):
    value = None
    minimum_value = None
    maximum_value = None

    def __init__(is_global=False, randomtype=):
        if is_global == False:
            self.name = 'RandomSearch-Global'
            self.shortname = 'rs'
        else:
            self.name = 'RandomSearch-Local'
            self.shortname = 'rsl'
        self.is_global = is_global

    def show(self,):
        return
    def draw(self,):
        return self.value

    def set_settings(self,):

        try:
            self.minimum_value = float(input('\t\tMin-Value (if pass, no value is set): '))
        except:
            self.minimum_value = None

        try:
            self.maximum_value = float(input('\t\tMax-Value (if pass, no value is set): '))
        except:
            self.maximum_value = None
        
        if self.is_global == False:
            self.num_of_draws = int(input('\t\tHow many draws do you want to make?: '))
        else:
            self.num_of_draws = None

        return

class HyperparameterRandomSearchLocal(HyperparameterBase):
    value = None
    def show(self,):
        return
    def draw(self,):
        return self.value
    def set_settings(self,):
        #input()
        return

class HyperparameterManually(HyperparameterBase):
    def __init__(self):
        self.name = 'Manually'
        self.shortname = 'm'
        self.is_global = False

    def set_data(self,data):
        data = data.split(',')
        num_of_draws = len(data)
        self.value = data

    def show(self,):
        return
    def draw(self,):
        return self.value
    def set_settings(self,):
        return

def get_possible_hyperparameter(variabletype):
    return [HyperparameterManually()]


def select_hyperparameteroptimizer(user_input, possible_hyperparameter):
    if user_input.startswith('--'):
        for h in possible_hyperparameter:
            if h.shortname == user_input[2:].lower():
                return h
        return None
    else:
        m = HyperparameterManually()
        m.set_data(user_input)
        return m

def dummy_to_dvc():
    # get all variables:
    variables = Variable.get_all_already_defined_variables()

    if len(variables) > 0:
        print('Found variables in dummy file.')

    # loop over all variables and save the hyperparameterclass
    hyperparameterclass = []
    variable_with_default_values = []
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
            selected_hyper.variable = v
            selected_hyper.set_settings()
            hyperparameterclass.append(selected_hyper)
        else:
            variable_with_default_values.append(v)

    
    
    # find and read all dummy files.
    dummy_files = ['dvc/.dummy/' + f for f in os.listdir('dvc/.dummy') if f.find('.dummy') > -1]


















































