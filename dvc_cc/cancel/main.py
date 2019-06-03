#!/usr/bin/env python3
from argparse import ArgumentParser
import keyring
import requests
import json
import numpy as np

DESCRIPTION = 'This script can cancel running jobs. This script do not cancel jobs that are NOT pushed to run in the cloud.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-ids','--experiment-ids', help='A list of ID\s of experiments.', nargs="+", type=str)
    parser.add_argument('-sids','--subexperiment-ids', help='A list of ID\'s of sub experiments', nargs="+", type=str)
    parser.add_argument('--all', help='If this parameter is set, all jobs get canceled.', default=False, action='store_true')
    parser.add_argument('--last', help='If this parameter is true, than the last started job get executed.', default=False, action='store_true')
    parser.add_argument('--last_n', help='If you set this parameter it will cancel the last n jobs, that was sstarted.', default=None, type=int)
    args = parser.parse_args()

    pw = keyring.get_password('red', 'agency_password')
    uname = keyring.get_password('red', 'agency_username')
    auth = (uname, pw)

    if args.last or args.last_n is not None:
        if args.last_n is None:
            args.last_n = 1

        r = requests.get(
            'https://agency.f4.htw-berlin.de/cc/experiments',
            auth=auth
        )
        r.raise_for_status()
        data = r.json()

        if args.experiment_ids is None:
            args.experiment_ids = []
        for i in range(args.last_n):
            args.experiment_ids.append(data[i]['_id'])

    if (args.experiment_ids is None or len(args.experiment_ids) == 0) and (args.subexperiment_ids is None or len(args.subexperiment_ids) == 0) and args.all == False:
        print('Error: You need to set one of the following parameters: "-ids", "-sids", "--all", "--last" or "--last_n"')
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
                'https://agency.f4.htw-berlin.de/cc/batches?experimentId={}'.format(args.experiment_ids[i]),
                auth=auth
            )
            r.raise_for_status()
            data = r.json()
    
            for d in data:
                if d['state'] != 'succeeded' and d['state'] != 'failed' and d['state'] != 'cancelled':
                    sids.append(d['_id'])

    if args.all:
        r = requests.get(
            'https://agency.f4.htw-berlin.de/cc/batches',
            auth=auth
        )
        r.raise_for_status()
        data = r.json()
        for d in data:
            if d['state'] != 'succeeded' and d['state'] != 'failed' and d['state'] != 'cancelled':
                sids.append(d['_id'])
        

    for sid in sids:
        print('DELETE Job: https://agency.f4.htw-berlin.de/cc/batches/'+sid)
        r = requests.delete(
            'https://agency.f4.htw-berlin.de/cc/batches/'+sid,
            auth=auth
        )
        r.raise_for_status()




