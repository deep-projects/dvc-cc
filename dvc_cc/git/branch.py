#!/usr/bin/env python3
import sys
import os
import subprocess
from subprocess import check_output
import numpy as np

DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'

def get_name_of_branch():
    out = check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    return current.strip("*").strip()

def main():
    git_name_of_branch = get_name_of_branch()
    
    name_of_branch = sys.argv[1]
    
    initbranch = 'master'
    
    if len(sys.argv) == 3 and sys.argv[2] == 'without':
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
        if len(sys.argv) < 3 or sys.argv[2] != 'same':
            last_pos += 1
        if len(sys.argv) >= 3 and sys.argv[2] == '.':
            initbranch = git_name_of_branch
        elif len(sys.argv) == 4 and sys.argv[3] == '.':
            initbranch = git_name_of_branch
            
        prefix = '%0.3d_'%last_pos
    
    subprocess.call(['hub', 'sync'])
    subprocess.call(['git', 'checkout', initbranch])
    subprocess.call(['dvc', 'pull'])
    subprocess.call(['git', 'branch', prefix + name_of_branch])
    subprocess.call(['git', 'checkout', prefix + name_of_branch])
    subprocess.call(['dvc', 'pull'])
    
    subprocess.call(['git', 'commit','-m', '"Init '+prefix+name_of_branch+' from '+git_name_of_branch+'"'])
    subprocess.call(['git', 'push', '--set-upstream', 'origin', prefix+name_of_branch])
    subprocess.call(['hub', 'sync'])
    
    
