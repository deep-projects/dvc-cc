import sys
from git import Repo as GITRepo
from dvc_cc.hyperopt.variable import *
import subprocess
import uuid
import os
import numpy as np
from dvc_cc.bcolors import *
from pathlib import Path
from dvc_cc.run.jupyter_notebook_to_source import jupyter_notebook_to_source
DESCRIPTION = 'This command guesses the "dvc-cc hyperopt new" commands that might interest you. ' \
              'This is a simple implementation that you must review and correct.'

def search_for_files(command, preference = '-d'):
    command = command.split('#')[0].replace('"','\'').split('\'')

    if len(command) < 2:
        return None

    # is open function:
    if command[0].find(' open(') >= 2 or command[0].find('=open(') >= 1:
        founded_file = ''
        if len(command) >= 5:
            if len(command[3]) < 4 and (command[3].find('w') >= 0 or command[3].find('a') >= 0):
                if command[1].endswith('.yml') or command[1].endswith('.json'):
                    founded_file = '-m ' + command[1]
                else:
                    founded_file = '-o ' + command[1]
        if founded_file == '':
            return '-d ' + command[1]
        else:
            return founded_file
    elif command[0].find('ModelCheckpoint(') >= 0:
        # maybe a tf.keras.callbacks.ModelCheckpoint call?
        for i in range(1, len(command), 2):
            if command[i].endswith('.h5'):
                return '-o ' + command[i]

    elif command[0].find('TensorBoard(') >= 0:
        # maybe a tf.keras.callbacks.TensorBoard call?
        return '-o ' + command[1]

    for i in range(1,len(command),2):
        if command[i].endswith('.yml') or command[1].endswith('.json'):
            return '-m ' + command[1]

        elif command[i].endswith('.csv') or command[1].endswith('.h5') \
                or command[1].endswith('.txt') or command[1].endswith('.rtf')\
                or command[1].endswith('.bmp') or command[1].endswith('.jpg')\
                or command[1].endswith('.jpeg') or command[1].endswith('.gif')\
                or command[1].endswith('.html') or command[1].endswith('.mp3')\
                or command[1].endswith('.mpg') or command[1].endswith('.mpeg')\
                or command[1].endswith('.avi') or command[1].endswith('.wmf')\
                or command[1].endswith('.mov') or command[1].endswith('.ram')\
                or command[1].endswith('.tif') or command[1].endswith('.tiff')\
                or command[1].endswith('.dat') or command[1].endswith('.js')\
                or command[1].endswith('.mp4') or command[1].endswith('.tmp'):
            return preference + ' ' + command[1]

    return None

def search_for_argparse_parameter(command):
    if command.find('.add_argument(\'') > 0:

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
            p = p.strip()
            if p.startswith('type='):
                if p[5:].startswith('int'):
                    dtype = 'int'
                elif p[5:].startswith('float'):
                    dtype = 'float'

            if p.startswith('default='):
                p = p[8:]
                if p[0] == '\'':
                    p = p[1:p[1:].find('\'')]
                if p[-1] == ')':
                    p = p[:-1]
                print('dvc-cc hyperopt var --set ' + p + ' ' + shortname)


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
            if filename.endswith('.py') and dirpath.find('.ipynb_checkpoints') == -1:
                with open(str(Path(path))) as f:
                    content = [tmpf.replace('"',"'") for tmpf in f.readlines()]
            elif filename.endswith('.ipynb') and dirpath.find('.ipynb_checkpoints') == -1:
                path = path[:-6] + '.py'
                content = jupyter_notebook_to_source(dirpath,filename).replace('"',"'").split('\n')

            # this variable is used to save lines, if a command goes over several lines.
            saved_lines = ''

            file_contains_argparser = False
            params = []
            outputs = []

            # for each line
            for i in range(len(content)):
                line = content[i]
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

                    if i  < 0.6 * len(content):
                        output = search_for_files(line,preference='-d')
                    else:
                        output = search_for_files(line,preference='-o')
                    if output is not None:
                        outputs.append(output)

            if file_contains_argparser:
                #params = list(np.unique(params))
                indexes = np.unique(params, return_index=True)[1]
                params = [params[index] for index in sorted(indexes)]

                #outputs = list(np.unique(outputs))
                indexes = np.unique(outputs, return_index=True)[1]
                outputs = [outputs[index] for index in sorted(indexes)]


                if filename.endswith('.py'):
                    filename = filename[:-3]+'.dvc'
                elif filename.endswith('.ipynb'):
                    filename = filename[:-6]+'.dvc'
                print('dvc-cc hyperopt new -d ' + path[2:] + ' \\')
                for output in outputs:
                    print('                    '+output+' \\')
                print('                    -f '+filename+' \\')
                print('                    \'python '+path[2:]+' '+' '.join(params)+'\'')
                print()
    print()
    print(bcolors.HEADER+'This is a simple implementation that you must review and correct.'+bcolors.ENDC)