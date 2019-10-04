import sys
import subprocess
from subprocess import check_output
from dvc.repo import Repo as DVCRepo
import getpass
import time
from dvc_cc.bcolors import *

SCRIPT_NAME = 'dvc-cc git'
TITLE = 'tools'
DESCRIPTION = 'With this script you can call everything what you can do with git. If you call '+bcolors.OKBLUE+'dvc-cc git branch'+bcolors.ENDC+' it will ' \
              'show you only your working branches and ignore DVC-CC branches. If you call '+bcolors.OKBLUE+'dvc-cc git sync'+bcolors.ENDC+' it will sync ' \
              'all remote branches and create a local branch for this. All other commands are piped to git directly and ' \
              'run '+bcolors.OKBLUE+'dvc checkout'+bcolors.ENDC+' after this to clean up your branches.'


def get_name_of_branch():
    out = check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    return current.strip("*").strip()


def main():
    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv or len(argv) == 0:
      print(DESCRIPTION)
      print()
      print('dvc-cc git branch:')
      print('\tShows the branches without the automatic created branches from DVC-CC.')
      print('dvc-cc git sync [-d] [-l]:')
      print('\tCreate local branches for all remote branches.')
      print('\t\t-d: Than it will download all files from the DVC-Server.')
      print('\t\t-l: If this is set, than it will repeat every 20 seconds the script.')
      print('\t\t\tYou can cancel it with CTRL+C.')
      print('dvc-cc git OTHER_GIT_COMMAND:')
      print('\tEvery other git command will be piped directly to git. After it was called it will run '+bcolors.OKBLUE+'dvc checkout'+bcolors.ENDC)
      print('\t\tto cleanup the repository')
    elif len(argv) == 1 and sys.argv[1] == 'branch':
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

        if (len(argv) > 2 and argv[1] == '-l') or (len(argv) == 3 and argv[2] == '-l'):
            loop = True
        else:
            loop = False

        _ = check_output(['git', 'stash'])

        try:
            is_first_iteration = True
            while loop or is_first_iteration:

                if is_first_iteration == False:
                    print('All remote branches were created locally. Wait 5 seconds for the next pull request. To cancel the script press CTRL+C.')
                    time.sleep(5)
                is_first_iteration = False

                _ = check_output(["git", "pull"]).decode("utf8").split("\n")

                all_branches = check_output(["git", "branch", '-a']).decode("utf8").split("\n")
                all_branches_local = [i[2:] for i in all_branches if len(i.split('/')) == 1]
                all_branches_remote = [i.split('/')[-1] for i in all_branches if len(i.split('/')) > 1]

                for b in all_branches_remote:
                    if b not in all_branches_local:
                        print('git checkout '+ b)
                        _ = check_output(['git', 'checkout', b])

                        print('\t\ŧI CHECKOUT THE DATA')

                        try:
                            repo.checkout()
                        except:
                            print('Some files are missing.')

                        if len(argv) >= 2 and argv[1] == '-d':
                            print('\t\ŧI PULL THE DATA')
                            try:
                                repo.pull()
                            except:
                                print('Some files are missing.')
        finally:
            print('git checkout ' + git_name_of_branch)
            _ = check_output(['git', 'checkout', git_name_of_branch])
            try:
                repo.checkout()
            except:
                print('Some files are missing.')
            try:
                repo.pull()
            except:
                print('Some files are missing.')
            _ = check_output(['git', 'stash', 'apply'])
    else:
        subprocess.call(['git'] + argv)
        try:
            subprocess.call(['dvc', 'checkout'])
        except:
            print('Some files are missing.')
