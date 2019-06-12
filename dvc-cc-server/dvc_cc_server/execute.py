from argparse import ArgumentParser
import json
import subprocess
import os
import datetime
import time
import shutil
import tensorflow as tf

print('Start executer-python [version 0.2]')

parser = ArgumentParser()

parser.add_argument('git_authentication_json', help='')
parser.add_argument('git_path_to_working_repository', help='')
parser.add_argument('git_working_repository_owner', help='')
parser.add_argument('git_working_repository_name', help='')
parser.add_argument('git_name_of_tag', help='')
parser.add_argument('dvc_authentication_json', help='')
parser.add_argument('dvc_servername', help='')
parser.add_argument('dvc_path_to_working_repository', help='')
parser.add_argument('--data_dir', default=None, help='')
parser.add_argument('--dvc_file_to_execute', default=None, help='')


args = parser.parse_args()

with open(args.git_authentication_json) as f:
    git_authentication_json = json.load(f)
with open(args.dvc_authentication_json) as f:
    dvc_authentication_json = json.load(f)


def get_command_list_in_right_order():
    from dvc.repo import Repo as DVCRepo
    dvcrepo = DVCRepo('.')

    G = dvcrepo.pipelines()[0]

    all_nodes = []
    while len(G.nodes()) > 0: 
        next = [x for x in G.nodes() if G.out_degree(x) == 0]
        all_nodes.extend(next)
        for node in next:
            G.remove_node(node)
    all_nodes


    stages = sorted(dvcrepo.stages(), key=lambda s: all_nodes.index(s.relpath))

    commandlist = ''
    for s in stages:
        commandlist = commandlist + s.cmd + '\n'
    return commandlist

def get_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('(%Y-%m-%d %H:%M:%S)')

def collabs_text(title, text):
    pretext = '\n\n<details><summary>'+title+'</summary>\n<p>\n\n'
    posttext = '\n\n</p>\n</details>\n\n'
    return pretext+text+posttext

def write_readme():
    with open('README.md',"w") as f:
        print('## About DVC-CC')
        print('This branch was automated created with the Software DVC-CC. This Software allows you to use Data Version Control System for Machine Learning Projects (DVC) and Curious Containers (CC). DVC makes is possible to define a Machine Learning Pipeline, so that everybody can reproduce some results. Curious Containers make sure that the script is running in a docker container which was configurated to handle DVC projects.', file=f)
        print()

        print()
        print('## Rerun this branch', file = f)

        print('### Pure command line', file = f)
        commands = get_command_list_in_right_order()
        print('```', file = f)
        print(commands, file = f)
        print('```', file = f)


        print('### Using DVC', file = f)
        print('```', file = f)
        print('dvc repro -P', file = f)
        print('```', file = f)

        print('### Using CC', file = f)
        print('```', file = f)
        print('faice exec cc_execution_file.red.yml', file = f)
        print('```', file = f)

        print('## Executed System', file = f)
        print('The scipt runned on the following system:', file = f)

        # GPUs
        try:
            command = 'nvidia-smi --query-gpu=gpu_name,memory.total --format=csv'
            gpus = subprocess.check_output(command, shell=True).decode().split('\n')
            gpus_output = '```\n'
            for i in range(len(gpus)-1):
                gpu = gpus[i].split(',')
                gpus_output = gpus_output + ('%30s%22s\n'% (gpu[0], gpu[1]))
                if i == 0:
                    gpus_output = gpus_output + ('='*52) + '\n'
            gpus_output = gpus_output + '\n```'
            print(collabs_text('GPU(s)',gpus_output),file=f)
        except:
            print('\n- The system does not have a GPU.\n',file=f)


        # Other HARDWARE
        command = 'lshw -c processor,memory -short'
        sysinfo = '```\n' + subprocess.check_output(command, shell=True).decode() + '\n```'

        print(collabs_text('Other Hardware',sysinfo),file=f)

        # Software
        command = 'pip list'
        software = '```\n' +subprocess.check_output(command, shell=True).decode()+ '\n```'
        print(collabs_text('Software',software),file=f)



