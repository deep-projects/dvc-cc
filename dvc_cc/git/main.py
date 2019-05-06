from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from argparse import ArgumentParser


from dvc_cc.job.main import main as job_main
from dvc_cc.job.main import DESCRIPTION as JOB_DESCRIPTION

SCRIPT_NAME = 'dvc-cc'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC git (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('commit_and_push', {'main': git_main, 'description': GIT_DESCRIPTION}),
    ('branch', {'main': red_main, 'description': RED_DESCRIPTION}),
    ('checkout', {'main': red_main, 'description': RED_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)