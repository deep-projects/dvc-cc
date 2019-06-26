from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import os
import yaml
import requests
import keyring
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
from argparse import ArgumentParser
import datetime
from dvc_cc.hyperopt.class_variable import *
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_main_git_directory_path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path


DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('name_of_variable', help='The name of variable to show. Use "all" to show all variables. If you use "all" --set and --set-type has no effect.', type=str)
    parser.add_argument('--set', help='Set a constant value for one parameter. If a constant value is set, it will not be queried when running "dvc-cc run". Use "None" to undo the constant value.', type=str, default=None)
    parser.add_argument('--set-type', help='If you want to reset the type of the variable you can use this parameter. This should be one of the following: float, ufloat, int, uint or file.', type=str, default=None)
    args = parser.parse_args()

    # go to the main git directory.
    os.chdir(get_main_git_directory_path())

    if not os.path.exists('dvc'):
        os.mkdir('dvc')

    if not os.path.exists('dvc/.hyperopt'):
        os.mkdir('dvc/.hyperopt')

    ######################
    # Read all Variables #
    ######################
    vc = VariableCache()
    if os.path.exists('dvc') and os.path.exists('dvc/.hyperopt'):
        list_of_hyperopt_files = [f for f in os.listdir('dvc/.hyperopt') if f.endswith('.hyperopt')]
        for f in list_of_hyperopt_files:
            os.rename('dvc/.hyperopt/' + f, 'dvc/'+f[:-9]+'.dvc')
    else:
        list_of_hyperopt_files = []
    for f in list_of_hyperopt_files:
        f = 'dvc/.hyperopt/' + f
        vc.register_dvccc_file(f)

    if args.name_of_variable.upper() == 'ALL':
        print('%25s%8s%6s'%('Varname','type','value'))
        for v in vc.list_of_all_variables:
            print(v.__pretty_str__())
    else:
        v = Variable.search_varname_in_list(vc.list_of_all_variables, args.name_of_variable.upper())
        if v is not None:
            if args.set_type is not None:
                v.set_type_of_variable(args.set_type)
            if args.set is not None:
                v.set_constant_value(args.set)
            if args.set_type is not None or args.set is not None:
                vc.update_dvccc_files()
            print(v.__pretty_str__())

        else:
            print('Did not found the Variable: ' + str(args.name_of_variable))
            print("This variable "+str(args.name_of_variable)+" does not exist. The following Variables exists: ")
            print('%25s%8s%6s'%('Varname','type','value'))
            for v in vc.list_of_all_variables:
                print(v.__pretty_str__())
            exit(1)


















