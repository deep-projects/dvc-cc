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
                    default='red')

parser.add_argument('--number-of-gpus', type=int,
                    help='The number of gpus.',
                    default=0)

parser.add_argument('--ram', type=int,
                    help='The ram that should be used here!',
                    default=20)

parser.add_argument('--docker-image', type=str,
                    help='The name of the docker image that should be used!',
                    default="large")

parser.add_argument('--batch-concurrency-limit',
                    help='...',
                    default=12)

parser.add_argument('--engine',
                    help='i.e. dt, cc, cctest',
                    default="dt")

parser.add_argument('--dvc-server',
                    help='i.e. dt1, avocado01',
                    default="dt1")

parser.add_argument('dvcusername',
                    help='The username of the dt1 or avaocado server.')

parser.add_argument('--dvc-folder',
                    help='...',#TODO
                    default=None)

parser.add_argument('--num_of_repeats_of_each_run',
                    help='...',#TODO
                    default=5)


args = parser.parse_args()

args.gitpassword = getpass.getpass('Git-Password: ')
args.dvcpassword = getpass.getpass('DVC-Storage-Password: ')
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
branch_name = str(int(time.time())) + '_Test_PapermillWithoutOutput'
p = subprocess.call(['git','checkout','-B', branch_name])
time.sleep(1)
PRINT_HEAD('TEST END')


import pexpect

child = pexpect.spawn('dvc-cc init')
child.expect([pexpect.TIMEOUT, ".*Number of GPUs.*"])
child.sendline(str(args.number_of_gpus))
print('SET num of GPUs')

child.expect([pexpect.TIMEOUT, ".*RAM in GB.*"])
child.sendline(str(args.ram))
print('SET ram')

child.expect([pexpect.TIMEOUT, ".*Docker Image.*"])
child.sendline(args.docker_image)
print('SET docker_image')

child.expect([pexpect.TIMEOUT, ".*Batch concurrency limit.*"])
child.sendline(str(args.batch_concurrency_limit))
print('SET batch_concurrency_limit')

child.expect([pexpect.TIMEOUT, ".*engine.*"])
child.sendline(args.engine)
print('SET engine')

child.expect([pexpect.TIMEOUT, ".*DVC server.*"])
child.sendline(args.dvc_server)
print('SET dvc_server')

child.expect([pexpect.TIMEOUT, ".*DVC folder.*"])
if args.dvc_folder is not None:
    child.sendline(args.dvc_folder)
else:
    child.sendline('')
print('SET dvc_folder')

child.expect([pexpect.TIMEOUT, ".*username.*"])
child.sendline(args.dvcusername)
print('SET dvcusername')

child.expect([pexpect.TIMEOUT, ".*s password:*"])
child.sendline(args.dvcpassword)
print('SET dvcpassword')

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
    p = subprocess.Popen(['dvc-cc', 'run', '-r', str(args.num_of_repeats_of_each_run), '-p','papermill without out'],
                         stdin = subprocess.PIPE,
                     bufsize = 1)
else:
    p = subprocess.Popen(['dvc-cc', 'run', '-p', 'papermill without out'], stdin = subprocess.PIPE,
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
