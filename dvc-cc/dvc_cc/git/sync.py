#!/usr/bin/env python3
import sys
import os
import subprocess
from subprocess import check_output
import numpy as np
from argparse import ArgumentParser

DESCRIPTION = 'Create a new git branch and handle prefix ids.'

def get_name_of_branch():
    out = check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    return current.strip("*").strip()

def main():
    git_name_of_branch = get_name_of_branch()

    all_branches = check_output(["git", "branch", '-a']).decode("utf8").split("\n")

    for b in all_branches:
        pos = b.find('remotes/origin/')
        if pos >= 0:
            b = b[pos+15:]
            subprocess.call(['git', 'checkout', b])
            
    
