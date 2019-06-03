#!/usr/bin/env python3
from argparse import ArgumentParser
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
import yaml
import os
from subprocess import check_output
import configparser
import keyring
import requests
import json
import numpy as np
import subprocess

DESCRIPTION = 'This script can cancel running jobs'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-ids','--experiment-ids', help='', nargs="+", type=str)
    parser.add_argument('-sids','--subexperiment-ids', help='', nargs="+", type=str)
    parser.add_argument('--all', help='', default=False, action='store_true')
    args = parser.parse_args()

    if (args.experiment_ids is None or len(args.experiment_ids) == 0) and (args.subexperiment_ids is None or len(args.subexperiment_ids) == 0) and args.all == False:
        print('Error: You need to set one of the following parameters: "-ids", "-sids", "--all"')
        print()
        print(parser.print_help())
        exit(1)
    
    if args.subexperiment_ids is not None and len(args.subexperiment_ids) > 0:
        sids = args.subexperiment_ids
    else:
        sids = []

    pw = keyring.get_password('red', 'agency_password')
    uname = keyring.get_password('red', 'agency_username')
    auth = (uname, pw)

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




