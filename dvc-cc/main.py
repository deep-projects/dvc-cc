#from collections import OrderedDict

from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from dvc_cc.slide_tiles.main import main as slide_tiles_main
from dvc_cc.slide_tiles.main import DESCRIPTION as SLIDE_TILES_DESCRIPTION

from dvc_cc.merge_hdf5.main import main as merge_hdf5_main
from dvc_cc.merge_hdf5.main import DESCRIPTION as MERGE_HDF5_DESCRIPTION

import sys
from argparse import ArgumentParser

SCRIPT_NAME = 'dvc-cc'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('git', {'main': slide_tiles_main, 'description': SLIDE_TILES_DESCRIPTION}),
    ('cc', {'main': merge_hdf5_main, 'description': MERGE_HDF5_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
