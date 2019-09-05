from argparse import ArgumentParser
import os
from dvc_cc.bcolors import *
import yaml
import dvc_cc.setting.config_parser

SCRIPT_NAME = 'dvc-cc init'
TITLE = 'tools'
DESCRIPTION = 'Scripts to initial a dvc-cc repository. It throws an exception, if the current project is not a git repository.'

from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
 
def get_main_git_directory_path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--not-interactive', help='If this parameter is set, it will not ask the user to set the values. All values will set by default values.',default=False, action='store_true')
    args = parser.parse_args()

    # 1. Read the setting informations from this build
    package_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    settinginfo_file = os.path.join(package_directory, 'setting', 'settingsinfo.yml')

    # 2. Interactive ask the user to define the settings
    with open(settinginfo_file, 'r') as stream:
        settings = yaml.safe_load(stream)
    dvc_cc.setting.config_parser.parse(settings)

    # 3. Save the settings