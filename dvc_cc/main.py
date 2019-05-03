#from collections import OrderedDict
from collections import OrderedDict

from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from dvc_cc.git.main import main as git_main
from dvc_cc.git.main import DESCRIPTION as GIT_DESCRIPTION

from dvc_cc.red.main import main as red_main
from dvc_cc.red.main import DESCRIPTION as RED_DESCRIPTION

from dvc_cc.job.main import main as job_main
from dvc_cc.job.main import DESCRIPTION as JOB_DESCRIPTION

SCRIPT_NAME = 'dvc-cc'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('git', {'main': git_main, 'description': GIT_DESCRIPTION}),
    ('red', {'main': red_main, 'description': RED_DESCRIPTION}),
    ('job', {'main': job_main, 'description': JOB_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
