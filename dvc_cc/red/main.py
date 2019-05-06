from argparse import ArgumentParser

from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from dvc_cc.red.add_to_red_yml_file import main as red_create_main
from dvc_cc.red.add_to_red_yml_file import DESCRIPTION as RED_CREATE_DESCRIPTION

from dvc_cc.red.delete_red_yml_file import main as red_delete_main
from dvc_cc.red.delete_red_yml_file import DESCRIPTION as RED_DELETE_DESCRIPTION


from dvc_cc.red.create_red_yml_file import create_red_yml_file
# from dvc_cc.red.main_core import *

SCRIPT_NAME = 'dvc-cc red'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC red (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.\n Helper to create the red yml file.'
MODES = OrderedDict([
    ('add_job', {'main': red_create_main, 'description': RED_CREATE_DESCRIPTION}),
    ('delete', {'main': red_delete_main, 'description': RED_DELETE_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
