from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes
import sys
from argparse import ArgumentParser


from dvc_cc.git.branch import main as git_branch
from dvc_cc.git.branch import DESCRIPTION as GIT_BRANCH_DESCRIPTION

from dvc_cc.git.commit_and_push import main as commit_and_push_main
from dvc_cc.git.commit_and_push import DESCRIPTION as COMMIT_AND_PUSH_DESCRIPTION
from dvc_cc.git.sync import main as sync_main
from dvc_cc.git.sync import DESCRIPTION as SYNC_DESCRIPTION

import subprocess
from subprocess import check_output

#from dvc_cc.job.main import main as job_main
#from dvc_cc.job.main import DESCRIPTION as JOB_DESCRIPTION

SCRIPT_NAME = 'dvc-cc git'
TITLE = 'tools'
DESCRIPTION = 'This code call the git command and run after this "dvc checkout". If you call "dvc-cc git branch", it will not show the dvc-cc result branches. If you call "dvc-cc git sync" it will checkout to all remote branches!'


def get_name_of_branch():
    out = check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    return current.strip("*").strip()


def main():
    argv = sys.argv[1:]
    if len(argv) == 1 and sys.argv[1] == 'branch':
        git_branch = check_output(['git','branch']).decode("utf8").split('\n')
        for line in git_branch:
            if not line.startswith('  bcc_') and not line.startswith('  remotes/origin/bcc_'):
                print(line)
    elif len(argv) == 1 and sys.argv[1] == 'sync':
        git_name_of_branch = get_name_of_branch()
        all_branches = check_output(["git", "branch", '-a']).decode("utf8").split("\n")
        for b in all_branches:
            pos = b.find('remotes/origin/')
            if pos >= 0:
                b = b[pos+15:]
                print('git checkout '+ b)
                _ = check_output(['git', 'checkout', b])
                _ = check_output(['dvc', 'checkout'])
        print('git checkout ' + git_name_of_branch)
        _ = check_output(['git', 'checkout', git_name_of_branch])
        _ = check_output(['dvc', 'checkout'])
    else:
        subprocess.call(['git'] + argv)
        subprocess.call(['dvc', 'checkout'])
