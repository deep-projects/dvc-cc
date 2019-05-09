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

DESCRIPTION = '...'

def main():
    parser = ArgumentParser()
    parser.add_argument('-d','--dvc_dummy_file', help = 'The dvc_dummy file with that you want to create a dvc file.',
    parser.add_argument('-p','--params', help = 'The params with that you would call your programm', default=None) default=None)
    args = parser.parse_args()
    
    if args.params is not None:
        name_of_experiment = subprocess.check_output(('python code/argparser.py ' + args.params).split())
    else:
        name_of_experiment = subprocess.check_output(('python code/argparser.py').split())

    name_of_experiment = name_of_experiment.decode().split('\n')[-2]
    print(name_of_experiment)

    if args.dvc_dummy_file is None:
        dummy_files = [f for f in os.listdir() if f.endswith('.dvc_dummy')]
    else:
        dummy_files = [args.dvc_dummy_file]
    for dummy_file in dummy_files:
        f = open(dummy_file, "r")
        content = f.read()
        f.close() 

        if args.params is not None:
            content = content.replace('<<param>>', args.params)
            content = content.replace('<<p>>', args.params)
        else:
            content = content.replace('<<param>>', '')
            content = content.replace('<<p>>', '')

        content = content.replace('<<name_of_experiment>>', name_of_experiment)
        content = content.replace('<<noe>>', name_of_experiment)

        f= open(dummy_file[:-10] + '_' + name_of_experiment + '.dvc',"w+")
        f.write(content)
        f.close() 

        print('Create ' + dummy_file[:-10] + '_' + name_of_experiment + '.dvc')

