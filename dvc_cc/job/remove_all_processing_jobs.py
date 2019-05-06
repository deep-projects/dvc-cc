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


DESCRIPTION = 'DVC-CC job (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.\n Helper to check the last job that you started.'


def main():
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



