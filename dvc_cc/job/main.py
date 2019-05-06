from argparse import ArgumentParser
# from dvc_cc.job.main_core import *

from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import subprocess
import os

from dvc_cc.job.start_jobs import main as red_delete_main
from dvc_cc.job.start_jobs import DESCRIPTION as RED_DELETE_DESCRIPTION

from dvc_cc.job.check_last import main as check_last_main
from dvc_cc.job.check_last import DESCRIPTION as CHECK_LAST_DESCRIPTION

from dvc_cc.job.check_all_jobs import main as check_all_jobs_main
from dvc_cc.job.check_all_jobs import DESCRIPTION as CHECK_ALL_JOBS_DESCRIPTION

SCRIPT_NAME = 'dvc-cc job'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC job (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.\n Helper to work with cc.'
MODES = OrderedDict([
    ('run', {'main': start_jobs_main, 'description': START_JOBS_DESCRIPTION}),
    ('check', {'main': check_last_main, 'description': CHECK_LAST_DESCRIPTION}),
    ('check', {'main': check_last_main, 'description': CHECK_LAST_DESCRIPTION})
])

def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
