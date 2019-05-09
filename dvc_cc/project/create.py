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
import dvc_cc

DESCRIPTION = 'list all started jobs'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-m','--mini_project', help='Create only a mini project with that you can use dvc.',default=False, action='store_true')
    args = parser.parse_args()

    if args.mini_project:
        f = os.path.dirname(os.path.realpath(dvc_cc.__file__)) + '/project/example_project_mini/.'
    else:
        f = os.path.dirname(os.path.realpath(dvc_cc.__file__)) + '/project/example_project/.'
    print(f)
    output = subprocess.check_output(('dvc init').split())
    output = subprocess.check_output(('cp -a '+f + ' .').split())
    

    
