from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import os
import sys
import yaml
import requests
import keyring
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
from argparse import ArgumentParser
import datetime
from dvc_cc.hyperopt.variable import *
import subprocess
import uuid
from dvc_cc.bcolors import *

def get_main_git_directory_path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path


# TODO EDIT DESCRIPTION !!!
DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'


def main():
    #parser = ArgumentParser(description=DESCRIPTION)
    #parser.add_argument('command', help='The command that you would use in `dvc run --no exec ...`. Here everything for what the dots stand you can use in this command. Use <<<A_Variable>>> to create a hyperopt variable.', type=str)
    #args = parser.parse_args()

    # go to the main git directory.
    os.chdir(get_main_git_directory_path())

    if not os.path.exists('dvc'):
        os.mkdir('dvc')
    
    if not os.path.exists('dvc/.hyperopt'):
        os.mkdir('dvc/.hyperopt')



    # get all existent variables
    vc = VariableCache()
    hyperopt_files = [f for f in os.listdir('dvc/.hyperopt') if f.endswith('.hyperopt')]
    for f in hyperopt_files:
        vc.register_dvccc_file('dvc/.hyperopt/'+f)

    # create the dvc file
    found_user_filename = False
    command_start_in = 0
    for i in range(len(sys.argv)-1):
        if sys.argv[i] == '-f':
            found_user_filename = True
            sys.argv[i + 1]='dvc/'+sys.argv[i + 1].replace('/', '_')
            output_filename = sys.argv[i+1]


    if found_user_filename:
        subprocess.call(['dvc', 'run', '--no-exec'] + sys.argv[1:])
    else:
        output_filename = 'dvc/'+ str(uuid.uuid4())+'.dvc'
        subprocess.call(['dvc', 'run', '--no-exec', '-f', output_filename] + sys.argv[1:])

    new_hyperopt_filename = 'dvc/.hyperopt/'+output_filename[4:-4]+'.hyperopt'
    os.rename(output_filename, new_hyperopt_filename)

    try:
        vc.register_dvccc_file(new_hyperopt_filename)
    except KeyboardInterrupt as ki:
        # Delete the file if the user want to cancel the job
        os.remove(new_hyperopt_filename)
        raise ki
    vc.update_dvccc_files()

    subprocess.call(['git', 'add', 'dvc/.hyperopt/*'])
























