SCRIPT_NAME = 'dvc-cc status'
TITLE = 'tools'
DESCRIPTION = 'Gives you the status of your project and an overview, which experiments was already executed.'

import os
import yaml
import requests
import keyring
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
 
def get_main_git_directory_path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-a','--all', help='Show all experiments.',
            type=bool, default=False, action='store_true')
    parser.add_argument('-l','--last_experiments', help='Number of the last experiments that should be displayed. Default is 1. Is the parameter --all is set, this parameter have no effect.', type=int, default=1)
    parser.add_argument('-id','--show_ids', help='Show the curious containers id of the experiment and sub-experiments.', default=False, action='store_true')
    parser.add_argument('-d','--detail', help='Show all details for the sub experiments.', default=False, action='store_true')
    parser.add_argument('-e','--list_of_experimentids', help='A list of experiment ids that you want include in the display.', nargs="+", type=int)
    parser.add_argument('-p','--list_of_position_of_the_subprojects', help='A list of positions of the subproject that you want include in the display.', nargs="+", type=int)
    parser.add_argument('-f','--only_failed', help='Show only failed experiments.', default=False, action='store_true')
    parser.add_argument('-ne','--only_not_executed', help='Show only not executed experiments.', default=False, action='store_true')
    args = parser.parse_args()
    
    # Change the directory to the main git directory.
    os.chdir(get_main_git_directory_path())

    pw = keyring.get_password('red', 'agency_password')
    uname = keyring.get_password('red', 'agency_username')
    auth = (uname, pw)

    if os.path.exists('.dvc_cc/cc_agency_experiments.yml'):
        with open(".dvc_cc/cc_agency_experiments.yml", 'r') as stream:
            try:
                experiments = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)

    # create a list of list with all subprojects, ids and status
    for k in experiments.keys():
        id_of_experiment = experiments[k]['id']
        if id_of_experiment is not None:
            if args.only_not_executed:
                # remove this experiments from the search
                experiments.pop(k, None)
            else:
                r = requests.get(
                    'https://agency.f4.htw-berlin.de/cc/batches?experimentId={}'.format(id_of_experiment),
                    auth=auth
                )
                r.raise_for_status()
                data = r.json()
                experiments[k]['sub_experiment'] = data


    # filter the results:
    if args.only_failed:
        for k in experiments.keys():
            








