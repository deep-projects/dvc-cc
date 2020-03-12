import keyring
import subprocess
from argparse import ArgumentParser
import time
import getpass
import os
import uuid
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

head_index = 1
def print_head(text):
    global head_index
    print()
    print()
    print('##### ' + str(head_index) + '. ' + text)
    print('#############################################')
    print()
    head_index += 1











print_head('create a new git repository')
subprocess.call(['mkdir', args.gitprojectname])
os.chdir(args.gitprojectname)
subprocess.call(['touch', 'README.md'])
subprocess.call(['git','init'])
subprocess.call(['git','add',  'README.md'])
subprocess.call(['git','commit',  '-m', '"Initial new TEST-Project"'])

project_path_full = args.gitpath + '/' + args.gitusername + '/' + args.gitprojectname + '.git'
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


time.sleep(3)

time.sleep(1)



import pexpect

child = pexpect.spawn('dvc-cc init')
child.expect([pexpect.TIMEOUT, ".*Number of GPUs (default 0).*"])
child.sendline(str(args.number_of_gpus))

child.expect([pexpect.TIMEOUT, ".*RAM in GB.*"])
child.sendline(str(args.ram))

child.expect([pexpect.TIMEOUT, ".*Docker Image.*"])
child.sendline(args.docker_image)

child.expect([pexpect.TIMEOUT, ".*Batch concurrency limit.*"])
child.sendline(str(args.batch_concurrency_limit))

child.expect([pexpect.TIMEOUT, ".*engine.*"])
child.sendline(args.engine)

child.expect([pexpect.TIMEOUT, ".*DVC server.*"])
child.sendline(args.dvc_server)

child.expect([pexpect.TIMEOUT, ".*DVC folder.*"])
if args.dvc_folder is not None:
    child.sendline(args.dvc_folder)
else:
    child.sendline('')

child.expect([pexpect.TIMEOUT, ".*username.*"])
child.sendline(args.dvcusername)

child.expect([pexpect.TIMEOUT, ".*private key passphrase or a password for host.*"])
child.sendline(args.dvcpassword)

child.expect([pexpect.TIMEOUT, ".*s password:*"])
child.sendline(args.dvcpassword)

print(child.read())


























time.sleep(5)

print_head('create some sorce code and build a pipeline')
subprocess.call(['mkdir', 'source'])
subprocess.call(['wget', '-O','source/train.py','https://bit.ly/2krHi8E'])
subprocess.call(['dvc-cc', 'hyperopt', 'new', '-d', 'source/train.py', '-o', 'tensorboard', '-o', 'model.h5', '-m',
                 'summary.yml', '-f', 'train.dvc', 'python source/train.py --num_of_kernels {{nk:int}} --activation_function {{af:[relu,tanh,sigmoid]}}'])
subprocess.call(['git', 'add','-A'])
subprocess.call(['git', 'commit', '-m', '"build the pipeline for the first test run with DVC-CC"'])
subprocess.call(['git', 'push'])











print_head('call "dvc-cc run"')
if args.num_of_repeats_of_each_run > 1:
    p = subprocess.Popen(['dvc-cc', 'run', '-r', str(args.num_of_repeats_of_each_run), 'RunTheTest'], stdin = subprocess.PIPE,
                     bufsize = 1)
else:
    p = subprocess.Popen(['dvc-cc', 'run', 'RunTheTest'], stdin = subprocess.PIPE,
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


# do you really want to start the jobs? YEES
time.sleep(0.1)
p.stdin.write((str('y')+'\n').encode())
print('# INPUT 13: y')
p.stdin.flush()

p.communicate()
