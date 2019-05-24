from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from argparse import ArgumentParser


from dvc_cc.git.branch import main as git_branch
from dvc_cc.git.branch import DESCRIPTION as GIT_BRANCH_DESCRIPTION

from dvc_cc.git.commit_and_push import main as commit_and_push_main
from dvc_cc.git.commit_and_push import DESCRIPTION as COMMIT_AND_PUSH_DESCRIPTION

#from dvc_cc.job.main import main as job_main
#from dvc_cc.job.main import DESCRIPTION as JOB_DESCRIPTION

SCRIPT_NAME = 'dvc-cc'
TITLE = 'tools'
DESCRIPTION = 'Scripts to make working with git easier.'
MODES = OrderedDict([
    ('commit-and-push', {'main': commit_and_push_main, 'description': COMMIT_AND_PUSH_DESCRIPTION}),
    ('branch', {'main': git_branch, 'description': GIT_BRANCH_DESCRIPTION}),
    #('checkout', {'main': red_main, 'description': RED_DESCRIPTION})
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
