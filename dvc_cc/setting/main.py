SCRIPT_NAME = 'dvc-cc setting'
TITLE = 'tools'
DESCRIPTION = 'Gives you the setting of your project.'

import os
import yaml
import requests
import keyring
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
from argparse import ArgumentParser
import datetime

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


def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-a','--all', help='Show all experiments of this project.', default=False, action='store_true')
    parser.add_argument('-n','--number_of_experiments', help='Number of the last experiments that should be displayed. Default is 1. Is the parameter --all is set, this parameter have no effect.', type=int, default=1)
    parser.add_argument('-id','--show_ids', help='Show the curious containers id of the experiment and curious containers id of the sub-experiments.', default=False, action='store_true')
    parser.add_argument('-d','--detail', help='Show all details and outputs for the sub experiments.', default=False, action='store_true')
    parser.add_argument('-e','--list_of_experimentids', help='A list of experiment ids that you want include in the display.', nargs="+", type=int)
    parser.add_argument('-p','--list_of_position_of_the_subprojects', help='A list of positions of the subproject that you want include in the display.', nargs="+", type=int)
    parser.add_argument('-f','--only_failed', help='Show only failed experiments.', default=False, action='store_true')
    parser.add_argument('-ne','--only_not_executed', help='Show only not executed experiments.', default=False, action='store_true')
    args = parser.parse_args()
    
    # Change the directory to the main git directory.
    os.chdir(get_main_git_directory_path())













