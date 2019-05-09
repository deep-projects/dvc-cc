#!/usr/bin/env python3
import sys
import os
import subprocess
from subprocess import check_output
import numpy as np
from argparse import ArgumentParser

DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'

def get_name_of_branch():
    out = check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    return current.strip("*").strip()

def main():
    git_name_of_branch = get_name_of_branch()
    
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('name_of_branch', help='The name of the branch', default=None)
    parser.add_argument('-l', '--last_prefix', help='Use the last prefix', default=False,action='store_true')
    parser.add_argument('-i', '--init_from_this_branch', help='The init branch is the current one.', default=False,action='store_true')
    parser.add_argument('-w', '--without_prefix', help='Create the branch name without prefix', default=False,action='store_true')
    args = parser.parse_args()

    name_of_branch = args.name_of_branch
    
    if args.init_from_this_branch == False:
        initbranch = 'master'
    else:
        initbranch = git_name_of_branch
    if args.without_prefix:
        prefix = ''
    else:
        # find last index
        a = check_output(['git','branch'])
        a = str(a).split(' ')
        pos = [int(b[:3]) for b in a if str.isdigit(b[:3])]
        if len(pos) > 0:
            last_pos = np.max(pos)
        else:
            last_pos = 0
        if args.last_prefix == False:
            last_pos += 1
            
        prefix = '%0.3d_'%last_pos
    
    #subprocess.call(['hub', 'sync'])
    subprocess.call(['git', 'checkout', initbranch])
    subprocess.call(['dvc', 'pull'])
    subprocess.call(['git', 'branch', prefix + name_of_branch])
    subprocess.call(['git', 'checkout', prefix + name_of_branch])
    subprocess.call(['dvc', 'push'])
    
    subprocess.call(['git', 'commit','-m', '"Init '+prefix+name_of_branch+' from '+git_name_of_branch+'"'])
    subprocess.call(['git', 'push', '--set-upstream', 'origin', prefix+name_of_branch])
    #subprocess.call(['hub', 'sync'])
    
    
