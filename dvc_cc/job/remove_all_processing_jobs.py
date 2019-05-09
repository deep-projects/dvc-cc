#!/usr/bin/env python3
import os
import requests
from collections import Counter
from ruamel.yaml import YAML
import datetime

yaml = YAML(typ='safe')


from argparse import ArgumentParser
import json
import subprocess
import os
import numpy as np


DESCRIPTION = 'This script cancel all jobs that current running.'


def main():
    parser = ArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()

    with open(os.path.expanduser('~/.cache/dvc_cc/secrets.yml')) as f:
        secrets = yaml.load(f)

    auth = (secrets['agency_username'], secrets['agency_password'])

    experiment_ids= ['']

    for i in range(len(experiment_ids)):
        r = requests.get(
            'https://agency.f4.htw-berlin.de/cc/batches?experimentId={}'.format(experiment_ids[i]),
            auth=auth
        )
        r.raise_for_status()
        data = r.json()

        for batch in data:
            if batch['state'] != 'cancelled' and batch['state'] != 'failed' and batch['state'] != 'succeeded':
                print('DELETE Job: https://agency.f4.htw-berlin.de/cc/batches/'+batch['_id'])
                r = requests.delete(
                    'https://agency.f4.htw-berlin.de/cc/batches/'+batch['_id'],
                    auth=auth
                )
                r.raise_for_status()



