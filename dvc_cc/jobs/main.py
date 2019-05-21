from argparse import ArgumentParser
# from dvc_cc.job.main_core import *
from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import subprocess
import os

from dvc_cc.jobs.run import main as run_main
from dvc_cc.jobs.run import DESCRIPTION as RUN_DESCRIPTION


SCRIPT_NAME = 'dvc-cc jobs'
TITLE = 'tools'
DESCRIPTION = 'Scripts to work with Curious Containers (CC) and start, cancel and check running jobs.'
MODES = OrderedDict([
    ('run', {'main': run_main, 'description': RUN_DESCRIPTION})
])

def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