def get_all_dvc_files_that_are_not_needed(dvc_filenames):
    from dvc.repo import Repo
    import networkx as nx
    dvcrepo = Repo('.')
    pipelines = dvcrepo.pipelines()
    descendants_stages = dvc_filenames.copy()

    for G in pipelines:
        try:
            for dvc_filename in dvc_filenames:
                descendants_stages.extend(list(nx.descendants(G,dvc_filename)))
        except:
            continue

    all_stages = [s.relpath for s in dvcrepo.stages()]
    return [s for s in all_stages if s not in descendants_stages]

git_own_username = git_authentication_json['username']
git_own_email = git_authentication_json['email']
git_own_password = git_authentication_json['password']
git_path_to_working_repository = args.git_path_to_working_repository
git_working_repository_owner = args.git_working_repository_owner
git_working_repository_name = args.git_working_repository_name
git_name_of_tag = args.git_name_of_tag

dvc_servername = args.dvc_servername
dvc_path_to_working_repository = args.dvc_path_to_working_repository
dvc_own_username = dvc_authentication_json['username']
dvc_own_password = dvc_authentication_json['password']

data_dir = args.data_dir
if args.dvc_file_to_execute is None:
    dvc_files_to_execute = None
else:
    dvc_files_to_execute = args.dvc_file_to_execute.split(',')

