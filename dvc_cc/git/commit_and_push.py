from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import sys
import os
import subprocess
from subprocess import check_output
from argparse import ArgumentParser

DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'

def get_name_of_branch():
    out = check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    return current.strip("*").strip()

def main():
    git_name_of_branch = get_name_of_branch()
    
    parser = ArgumentParser()
    parser.add_argument('-m', '--message', help='The message to do the git commit.', default=None)
    args = parser.parse_args()
    commit_message = args.message
    if commit_message is None or commit_message == '':
        commit_message = 'Build the experiment: ' + git_name_of_branch + '.'
        
    dvc_files = [d for d in os.listdir() if d.endswith('.dvc') and not d.startswith('_') and d is not '.dir']
    if len(dvc_files) == 0:
        print('Error: no job is available. Please create first a .dvc file to describe the experiment. [branch name '+git_name_of_branch+']')
    else:
        subprocess.call(['git','add','-A'])
        subprocess.call(['git','commit','-m', '"'+commit_message+'"'])
        subprocess.call(['git','push','--set-upstream', 'origin',git_name_of_branch])
        subprocess.call(['hub','sync'])
    
    
