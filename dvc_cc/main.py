#from collections import OrderedDict
from collections import OrderedDict

from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from dvc_cc.git.main import main as git_main
from dvc_cc.git.main import DESCRIPTION as GIT_DESCRIPTION

from dvc_cc.jobs.main import main as jobs_main
from dvc_cc.jobs.main import DESCRIPTION as JOBS_DESCRIPTION

from dvc_cc.init.main import main as init_main
from dvc_cc.init.main import DESCRIPTION as INIT_DESCRIPTION

SCRIPT_NAME = 'dvc-cc'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('git', {'main': git_main, 'description': GIT_DESCRIPTION}),
    ('jobs', {'main': jobs_main, 'description': JOBS_DESCRIPTION}),
    ('init', {'main': init_main, 'description': INIT_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
