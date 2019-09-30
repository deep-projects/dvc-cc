from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes
from dvc_cc.bcolors import  *

from dvc_cc.hyperopt.new import main as new_main
from dvc_cc.hyperopt.new import DESCRIPTION as NEW_DESCRIPTION

from dvc_cc.hyperopt.new_suggest import main as new_suggest_main
from dvc_cc.hyperopt.new_suggest import DESCRIPTION as NEW_SUGGEST_DESCRIPTION

from dvc_cc.hyperopt.var import main as variable_main
from dvc_cc.hyperopt.var import DESCRIPTION as VARIABLE_DESCRIPTION

from dvc_cc.hyperopt.plot_beta_distribution import main as plot_beta_distribution_main
from dvc_cc.hyperopt.plot_beta_distribution import DESCRIPTION as PLOT_BETA_DESCRIPTION

SCRIPT_NAME = 'dvc-cc hyperopt'
TITLE = 'tools'
DESCRIPTION = 'With '+bcolors.OKBLUE+'dvc-cc hyperopt'+bcolors.ENDC+' you can create DVC files with and without hyperparameter that you can than run with ' \
              +bcolors.OKBLUE+'dvc-cc run'+bcolors.ENDC+'.'
MODES = OrderedDict([
    ('new', {'main': new_main, 'description': NEW_DESCRIPTION}),
    ('new-suggest', {'main': new_suggest_main, 'description': NEW_SUGGEST_DESCRIPTION}),
    #('stage', {'main': stage_main, 'description': STAGE_DESCRIPTION}),
    ('var', {'main': variable_main, 'description': VARIABLE_DESCRIPTION}),
    #('command', {'main': command_main, 'description': COMMAND_DESCRIPTION}),
    ('plot-beta', {'main': plot_beta_distribution_main, 'description': PLOT_BETA_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
