#from collections import OrderedDict
from collections import OrderedDict

from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from dvc_cc.git.main import main as git_main
from dvc_cc.git.main import DESCRIPTION as GIT_DESCRIPTION

from dvc_cc.dvc.main import main as dvc_main
from dvc_cc.dvc.main import DESCRIPTION as DVC_DESCRIPTION

from dvc_cc.run.main import main as run_main
from dvc_cc.run.main import DESCRIPTION as run_DESCRIPTION

from dvc_cc.run_all_defined.main import main as run_all_defined_main
from dvc_cc.run_all_defined.main import DESCRIPTION as RUN_ALL_DEFINED_DESCRIPTION

from dvc_cc.output_to_tmp.main import main as output_to_tmp_main
from dvc_cc.output_to_tmp.main import DESCRIPTION as output_to_tmp_DESCRIPTION

from dvc_cc.init.main import main as init_main
from dvc_cc.init.main import DESCRIPTION as INIT_DESCRIPTION

from dvc_cc.status.main import main as status_main
from dvc_cc.status.main import DESCRIPTION as STATUS_DESCRIPTION

from dvc_cc.cancel.main import main as cancel_main
from dvc_cc.cancel.main import DESCRIPTION as CANCEL_DESCRIPTION

from dvc_cc.setting.main import main as setting_main
from dvc_cc.setting.main import DESCRIPTION as SETTING_DESCRIPTION

from dvc_cc.hyperopt.main import main as hyperopt_main
from dvc_cc.hyperopt.main import DESCRIPTION as HYPEROPT_DESCRIPTION

from dvc_cc.live_output.main import main as live_output_main
from dvc_cc.live_output.main import DESCRIPTION as LIVE_OUTPUT_DESCRIPTION

SCRIPT_NAME = 'dvc-cc'
TITLE = 'tools'
DESCRIPTION = 'This software is for Machine Learner and Deep Learner to make scalable and reproducable experiments. It combines ' \
              'the two softwares Data Version Control (www.dvc.org) and Curious Containers (www.curious-containers.cc). DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('init', {'main': init_main, 'description': INIT_DESCRIPTION}),
    ('setting', {'main': setting_main, 'description': SETTING_DESCRIPTION}),
    ('hyperopt', {'main': hyperopt_main, 'description': HYPEROPT_DESCRIPTION}),
    ('run', {'main': run_main, 'description': run_DESCRIPTION}),
    # TODO: This should be the rerun-part!
    #('run-all-defined', {'main': run_all_defined_main, 'description': RUN_ALL_DEFINED_DESCRIPTION}),
    ('git', {'main': git_main, 'description': GIT_DESCRIPTION}),
    ('dvc', {'main': dvc_main, 'description': DVC_DESCRIPTION}),
    ('status', {'main': status_main, 'description': STATUS_DESCRIPTION}),
    ('cancel', {'main': cancel_main, 'description': CANCEL_DESCRIPTION}),
    ('live-output', {'main': live_output_main, 'description': LIVE_OUTPUT_DESCRIPTION}),
    ('output-to-tmp', {'main': output_to_tmp_main, 'description': output_to_tmp_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
