from argparse import ArgumentParser
# from dvc_cc.job.main_core import *
from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import subprocess
import os

from dvc_cc.project.create import main as create_jobs_main
from dvc_cc.project.create import DESCRIPTION as CREATE_JOBS_DESCRIPTION

from dvc_cc.project.dummy_to_dvc import main as dummy_to_dvc_jobs_main
from dvc_cc.project.dummy_to_dvc import DESCRIPTION as DUMMY_TO_DVC_JOBS_DESCRIPTION



SCRIPT_NAME = 'dvc-cc job'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC job (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.\n Helper to work with cc.'
MODES = OrderedDict([
    ('create', {'main': create_jobs_main, 'description': CREATE_JOBS_DESCRIPTION}),
    ('dummy', {'main': dummy_to_dvc_jobs_main, 'description': DUMMY_TO_DVC_JOBS_DESCRIPTION})
])

def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
