from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import os
import yaml
import requests
import keyring
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
from argparse import ArgumentParser
import datetime

from dvc_cc.dummy.new import main as new_main
from dvc_cc.dummy.new import DESCRIPTION as NEW_DESCRIPTION

from dvc_cc.dummy.stage import main as stage_main
from dvc_cc.dummy.stage import DESCRIPTION as STAGE_DESCRIPTION

from dvc_cc.dummy.variable import main as variable_main
from dvc_cc.dummy.variable import DESCRIPTION as VARIABLE_DESCRIPTION

from dvc_cc.dummy.command import main as command_main
from dvc_cc.dummy.command import DESCRIPTION as COMMAND_DESCRIPTION

SCRIPT_NAME = 'dvc-cc dummy'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('new', {'main': new_main, 'description': NEW_DESCRIPTION}),
    #('stage', {'main': stage_main, 'description': STAGE_DESCRIPTION}),
    ('variable', {'main': variable_main, 'description': VARIABLE_DESCRIPTION}),
    #('command', {'main': command_main, 'description': COMMAND_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
