from argparse import ArgumentParser
import subprocess
from subprocess import check_output
import os
from dvc_cc.bcolors import *
from pathlib import Path
import keyring
import getpass
import pexpect
import urllib.parse
import yaml
import requests

SCRIPT_NAME = 'dvc-cc keyring'
TITLE = 'tools'
DESCRIPTION = 'Scripts to manage the keyring information that are saved.'

def get_gitinformation():
    # TODO: use the intern python-git for this.
    out = check_output(["git", "config", "--get", "remote.origin.url"]).decode("utf8")
    if out.startswith('https://'):
        _,_, gitrepo,gitowner,gitname = out.split('/')
    else:
        gitrepo = out[4:out.find(':')]
        gitowner = out[out.find(':')+1:out.find('/')]
        gitname = out[out.find('/')+1:]

    gitname = gitname[:gitname.find('.git')+4]
    return gitrepo,gitowner,gitname

def get_dvcurl_information():
    dvc_url = []
    try:
      with open(str(Path(".dvc/config.local")), "r") as fi:
        for ln in fi:
            ln = ln.replace(' ', '')
            if ln.startswith("url="):
              dvc_url.append(ln)
    except:
        try:
          with open(str(Path(".dvc/config")), "r") as fi:
            for ln in fi:
                ln = ln.replace(' ', '')
                if ln.startswith("url="):
                  dvc_url.append(ln)
        except:
          print('No .dvc/config or .dvc/config.local was found.')

    if len(dvc_url) != 1:
      if len(dvc_url) == 0:
        print('no url was found. please set the url in the .dvc/config file.')
      if len(dvc_url) > 1:
        print('multiple url was found. only one url is currently allowed')
      print('Please specifier the servername and the repository.')
      dvc_url = None
      dvc_user = None
      dvc_server = input("dvc_servername: ")
      dvc_path = input("dvc_path_to_working_repository: ")
    else:
      dvc_user = dvc_url[0].split('@')[0]
      dvc_url = dvc_url[0].split('@')[1]
      dvc_server = dvc_url[:dvc_url.find(':')]
      dvc_path = dvc_url[dvc_url.find(':')+1:].rstrip()
    return dvc_url, dvc_server, dvc_path, dvc_user.split('/')[-1]

def read_execution_engine():
    with open(str(Path('.dvc_cc/cc_config.yml'))) as f:
        y = yaml.safe_load(f.read())
    return y['execution']['settings']['access']['url']

