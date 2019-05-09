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

DESCRIPTION = 'This scripts checks all jobs that you already started.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()

    with open(os.path.expanduser('~/.cache/dvc_cc/secrets.yml')) as f:
        secrets = yaml.load(f)

    auth = (secrets['agency_username'], secrets['agency_password'])

    experiment_ids = ['']

    for i in range(len(experiment_ids)):
        r = requests.get(
            'https://agency.f4.htw-berlin.de/cc/batches?experimentId={}'.format(experiment_ids[i]),
            auth=auth
        )
        r.raise_for_status()
        data = r.json()

        print(Counter([batch['state'] for batch in data]))



