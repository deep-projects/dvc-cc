import sys
from git import Repo as GITRepo
from dvc_cc.hyperopt.variable import *
import subprocess
import uuid
import os
from dvc_cc.bcolors import *
from pathlib import Path

DESCRIPTION = 'This command guesses the "dvc-cc hyperopt new" commands that might interest you. ' \
              'This is a simple implementation that you must review and correct.'

def search_for_argparse_parameter(command):
    if command.find('.add_argument(\'') > 0:
        print(command)
        params = command.split('.add_argument(')[1].split(',')

        if params[0].startswith('\'--'): # optional parameter but only with long name
            shortname = params[0][3:-1]
            longname = params[0][1:-1]
        elif params[0].startswith('\'-'): # required parameter
            shortname = params[0][2:-1]
            longname = params[1][1:-1]
        else:
            shortname = params[0][1:-1]
            longname = ''
        dtype = ''
        for p in params[1:]:
            if p.startswith('type='):
                if p[5:] == 'int':
                    dtype = 'int'
                elif p[5:] == 'float':
                    dtype = 'float'
        var = '{{' + shortname
        if dtype != '':
            var = var + ':' + dtype
        var = var + '}}'
        if longname == '':
            return var
        else:
            return longname + ' ' + var
    else:
        None

def main():
    for (dirpath, dirnames, filenames) in os.walk('.'):
        for filename in filenames:
            content = []
            path = dirpath+'/'+filename
            if filename.endswith('.py'):
                with open(str(Path(path))) as f:
                    content = f.readlines()

            # this variable is used to save lines, if a command goes over several lines.
            saved_lines = ''

            file_contains_argparser = False
            params = []

            # for each line
            for line in content:
                splitted_line = line.split()

                if len(splitted_line) >= 2 and splitted_line[1] == 'argparse':
                    file_contains_argparser = True

                line = line.strip().split('#')[0]

                if len(saved_lines) > 0:
                    saved_lines = saved_lines + line
                    line = saved_lines

                if line.count('(') == line.count(')'):
                    saved_lines = ''
                    # the command is complete
                    param = search_for_argparse_parameter(line)
                    if param is not None:
                        params.append(param)

            if file_contains_argparser:
                print('dvc-cc hyperopt new -d ' + path[2:] + ' \\')
                print('                    -o ... \\')
                print('                    -m ... \\')
                print('                    -f '+filename[:-3]+'.dvc'+' \\')
                print('                    \'python '+path[2:]+' '+' '.join(params)+'\'')
                print()


