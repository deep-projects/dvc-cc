SCRIPT_NAME = 'dvc-cc status'
TITLE = 'tools'
DESCRIPTION = 'Gives you the status of your project and an overview, which experiments was already executed.'

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

def print_overview(experiments, show_ids = False):
    print()
    for exp in list(experiments.keys())[::-1]:
        if show_ids:
            print(exp, experiments[exp]['id'])
            for sub in experiments[exp]['sub_experiment']:
                if sub['state'] == 'failed' or sub['state'] == 'succeeded' or sub['state'] == 'canceled':
                    c = sub['detail']['history'][-1]['ccagent']['command']
                    if len(c) == 13:
                        print('\t-%10s | %50s | %s' % (sub['state'], c[-1], sub['_id']))
                    else:
                        print('\t-%10s | %50s | %s' % (sub['state'], '', sub['_id']))
                else:
                    print('\t-%10s | %50s | %s' % (sub['state'], 'still running', sub['_id']))
        else:
            print(exp)
            status_count = {}
            for sub in experiments[exp]['sub_experiment']:
                if sub['state'] in status_count:
                    status_count[sub['state']] += 1
                else:
                    status_count[sub['state']] = 1
            print('\t',status_count)
        print()
    #print(experiments[exp])

def print_detail(experiments, show_ids = False):
    print()
    for exp in list(experiments.keys())[::-1]:
        print(bcolors.OKGREEN+'#'*54+bcolors.ENDC)
        if show_ids:
            print(bcolors.OKGREEN+'# %50s # (%s)' % (exp, experiments[exp]['id'])+bcolors.ENDC)
        else:
            print(bcolors.OKGREEN+'# %50s #' % (exp)+bcolors.ENDC)
        print(bcolors.OKGREEN+'#'*54+bcolors.ENDC)
        print('')

        for sub in experiments[exp]['sub_experiment']:
            print(bcolors.OKGREEN+'State: '+bcolors.ENDC + sub['state'])
            if show_ids:
                print(bcolors.OKGREEN+'ID of subexperiment: '+bcolors.ENDC + sub['_id'])
            for h in sub['detail']['history']:
                print(bcolors.OKGREEN+'Time (' + h['state'] + '):  '+bcolors.ENDC + datetime.datetime.fromtimestamp(h['time']).strftime('%Y-%m-%d %H:%M:%S'))
            if sub['state'] == 'failed' or sub['state'] == 'succeeded' or sub['state'] == 'canceled':
                print(bcolors.OKGREEN+'Used server node: '+bcolors.ENDC + str(sub['node']))
                if len(sub['detail']['usedGPUs']) == 1:
                    print(bcolors.OKGREEN+'Used GPUs: '+bcolors.ENDC + str(sub['detail']['usedGPUs'][0]))
                else:
                    print(bcolors.OKGREEN+'Used GPUs: ' +bcolors.ENDC+ str(sub['detail']['usedGPUs']))
                c = sub['detail']['history'][-1]['ccagent']['command']
                if len(c) == 13:
                    print(bcolors.OKGREEN +'Files: '+bcolors.ENDC + str(c[-1]))                    
                else:
                    print(bcolors.OKGREEN +'Files:'+bcolors.ENDC+' ALL')
                print(bcolors.OKGREEN + 'Return Code: ' + bcolors.ENDC + str(sub['detail']['history'][-1]['ccagent']['process']['returnCode']))
                print()
                print(bcolors.OKGREEN + 'stdOut: ' + bcolors.ENDC)
                print('\n'.join(sub['detail']['history'][-1]['ccagent']['process']['stdOut']))
                print()
                print(bcolors.WARNING + 'stdErr: ' + bcolors.ENDC)
                print('\n'.join(sub['detail']['history'][-1]['ccagent']['process']['stdErr']))
                print()
            print()

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
    filtered_experiments = {}
    for k in list(experiments.keys())[::-1]:
        if args.list_of_experimentids is not None and int(k.split('_')[1]) not in args.list_of_experimentids:
            continue

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

                for i in range(len(data)):
                    r = requests.get(
                          'https://agency.f4.htw-berlin.de/cc/batches/{}'.format(data[i]['_id']),
                          auth=auth
                    )
                    r.raise_for_status()
                    data2 = r.json()
                    data[i]['detail'] = data2

                if args.list_of_position_of_the_subprojects is not None:
                    data_tmp = []
                    for i in range(len(data)):
                        if i in args.list_of_position_of_the_subprojects:
                            data_tmp.append(data[i])
                    data = data_tmp

                if not args.only_failed:
                    experiments[k]['sub_experiment'] = data
                    filtered_experiments[k] = experiments[k]
                else:
                    failed_data = []
                    for d in data:
                        if d['state'] == 'failed':
                            failed_data.append(d)
                    if len(failed_data) > 0:
                        experiments[k]['sub_experiment'] = failed_data
                        filtered_experiments[k] = experiments[k]
        if args.all == False and len(filtered_experiments) >= args.number_of_experiments:
            break
    
    if args.detail:
         print_detail(filtered_experiments, args.show_ids)
    else:
         print_overview(filtered_experiments, args.show_ids)

