if __name__ == '__main__':
    print('SET GIT GLOBAL CONFIGURATIONS   ' + get_time())
    command = 'git config --global user.email ' + git_own_email
    print('\t'+str(command))
    subprocess.check_output(command, shell=True)
    command = 'git config --global user.name ' + git_own_username
    print('\t'+str(command))
    subprocess.check_output(command, shell=True)


    print('CLONE GIT REPOSITORY   ' + get_time())
    # clone repository
    #git clone https://$2:$3@$1/$4/$5/
    git_complete_path_to_repo = 'https://' + git_own_username+":"+git_own_password+"@"+git_path_to_working_repository + '/' + git_working_repository_owner + '/'+ git_working_repository_name
    command = 'git clone --recurse-submodules ' + git_complete_path_to_repo
    print('\t' + 'git clone --recurse-submodules ' + 'https://' + git_own_username+":"+"$$$$$$$$$$$$$"+"@"+git_path_to_working_repository + '/' + git_working_repository_owner + '/'+ git_working_repository_name)
    print(subprocess.check_output(command, shell=True).decode())

    print('CD TO PATH   ' + get_time())
    print('\t chdir: '+git_working_repository_name[:-4])
    print(os.chdir(git_working_repository_name[:-4]))

    print('WRITE TO config.local FILE   ' + get_time())
    print("\n\t['remote \\\"nas\\\"']\n\turl = ssh://"+dvc_own_username+"@"+dvc_servername+dvc_path_to_working_repository+"\n\tpassword = '"+"$$$$$$$$$$$$$"+"'\n\n\t[core]\n\tremote = nas")
    filecontent = "\n['remote \\\"nas\\\"']\nurl = ssh://"+dvc_own_username+"@"+dvc_servername+dvc_path_to_working_repository+"\npassword = '"+dvc_own_password+"'\n\n[core]\nremote = nas"
    command = "echo \"" + filecontent + "\" > .dvc/config.local"
    print(subprocess.check_output(command, shell=True).decode())

    print('SWITCH GIT BRANCH   ' + get_time())
    if dvc_files_to_execute is None:
        command = 'git checkout tags/' + git_name_of_tag + ' -b b' + git_name_of_tag
    else: 
        command = 'git checkout tags/' + git_name_of_tag + ' -b b' + git_name_of_tag + '___' + str(dvc_files_to_execute).replace('/','_').replace(',','_').replace('[','').replace(']','').replace(' ','')
    print('\t'+command)
    print(subprocess.check_output(command, shell=True).decode())

    print('PULL FROM DVC   ' + get_time())
    command = 'dvc pull'
    print(subprocess.check_output(command, shell=True).decode())

    if data_dir is not None and len(data_dir) > 0 and data_dir[0] == '/':
        print('SET A LINK TO THE DATAFOLDER   ' + get_time())
        command = 'ln -s ' + data_dir + ' data'
        print('\t'+command)
        print(subprocess.check_output(command, shell=True).decode())

    if dvc_files_to_execute is not None:
        for f in dvc_files_to_execute:
            if f.endswith('.dvc'):
                print('START DVC REPRO ' + f + '   ' + get_time())
                command = 'dvc repro ' + f
                print(subprocess.check_output(command, shell=True).decode())
            else:
                print('WARNING: A file that should be execute ('+f+') does not ends with .dvc. The job is skipped!')
    else:
        print('START DVC REPRO -P   ' + get_time())
        command = 'dvc repro -P'
        print(subprocess.check_output(command, shell=True).decode())

    print('WRITE RED-YML-File TO MAIN-Directory   ' + get_time())
    #TODO HANDLE IF dvc_files_to_execute is NONE !!!
    path = '.dvc_cc/'+git_name_of_tag+'/'+args.dvc_file_to_execute.replace('/','___').replace(',','_') + '.yml'
    with open('cc_execution_file.red.yml',"w") as f:
        print("batches:", file=f)
        with open(path,"r") as r:
            print(r.read(), file=f)
        with open('.dvc_cc/cc_config.yml',"r") as r:
            print(r.read(), file=f)

    if dvc_files_to_execute is not None:
        print('REMOVE ALL DVC FILES THAT ARE NOT NEEDED   ' + get_time())
        files = get_all_dvc_files_that_are_not_needed(dvc_files_to_execute)
        for f in files:
            print('   - delete File: ' + f)
            os.remove(f)

    print('Remove ".dvc_cc"-direcotry   ' + get_time())
    shutil.rmtree('.dvc_cc')

    print('WRITE README.md')
    write_readme()

    print('GIT-ADD ' + get_time())
    command = "git add -A"
    print(subprocess.check_output(command, shell=True).decode())

    print('COMMIT AT GIT   ' + get_time())
    if dvc_files_to_execute is not None:
        command = "git commit -m 'run "+str(dvc_files_to_execute)+" in the experiment setup: " + git_name_of_tag + "'"
    else:
        command = "git commit -m 'run all dvc-files in the experiment setup: " + git_name_of_tag + "'"
    print(subprocess.check_output(command, shell=True).decode())

    print('COMMIT AT DVC   ' + get_time())
    command = "dvc commit --force"
    print(subprocess.check_output(command, shell=True).decode())

    print('PUSH TO DVC   ' + get_time())
    command = "dvc push"
    print(subprocess.check_output(command, shell=True).decode())

    print('PUSH TO GIT   ' + get_time())
    pushed_successfull = False
    num_of_tries = 1
    while pushed_successfull == False:
        try:
            if dvc_files_to_execute is None:
                name_of_new_branch = 'b' + git_name_of_tag
            else:
                name_of_new_branch = 'b' + git_name_of_tag + '___' + str(dvc_files_to_execute).replace('/','_').replace(',','_').replace('[','').replace(']','').replace(' ','')

            command = 'git push -u origin ' + name_of_new_branch + ':' + name_of_new_branch
            if num_of_tries >= 2:
                command = command + '_' + str(num_of_tries)

            print(subprocess.check_output(command, shell=True).decode())
            pushed_successfull = True
        except:
            if num_of_tries < 1000:
                # TODO: Smarter way would be to ask already used indexing.
                num_of_tries += 1
            else:
                raise ValueError('It was tried 1000 times to push to the remote. This was not possible.')