def remove_keyring_pair(keyring_service, key_dvc_pw):
    try:
        keyring.delete_password(keyring_service, key_dvc_pw)
        print('Delete the keyring parameter: ', keyring_service, key_dvc_pw)
    except:
        print('The following combination of keyring service and name does not exists: ', keyring_service, key_dvc_pw)

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--htw-student', help='If this parameter is set, it will not ask the user to set the values. '
                                             'All values will set by default values. This parameter is only used, '
                                              'if the paraneter "--set" is used.',default=False,
                        action='store_true')
    parser.add_argument('--htw-staff', help='If this parameter is set, it will not ask the user to set the values. '
                                             'All values will set by default values. This parameter is only used, '
                                              'if the paraneter "--set" is used.' ,default=False, action='store_true')

    parser.add_argument('--keyring-service', type=str,
                        help='The default name of the keyring service that is used. For more information visit: '
                             'https://www.curious-containers.cc/docs/red-format-protecting-credentials',
                        default= 'red')

    parser.add_argument('--set', help='If this parameter is set, it will not ask the user to set the values. '
                                            'All values will set by default values.', default=False,
                        action='store_true')
    parser.add_argument('--check', help='If this parameter is set, it will check the current settings.', default=False,
                        action='store_true')
    parser.add_argument('--check-unsave', help='This is the same as --check, only that it shows the original error '
                                               'message of git push and sshfs connections. Warning: It can happen '
                                               'that the message shows your password.',
                        default=False,
                        action='store_true')
    parser.add_argument('--delete', help='Delete all keyring informations.',
                        default=False,
                        action='store_true')
    args = parser.parse_args()

    keyring_service = args.keyring_service

    git_repo, git_owner, git_name = get_gitinformation()
    dvc_url, dvc_server, dvc_path, dvcurl_user = get_dvcurl_information()

    key_git_pw = git_repo.replace('.', '_').replace('-', '_') + "_password"
    key_git_username = git_repo.replace('.', '_').replace('-', '_') + "_username"
    key_git_email = git_repo.replace('.', '_').replace('-', '_') + "_email"

    key_dvc_username = dvc_server.replace('.', '_').replace('-', '_') + "_username"  # s0000000
    key_dvc_pw = dvc_server.replace('.', '_').replace('-', '_') + "_password"  # PWWWW

    key_agency_username = 'agency_username' # s0000000
    key_agency_pw = 'agency_password' # PWWWW




    if args.set:
        print('# Set the keyring parameters')

        keyring.set_password(keyring_service, key_dvc_username, dvcurl_user)
        if args.htw_student or args.htw_staff:
            keyring.set_password(keyring_service, key_agency_username, dvcurl_user)
        else:
            agency_user = input('\tPlease insert your '+bcolors.OKBLUE+'username for the CC-Agency'+bcolors.ENDC+': ')
            keyring.set_password(keyring_service, key_agency_username, agency_user)

        if args.htw_student:
            pw = getpass.getpass('\tPlease insert your '+bcolors.OKBLUE+'password for the '
                                                                        'DT-Cluster / CC agency'+bcolors.ENDC+': ')
            keyring.set_password(keyring_service, key_agency_pw, pw)
            keyring.set_password(keyring_service, key_dvc_pw, pw)
        else:
            pw = getpass.getpass('\tPlease insert your '+bcolors.OKBLUE+'password for the CC-Agency'+bcolors.ENDC+': ')
            keyring.set_password(keyring_service, key_agency_pw, pw)
            if args.htw_staff:
                pw = getpass.getpass('\tPlease insert your ' + bcolors.OKBLUE + 'password for LDAP' + bcolors.ENDC + ': ')
                keyring.set_password(keyring_service, key_dvc_pw, pw)
            else:
                pw = getpass.getpass('\tPlease insert your ' + bcolors.OKBLUE + 'password for ' + dvc_server + bcolors.ENDC + ': ')
                keyring.set_password(keyring_service, key_dvc_pw, pw)

        keyring.set_password(keyring_service, key_git_email, 'no-reply@dvc-cc-agent.com')
        user = input('\tPlease insert your ' + bcolors.OKBLUE + 'username for GIT (' + git_repo + ')' + bcolors.ENDC +
                     ': ')
        pw = getpass.getpass('\tPlease insert your ' + bcolors.OKBLUE + 'password for GIT (' + git_repo + ')' + bcolors.ENDC + ': ')
        keyring.set_password(keyring_service, key_git_username, user)
        keyring.set_password(keyring_service, key_git_pw, pw)







    if args.check or args.check_unsave:
        dvc_url = dvc_url.strip()
        print('# Check the keyring parameters')
        print('\tCheck GIT parameters. This will push a empty file (git_push_test.txt) to GIT.')
        user_input = input('\t\tDo you want to continue? [N, y]: ')
        if user_input.lower().strip().startswith('y') or user_input.lower().strip().startswith('j'):
            try:
                username = keyring.get_password(keyring_service, key_git_username)
                password = keyring.get_password(keyring_service, key_git_pw)

                if username is None or password is None:
                    raise ValueError('The git username is not set. Please call "dvc-cc keyring --set" to fix this.')

                push_url = 'https://' + username + ':' + urllib.parse.quote(password)+'@' +  git_repo+'/'+git_owner+'/'+git_name

                subprocess.call(['touch', 'git_push_test.txt'])
                subprocess.call(['git', 'add', 'git_push_test.txt'], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                subprocess.call(['git', 'commit', '-m','Push git_push_test.txt to test the git credentials.'], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                subprocess.check_call(['git', 'push', '-q', push_url], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                subprocess.call(['git','rm', 'git_push_test.txt'], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                subprocess.call(['git', 'commit', '-m', 'Remove git_push_test.txt from git repository.'], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                subprocess.call(['git', 'push',push_url], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                error = False
            except:
                error = True
                if args.check_unsave:
                    raise ValueError()
            if error:
                print(bcolors.FAIL+'\t\tIt seems that something has gone wrong. Maybe the credentials are wrong, '
                                   'or you need to pull and merge before you can run this command again.'+bcolors.ENDC)
            else:
                print(bcolors.OKGREEN+'\t\tGit credentials work fine.'+bcolors.ENDC)







        print()
        print('\tCheck DVC parameters. This will try to setup a SSHFS connection (sshfs_storage_folder_for_testing) to the DVC storage.')
        username = keyring.get_password(keyring_service, key_dvc_username)
        password = keyring.get_password(keyring_service, key_dvc_pw)
        try:
            subprocess.call(['mkdir', 'sshfs_storage_folder_for_testing'],stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
            child = pexpect.spawn('sshfs ' + username + '@'+dvc_url + ' sshfs_storage_folder_for_testing', echo=False)
            child.expect('password')
            child.sendline(password)
            print(child.read())
            error = False
        except:
            error = True
            if args.check_unsave:
                raise ValueError()
        if error:
            print(bcolors.FAIL+'\t\tIt seems that something has gone wrong. Maybe the DVC storage URL '
                                  'or the credentials are wrong.'+bcolors.ENDC)
        else:
            print(bcolors.OKGREEN + '\t\tDVC credentials work fine.' + bcolors.ENDC)
        try:
            subprocess.call(['fusermount','-u', 'sshfs_storage_folder_for_testing'], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
        except:
            print()
        try:
            subprocess.call(['rm','-Rf', 'sshfs_storage_folder_for_testing'], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
        except:
            print()

        print('\tCheck CC-Agency-Parameters')
        auth = (keyring.get_password(keyring_service, key_agency_username),
                keyring.get_password(keyring_service, key_agency_pw))
        print(auth)
        print(read_execution_engine() + '/batches')
        try:
            # get all experiments:
            r = requests.get(
                read_execution_engine() + '/batches',
                auth=auth
            )
            r.raise_for_status()
            error = False
        except:
            error = True
            if args.check_unsave:
                raise ValueError()
        if error:
            print(bcolors.FAIL + '\t\tIt seems that something has gone wrong. Maybe the CC Agency URL '
                                 'or the credentials are wrong.' + bcolors.ENDC)
        else:
            print(bcolors.OKGREEN + '\t\tCC-Agency credentials work fine.' + bcolors.ENDC)




    if args.delete:
        print()
        print('# All keyring parameters are deleted.')

        remove_keyring_pair(keyring_service, key_git_username)
        remove_keyring_pair(keyring_service, key_git_email)
        remove_keyring_pair(keyring_service, key_git_pw)

        remove_keyring_pair(keyring_service, key_dvc_username)
        remove_keyring_pair(keyring_service, key_dvc_pw)

        remove_keyring_pair(keyring_service, key_agency_username)
        remove_keyring_pair(keyring_service, key_agency_pw)

    print()
    print('# Print the keyring parameters')
    print('%23s : %s' % ('key_git_username', keyring.get_password(keyring_service, key_git_username)))
    print('%23s : %s' % ('key_git_email', keyring.get_password(keyring_service, key_git_email)))
    if keyring.get_password(keyring_service, key_git_pw) is not None:
        print('%23s : %s' % ('key_git_pw', '*'*len(keyring.get_password(keyring_service, key_git_pw))))
    else:
        print('%23s : %s' % ('key_git_pw', 'None'))
    print()
    print('%23s : %s' % ('key_dvc_username', keyring.get_password(keyring_service, key_dvc_username)))
    if keyring.get_password(keyring_service, key_dvc_pw) is not None:
        print('%23s : %s' % ('key_dvc_pw', '*'*len(keyring.get_password(keyring_service, key_dvc_pw))))
    else:
        print('%23s : %s' % ('key_dvc_pw', 'None'))
    print()
    print('%23s : %s' % ('key_agency_username', keyring.get_password(keyring_service, key_agency_username)))
    if keyring.get_password(keyring_service, key_agency_pw) is not None:
        print('%23s : %s' % ('key_agency_pw', '*'*len(keyring.get_password(keyring_service, key_agency_pw))))
    else:
        print('%23s : %s' % ('key_agency_pw', 'None'))










