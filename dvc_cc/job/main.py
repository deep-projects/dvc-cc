from argparse import ArgumentParser
# from dvc_cc.job.main_core import *
from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import subprocess
import os

from dvc_cc.job.start_jobs import main as start_jobs_main
from dvc_cc.job.start_jobs import DESCRIPTION as START_JOBS_DESCRIPTION

from dvc_cc.job.check_last_job import main as check_last_main
from dvc_cc.job.check_last_job import DESCRIPTION as CHECK_LAST_DESCRIPTION

from dvc_cc.job.check_all_jobs import main as check_all_jobs_main
from dvc_cc.job.check_all_jobs import DESCRIPTION as CHECK_ALL_JOBS_DESCRIPTION

from dvc_cc.job.remove_all_processing_jobs import main as remove_all_jobs_main
from dvc_cc.job.remove_all_processing_jobs import DESCRIPTION as REMOVE_ALL_JOBS_DESCRIPTION




SCRIPT_NAME = 'dvc-cc job'
TITLE = 'tools'
DESCRIPTION = 'Scripts to work with Curious Containers (CC) and start, cancel and check running jobs.'
MODES = OrderedDict([
    ('run', {'main': start_jobs_main, 'description': START_JOBS_DESCRIPTION}),
    ('check', {'main': check_last_main, 'description': CHECK_LAST_DESCRIPTION}),
    ('check_all', {'main': check_all_jobs_main, 'description': CHECK_ALL_JOBS_DESCRIPTION}),
    ('cancel_all', {'main': remove_all_jobs_main, 'description': REMOVE_ALL_JOBS_DESCRIPTION})
])

def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
