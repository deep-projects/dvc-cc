#!/usr/bin/env python3
from argparse import ArgumentParser
import keyring
import requests
import yaml
from dvc_cc.bcolors import *
from pathlib import Path
DESCRIPTION = 'Cancel jobs that are running or registered on a CC server.'

def read_execution_engine():
    with open(str(Path('.dvc_cc/cc_config.yml'))) as f:
        y = yaml.safe_load(f.read())
    return y['execution']['settings']['access']['url']

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-ids','--experiment-ids', help='A list of CC IDs of the experiments. Run "dvc-cc status -id" to show the ID for the experiments.', nargs="+", type=str)
    parser.add_argument('-sids','--subexperiment-ids', help='A list of CC SUB-IDs of the experiments. Run "dvc-cc status -id" to show the SUB-ID for the experiments.', nargs="+", type=str)
    parser.add_argument('--all', help='If this parameter is set, all running or registered jobs get canceled.', default=False, action='store_true')
    parser.add_argument('--last', help='If this parameter is true, than the last started job get canceled.', default=False, action='store_true')
    parser.add_argument('--last_n', help='If you set this parameter it will cancel the last n jobs, that was started.', default=None, type=int)
    args = parser.parse_args()

    pw = keyring.get_password('red', 'agency_password')
    uname = keyring.get_password('red', 'agency_username')
    auth = (uname, pw)

    execution_engine = read_execution_engine()

    if args.last or args.last_n is not None:
        if args.last_n is None:
            args.last_n = 1

        r = requests.get(
            execution_engine+'/experiments',
            auth=auth
        )
        r.raise_for_status()
        data = r.json()

        if args.experiment_ids is None:
            args.experiment_ids = []
        for i in range(args.last_n):
            args.experiment_ids.append(data[i]['_id'])

    if (args.experiment_ids is None or len(args.experiment_ids) == 0) and (args.subexperiment_ids is None or len(args.subexperiment_ids) == 0) and args.all == False:
        print(bcolors.FAIL + 'Error: You need to set one of the following parameters: "-ids", "-sids", "--all", "--last" or "--last_n"' + bcolors.ENDC)
        print()
        print(parser.print_help())
        exit(1)
    
    if args.subexperiment_ids is not None and len(args.subexperiment_ids) > 0:
        sids = args.subexperiment_ids
    else:
        sids = []

    if args.experiment_ids is not None and len(args.experiment_ids) > 0:
        for i in range(len(args.experiment_ids)):
            r = requests.get(
                execution_engine+'/batches?experimentId={}'.format(args.experiment_ids[i]),
                auth=auth
            )
            r.raise_for_status()
            data = r.json()
    
            for d in data:
                if d['state'] != 'succeeded' and d['state'] != 'failed' and d['state'] != 'cancelled':
                    sids.append(d['_id'])

    if args.all:
        r = requests.get(
            execution_engine+'/batches',
            auth=auth
        )
        r.raise_for_status()
        data = r.json()
        for d in data:
            if d['state'] != 'succeeded' and d['state'] != 'failed' and d['state'] != 'cancelled':
                sids.append(d['_id'])
        

    for sid in sids:
        print('DELETE Job: '+execution_engine+'/batches/'+sid)
        r = requests.delete(
            execution_engine+'/batches/'+sid,
            auth=auth
        )
        r.raise_for_status()




