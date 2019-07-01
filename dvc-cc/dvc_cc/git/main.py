from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes
import sys
from argparse import ArgumentParser

import subprocess
from subprocess import check_output

from dvc.repo import Repo as DVCRepo
import getpass
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
            if not line.startswith('  rcc_') and not line.startswith('  remotes/origin/rcc_') and not line.startswith('  cc_') and not line.startswith('  remotes/origin/cc_'):
                print(line)
    elif sys.argv[1] == 'sync':
        repo = DVCRepo()
        if (len(argv) > 2 and argv[1] == '-d') or (len(argv) == 3 and argv[2] == '-d'):
            remote_name = repo.config.config['core']['remote']
            remote_settings = repo.config.config['remote "' + remote_name + '"']
            if 'ask_password' in remote_settings and remote_settings['ask_password']:
                remote_settings['password'] = getpass.getpass('Password for ' + remote_settings['url'] + ': ')
                remote_settings['ask_password'] = False

        git_name_of_branch = get_name_of_branch()
        _ = check_output(["git", "pull"]).decode("utf8").split("\n")

        all_branches = check_output(["git", "branch", '-a']).decode("utf8").split("\n")
        all_branches_local = [i[2:] for i in all_branches if len(i.split('/')) == 1]
        all_branches_remote = [i.split('/')[-1] for i in all_branches if len(i.split('/')) > 1]

        if (len(argv) > 2 and argv[1] == '-l') or (len(argv) == 3 and argv[2] == '-l'):
            loop = True
        else:
            loop = False

        try:
            is_first_iteration = True
            while loop or is_first_iteration:
                is_first_iteration = False
                for b in all_branches_remote:
                    if b not in all_branches_local:
                        print('git checkout '+ b)
                        _ = check_output(['git', 'checkout', b])
                        print('\t\ŧI CHECKOUT THE DATA')
                        repo.checkout()
                        if argv[1] == '-d':
                            print('\t\ŧI PULL THE DATA')
                            repo.pull()
        finally:
            print('git checkout ' + git_name_of_branch)
            _ = check_output(['git', 'checkout', git_name_of_branch])
            repo.checkout()
    else:
        subprocess.call(['git'] + argv)
        subprocess.call(['dvc', 'checkout'])
