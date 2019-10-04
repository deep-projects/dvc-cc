#!/usr/bin/env python3

import os
from argparse import ArgumentParser
import re
import random
import dvc
from dvc.repo import Repo as DVCRepo
from git import Git
import subprocess
import time
import numpy as np
import getpass
from pathlib import Path

DESCRIPTION = 'This script gives you the possibility to get all output files that match some regex over different branches and saves them in a tmp folder.'

def create_output_dir(root_dir, path_to_output = None):
    """ This function creates the output dir to save the data.
    Args:
        root_dir (str): The root dir of the project. This could be repo.root_dir and this is the part where the .gitignore will be wroten to.
        path_to_output (str): default=None

    Returns:
        str: The foldername that was created. If no folder could be created, it will return None
    """
    if path_to_output is None:
        path_to_output = 'tmp_' + str(random.getrandbits(32))
    else:
        path_to_output = 'tmp_' + path_to_output + '_' + str(random.getrandbits(32))
    if os.path.exists(str(Path(path_to_output))):
        print('Error the path '+ path_to_output +' already exists. First remove this folder.')
        return None

    # Create folder and write them to .gitignore
    os.mkdir(path_to_output)
    f= open(str(Path(os.path.join(root_dir, '.gitignore'))),"a+")
    f.write('\n'+path_to_output)
    f.close()
    subprocess.call(['git', 'add', '.gitignore'])
    subprocess.call(['git', 'commit','-m','update .gitignore'])
    subprocess.call(['git', 'push'])
    print('Create folder ' + path_to_output + ' and wrote this to .gitignore')
    return path_to_output

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('path_to_output',
                        help='The path to the output/metric file or folder that you want get.', type=str)
    parser.add_argument('-p', '--list-of-pos',
                        help='A list of dvc-cc indizes that you want include in the display. You can also use slicing for example: 12:15:2 to use 12, 14.',
                        nargs="+", type=str)
    args = parser.parse_args()

    repo = DVCRepo()
    g = Git()
    starting_branch = g.branch().split('*')[1].split('\n')[0][1:]

    # Set the password only once!
    remote_name = repo.config.config['core']['remote']
    remote_settings = repo.config.config['remote "' + remote_name + '"']
    if 'ask_password' in remote_settings and remote_settings['ask_password']:
        remote_settings['password'] = getpass.getpass('Password for ' + remote_settings['url'] + ': ')
        remote_settings['ask_password'] = False

    outputdir = create_output_dir(repo.root_dir, args.path_to_output)
    if outputdir is None:
        exit(1)

    list_of_allowed_dvccc_ids = None

    if args.list_of_pos is not None:

        list_of_allowed_dvccc_ids = []
        for pos in args.list_of_pos:
            try:
                if pos.find(':') > -1:
                    pos = np.array(pos.split(':'), dtype=int)
                    list_of_allowed_dvccc_ids.extend(np.arange(*pos))
                else:
                    pos = int(pos)
                    if pos >= 0:
                        list_of_allowed_dvccc_ids.append(pos)
                    else:
                        raise ValueError('ERROR: The parameters ' + str(
                            pos) + ' from --list-of-pos must be positive.')
            except:
                raise ValueError('ERROR: The parameters ' + str(
                    pos) + ' from --list-of-pos must be an integer or a slicings. i.e.1: 12 14    i.e.2: 12:15:2')

        list_of_allowed_dvccc_ids = np.array(list_of_allowed_dvccc_ids)

    all_branches = [b.split('/')[-1] for b in g.branch('-a').split() if b.startswith('rcc_')]
    all_branches = np.unique(all_branches)

    for b in all_branches:
        if list_of_allowed_dvccc_ids is None or int(b.split('_')[1]) in list_of_allowed_dvccc_ids:
            print('dvc get : ','.', args.path_to_output,str(Path(outputdir + '/' + b)), b)

            if b.endswith('.dvc'):
                repo.get('.', args.path_to_output,out=str(Path(outputdir + '/' + b[:-4])), rev=b)
            else:
                repo.get('.', args.path_to_output,out=str(Path(outputdir + '/' + b)), rev=b)
    print()
    print('Found ' + str(len(os.listdir(str(Path(outputdir))))) + ' files or folders.')
    print('If files are missing, please use "dvc-cc git sync" to get new result branches and repeat this command.')