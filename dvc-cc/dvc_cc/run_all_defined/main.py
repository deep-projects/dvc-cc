#!/usr/bin/env python3

from argparse import ArgumentParser
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
import yaml
import os
from subprocess import check_output
import configparser

import numpy as np
import subprocess
from pathlib import Path
DESCRIPTION = 'This script starts the jobs that are already defined with "dvc-cc run" but run with the parameter "--no-exec".'

def get_main_git_directory_Path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()
    
    project_dir = get_main_git_directory_Path()

    #os.chdir(str(Path(project_dir))
    
    gitrepo = GITRepo('.')
    dvcrepo = DVCRepo('.')

    subprocess.call(['git', 'push'])
    subprocess.call(['git', 'push', 'origin', '--tags'])

    if os.path.exists(str(Path('.dvc_cc/cc_agency_experiments.yml'))):
        with open(str(Path('.dvc_cc/cc_agency_experiments.yml')), 'r') as stream:
            try:
                experiments = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)

        start_an_experiment = False
        for k in experiments.keys():
            # find all files
            paths = []
            if experiments[k]['id'] is None:
                print('Start job ' + k)
                start_an_experiment = True
                paths.extend(experiments[k]['files'])
                # write all to tmp.red.yml
                with open(str(Path('.dvc_cc/tmp.red.yml')), 'w') as f:
                    print("batches:", file=f)
                    for path in paths:
                        with open(str(Path(path)),"r") as r:
                            print(r.read(), file=f)
                    with open(str(Path('.dvc_cc/cc_config.yml')),"r") as r:
                        print(r.read(), file=f)

                # execute faice
                output = subprocess.Popen(('faice exec .dvc_cc/tmp.red.yml').split(), stdout=subprocess.PIPE)
                cc_id = output.communicate()[0].decode().split()[-1]
                print('The experiment ID is: ' + cc_id)
                os.remove('.dvc_cc/tmp.red.yml')

                # write cc_id to cc_agency_experiments.yml
                experiments[k]['id'] = cc_id
        if start_an_experiment:
            with open(str(Path('.dvc_cc/cc_agency_experiments.yml')), 'w') as outfile:
                yaml.dump(experiments, outfile, default_flow_style=False)

        # push the ids
        subprocess.call(['git', 'add', '.dvc_cc/cc_agency_experiments.yml'])
        subprocess.call(['git', 'commit', '-m', '\'Update cc_agency_experiments.yml: ' + path + '\''])
        subprocess.call(['git', 'push'])
    else:
        print('Warning you did not define a job with dvc-cc run --no-exec. So there is no job to start.')

        
# TODO: CHECK IF A COMMIT WAS DONE BEFORE A NEW PROJEC

#
#### Improvements:
#
# - it should be possible to check if this repo already are in the yaml file and than it should not be pushed in the file!
# 
# - the BETTER solution is to use yaml see below:
#
#
# from ruamel.yaml import YAML
# yaml = YAML(typ='safe')
#
#red = {
#  'batches': [{
#     'inputs': {},
#     'outputs': {}
#   }]
#}
#
#with open(path, 'w') as f:
#  yaml.dump(red, f)
#
