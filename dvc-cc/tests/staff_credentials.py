# This test use the Script: tests/Helper_Scripts/papermill.ipynb
# This tests works, if the keyring data are already set!

import keyring
import subprocess
from argparse import ArgumentParser
import time
import getpass
import os
import uuid
import numpy as np

parser = ArgumentParser()
parser.add_argument('--gitpath', type=str,
                    help='The path to the git repository',
                    default='https://git.tools.f4.htw-berlin.de')

parser.add_argument('gitusername', type=str,
                    help='The username to the git repository')

parser.add_argument('--gitprojectname', type=str,
                    help='The git project name. if None this is a random sequence.',
                    default=None)

parser.add_argument('--keyring-service', type=str,
                    help='The default name of the keyring service that is used. For more information visit: '
                         'https://www.curious-containers.cc/docs/red-format-protecting-credentials',
                    default='staff_test')

parser.add_argument('dvcusername',
                    help='The username of the dt1 or avaocado server.')

parser.add_argument('--num_of_repeats_of_each_run',type=int,
                    help='...',#TODO
                    default=5)


args = parser.parse_args()

args.gitpassword = getpass.getpass('Git-Password: ')
args.dvcpassword = getpass.getpass('DVC-Storage-Password: ')
args.ccpassword = getpass.getpass('CC-AGENCY-Password: ')
if args.gitprojectname == None:
    args.gitprojectname = 'TEST_' + uuid.uuid4().hex

os.chdir(os.path.expanduser('~'))

head_index = 1
def PRINT_HEAD(text):
    global head_index
    print()
    print()
    print('##### ' + str(head_index) + '. ' + text)
    print('#############################################')
    print()
    head_index += 1

PRINT_HEAD('remove local repository folder, if exists.')
if os.path.exists(args.gitprojectname):
    subprocess.call(['rm','-Rf',args.gitprojectname])
    print('Folder '+args.gitprojectname+' was removed.')
else:
    print('Nothing to do.')

PRINT_HEAD('clone existing repo or create a new one.')
project_path_full = args.gitpath + '/' + args.gitusername + '/' + args.gitprojectname + '.git'

try:
    subprocess.call(['git', 'clone', project_path_full])
    os.chdir(args.gitprojectname)
    subprocess.call(['git', 'config', '--global', 'credential.helper', 'store'])
    subprocess.call(['git', 'config', 'credential.helper', 'cache', '1800'])
    subprocess.call(['git', 'checkout', 'master'])
    print('The repo was cloned!')
except:
    subprocess.call(['mkdir', args.gitprojectname])
    os.chdir(args.gitprojectname)
    subprocess.call(['touch', 'README.md'])
    subprocess.call(['git','init'])
    subprocess.call(['git', 'config', '--global', 'credential.helper', 'store'])
    subprocess.call(['git', 'config', 'credential.helper', 'cache', '1800'])
    subprocess.call(['git','add',  'README.md'])
    subprocess.call(['git','commit',  '-m', '"Initial new TEST-Project"'])

    subprocess.call(['git','remote',  'add', 'origin', project_path_full])

    p = subprocess.Popen(['git','push','--set-upstream',
                     project_path_full,
                     'master'],
                         stdin = subprocess.PIPE, bufsize = 1)
    time.sleep(0.5)
    p.stdin.write((args.gitusername+'\n').encode())
    p.stdin.flush()
    time.sleep(0.5)
    p.stdin.write((args.gitpassword+'\n').encode())
    p.communicate()
    print('The repo was new created!')


PRINT_HEAD('switch to new branch')
branch_name = str(int(time.time())) + '_Test_Student'
p = subprocess.call(['git','checkout','-B', branch_name])
time.sleep(1)
PRINT_HEAD('TEST END')


import pexpect

child = pexpect.spawn('dvc-cc init --htw-staff')

child.expect([pexpect.TIMEOUT, ".*ldap username.*"])
child.sendline(args.dvcusername)
print('SET ldap username')

child.expect([pexpect.TIMEOUT, ".*s password:*"])
child.sendline(args.dvcpassword)
print('SET password')

print(child.read())











PRINT_HEAD('Set Keyring-Information!')
child = pexpect.spawn('dvc-cc keyring --htw-staff --set --keyring-service '+args.keyring_service)

child.expect([pexpect.TIMEOUT, ".*password for the CC-Agency.*"])
child.sendline(args.ccpassword)
print('SET password for the CC-Agency')

child.expect([pexpect.TIMEOUT, ".*password for LDAP.*"])
child.sendline(args.dvcpassword)
print('SET ldap password')

child.expect([pexpect.TIMEOUT, ".*username for GIT.*"])
child.sendline(args.gitusername)
print('SET username for GIT')
child.expect([pexpect.TIMEOUT, ".*password for GIT.*"])
child.sendline(args.gitpassword)
print('SET password for GIT')

print(child.read())







time.sleep(1)

PRINT_HEAD('create some sorce code and build a pipeline')
subprocess.call(['mkdir', 'source'])
subprocess.call(['wget', '-O','example.ipynb',
                 'https://raw.githubusercontent.com/deep-projects/dvc-cc/master/dvc-cc/tests/Helper_Scripts/papermill.ipynb'])
subprocess.call(['git', 'add','-A'])
subprocess.call(['git', 'commit', '-m', '"build the pipeline for the first test run with DVC-CC"'])
#subprocess.call(['git', 'push'])
subprocess.call(['git', 'push', '--set-upstream',
                      project_path_full,
                      branch_name])









PRINT_HEAD('call "dvc-cc run"')
if args.num_of_repeats_of_each_run > 1:
    p = subprocess.Popen(['dvc-cc', 'run', '-r', str(args.num_of_repeats_of_each_run), '-p', '--keyring-service',args.keyring_service,'student credentials'],
                         stdin = subprocess.PIPE,
                     bufsize = 1)
else:
    p = subprocess.Popen(['dvc-cc', 'run', '-p', '--keyring-service',args.keyring_service, 'student credentials'],
                         stdin = subprocess.PIPE,
                     bufsize = 1)

# The Kernelsize of the script
time.sleep(0.1)
p.stdin.write((str(64)+'\n').encode())
print('# INPUT 11: 64')
p.stdin.flush()

# the activation function, 0 = the first == relu
time.sleep(0.1)
p.stdin.write((str(0)+'\n').encode())
print('# INPUT 12: 0')
p.stdin.flush()


# the one_of parameters
for i in range(9):
    time.sleep(0.1)
    p.stdin.write((str(np.random.randint(0,3))+'\n').encode())
    print('# INPUT of one_of parameter.')
    p.stdin.flush()


# do you really want to start the jobs? YEES
time.sleep(0.1)
p.stdin.write((str('y')+'\n').encode())
print('# INPUT 13: y')
p.stdin.flush()

p.communicate()

subprocess.call(['dvc-cc','keyring','--keyring-service',args.keyring_service, '--delete'])