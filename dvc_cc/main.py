#from collections import OrderedDict
from collections import OrderedDict

from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from dvc_cc.git.main import main as git_main
from dvc_cc.git.main import DESCRIPTION as GIT_DESCRIPTION

from dvc_cc.run.main import main as run_main
from dvc_cc.run.main import DESCRIPTION as run_DESCRIPTION

from dvc_cc.init.main import main as init_main
from dvc_cc.init.main import DESCRIPTION as INIT_DESCRIPTION

SCRIPT_NAME = 'dvc-cc'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('git', {'main': git_main, 'description': GIT_DESCRIPTION}),
    ('run', {'main': run_main, 'description': run_DESCRIPTION}),
    ('init', {'main': init_main, 'description': INIT_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
