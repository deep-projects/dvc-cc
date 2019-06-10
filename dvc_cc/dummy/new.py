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
from dvc_cc.dummy.class_variable import *
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
    parser.add_argument('command', help='The command that you would use in `dvc run --no exec ...`. Here everything for what the dots stand you can use in this command. Use <<<A_Variable>>> to create a dummy variable.', type=str)
    args = parser.parse_args()

    # go to the main git directory.
    os.chdir(get_main_git_directory_path())

    if not os.path.exists('dvc'):
        os.mkdir('dvc')
    
    if not os.path.exists('dvc/.dummy'):
        os.mkdir('dvc/.dummy')
    
    # get all existent variables
    variables = get_all_already_defined_variables()

    # search for parameters
    args.command = args.command.split(' ')
    variables, founded_vars = find_all_variables(args.command, variables,return_founded_variables=True)
    args.command = update_variables_in_text(args.command, variables)

    # search for -f option!
    filename = None
    filename_pos = -1
    outputnames = []
    for i in range(len(args.command)):
        if args.command[i] == '-f':
            filename_pos = i+1
            filename = args.command[filename_pos]
        if args.command[i] == '-o' or args.command[i] == '-O' or args.command[i] == '-m' or args.command[i] == '-M':
            outputnames.append(args.command[i + 1])
            var = find_all_variables(args.command[i + 1])
            for v in founded_vars:
                if v not in var:
                    print('ERROR: You need to define all parameters to all output and metric files!')
                    print('       '+str(v)+' was not found in ' + args.command[i + 1])
                    exit(1)

    firstoutputname = outputnames[0]

    # remove variable names in firstoutputname
    variable_start = firstoutputname.find('<<<')
    while variable_start >= 0:
        variable_end = firstoutputname.find('>>>')
        if firstoutputname[variable_start - 1] == '_':
            variable_start = variable_start - 1
        firstoutputname = firstoutputname[:variable_start] + firstoutputname[variable_end+3:]
        variable_start = firstoutputname.find('<<<')

    # make sure that the filename is in the dvc folder
    if filename is None:
        filename = firstoutputname + '.dvc'
    filename = filename.split('/')[-1]

    if filename_pos == -1:
        args.command = ['-f', 'dvc/'+filename] + args.command
    else:
        args.command[filename_pos] = 'dvc/'+filename

    # TODO: maybe it is possible to combine this and the next blog.
    # if no variable is found, than ask user to save this just as dvc file.
    if len(variables) == 0:
        if input('Warning: No variable was found. Do you want to save this as standart dvc-file instead of a dummy file? (y/n)').lower().startswith('y'):
            command = ['dvc','run','--no-exec'] + args.command
            print('run command: "'+' '.join(command) + '"')
            subprocess.call(command)
            exit(0)
        else:
            print('Hint: You can define variables with <<<some_name_of_your_variable>>>.')
            exit(1)


    # create the dvc file.
    command = ['dvc','run','--no-exec'] + args.command
    print('run command: "'+' '.join(command) + '"')
    subprocess.call(command)

    # move the dvc file to dvc/.dummy/....dvc.dummy
    index = ''
    while os.path.exists('dvc/.dummy/'+filename+'.dummy'+index):
        if index == '':
            index = '.2'
        else:
            index = int(index[1:]) + 1
            index = '.' + str(index)
    os.rename('dvc/'+filename,'dvc/.dummy/'+filename+'.dummy'+index)


    subprocess.call(['git', 'add', 'dvc/.dummy/'+filename+'.dummy'+index])
























