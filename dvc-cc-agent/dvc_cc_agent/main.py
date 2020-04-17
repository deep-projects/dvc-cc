from argparse import ArgumentParser
import json
import subprocess
import os
import datetime
import time
import shutil
import dvc_cc_agent.version
import dvc_cc_agent.copy_output_files
from dvc_cc_agent.bcolors import bcolors

def get_command_list_in_right_order():
    from dvc.repo import Repo as DVCRepo
    dvcrepo = DVCRepo('.')

    G = dvcrepo.pipelines[0]

    all_nodes = []
    while len(G.nodes()) > 0: 
        next = [x for x in G.nodes() if G.out_degree(x) == 0]
        all_nodes.extend(next)
        for node in next:
            G.remove_node(node)

    stages = sorted(dvcrepo.stages, key=lambda s: all_nodes.index(s))

    commandlist = ''
    for s in stages:
        if s.cmd is not None:
            commandlist = commandlist + s.cmd + '\n'
    return commandlist

def get_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('(%Y-%m-%d %H:%M:%S)')

def collabs_text(title, text):
    pretext = '\n\n<details><summary>'+title+'</summary>\n<p>\n\n'
    posttext = '\n\n</p>\n</details>\n\n'
    return pretext+text+posttext


def get_all_tensorboard_folders():
    tensorboard_folders = []
    for root, dirs, files in os.walk(".", topdown=True):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for filename in files:
            if 'events.out.tfevents' in filename:
                tensorboard_folders.append(root)
    return list(set(tensorboard_folders))


def tensorboard_scalar_to_dagshub_rows(board, file=None):
    import tensorflow as tf
    from tensorboard.backend.event_processing import event_accumulator

    ea = event_accumulator.EventAccumulator(board,
                                            size_guidance={  # see below regarding this argument
                                                # event_accumulator.COMPRESSED_HISTOGRAMS: 500,
                                                # event_accumulator.IMAGES: 4,
                                                # event_accumulator.AUDIO: 4,
                                                event_accumulator.SCALARS: 0,
                                                event_accumulator.TENSORS: 0,
                                                # event_accumulator.HISTOGRAMS: 1,
                                            })
    ea.Reload()

    founded_scalars_min = {} #[min_value,min_step]
    founded_scalars_max = {} # [max_value,max_step]
    last_used_timestamp = 0

    for scalar in ea.Tags()['scalars']:
        name = '"' + board.split('/')[-1] + '_' + scalar + '"'
        founded_scalars_min[name] = None
        founded_scalars_max[name] = None
        for value in ea.Scalars(scalar):
            if not founded_scalars_min[name] or founded_scalars_min[name][0] > value.value:
                founded_scalars_min[name] = [value.value, value.step]
            if not founded_scalars_max[name] or founded_scalars_max[name][0] < value.value:
                founded_scalars_max[name] = [value.value, value.step]
            if last_used_timestamp < value.wall_time * 1000:
                last_used_timestamp = value.wall_time * 1000
            print(name + ',' + str(value.value) + ',' + str(
                int(value.wall_time * 1000)) + ','
                                               '' + str(value.step), file=file)
    for tensor in ea.Tags()['tensors']:
        name = '"' + board.split('/')[-1] + '_' + tensor + '"'
        founded_scalars_min[name] = None
        founded_scalars_max[name] = None
        for value in ea.Tensors(tensor):
            v = tf.make_ndarray(value.tensor_proto)
            if not founded_scalars_min[name] or founded_scalars_min[name][0] > v:
                founded_scalars_min[name] = [v, value.step]
            if not founded_scalars_max[name] or founded_scalars_max[name][0] < v:
                founded_scalars_max[name] = [v, value.step]
            if last_used_timestamp < value.wall_time * 1000:
                last_used_timestamp = value.wall_time * 1000
            print(name + ',' + str(v) + ',' + str(int(value.wall_time * 1000)) + ',' + str(value.step), file=file)

    for key in founded_scalars_min:
        print(key[:-1] + '_min",' + str(founded_scalars_min[key][0]) + ',' + str(int(last_used_timestamp)) + ',' + str(founded_scalars_min[key][1]), file=file)
    for key in founded_scalars_max:
        print(key[:-1] + '_max",' + str(founded_scalars_max[key][0]) + ',' + str(int(last_used_timestamp)) + ',' + str(founded_scalars_max[key][1]), file=file)


def cmd_paraneter_to_dagshub_paramfile(file=None):
    from dvc.repo import Repo as DVCRepo
    dvcrepo = DVCRepo('.')

    parameters = {}
    not_saved_parametername = None
    for pipe in dvcrepo.pipelines:
        for node in pipe.nodes:
            num_of_unnamed_parameters_found = 0
            node = node.cmd.split()
            if node[0] == 'python':
                name_of_pyfile = None
                for i in range(1, len(node)):
                    if name_of_pyfile is not None:
                        if node[i].startswith('--'):
                            not_saved_parametername = node[i][2:]
                        elif node[i].startswith('-'):
                            not_saved_parametername = node[i][1:]
                        else:
                            if not_saved_parametername is None:
                                num_of_unnamed_parameters_found += 1
                                parameters[name_of_pyfile + '_unnamed_' + str(num_of_unnamed_parameters_found)] = node[
                                    i]
                            else:
                                parameters[name_of_pyfile + '_' + not_saved_parametername] = node[i]
                                not_saved_parametername = None

                    if node[i].endswith('.py'):
                        name_of_pyfile = node[i][:-3].split('/')[-1].replace('-', '').replace('-', '')
            elif node[0] == 'papermill':
                position = None
                for i in range(1, len(node)):
                    if node[i] == '-p':
                        position = 1
                    elif position == 1:
                        not_saved_parametername = node[i]
                        position = 2
                    elif position == 2:
                        position = None
                        parameters[not_saved_parametername] = node[i]

    for k in parameters.keys():
        print(k + ': ' + str(parameters[k]), file=file)





def write_readme(dvc_status_before_execution, used_sshfs):
    with open('README.md',"a+") as f:
        print('## About DVC-CC', file=f)
        print('This branch was automated created with the tool DVC-CC. This tool connects DVC (https://dvc.org/) to CC (www.curious-containers.cc) to run your defined stages with DVC in a docker on your cloud system with CC. [More information about DVC-CC](https://github.com/deep-projects/dvc-cc)', file=f)
        print('',file=f)
        print('## DVC-Status', file=f)
        print(collabs_text('Before Execution', '```\n'+dvc_status_before_execution+'\n```'),file=f)
        dvc_status = subprocess.check_output('dvc status -c', shell=True).decode()
        print(collabs_text('After Execution', '```\n'+dvc_status+'\n```'),file=f)

        print('',file=f)
        print('## How to rerun this experiment:', file = f)
        print('The following sections describe how you can rerun the dvc stages yourself.',file=f)
        if used_sshfs:
            print('\n\n<span style="color:red">Warning: During execution a folder was included via sshfs.</span>\n\n', file = f)

        print('### Pure command line (run the experiment local)', file = f)
        commands = get_command_list_in_right_order()
        print('```', file = f)
        print(commands, file = f)
        print('```', file = f)

        print('### Using DVC (run the experiment local)', file = f)
        print('```', file = f)
        print('dvc repro -P', file = f)
        print('```', file = f)

        print('### Using CC (run the experiment on a server)', file = f)
        print('```', file = f)
        print('faice exec cc_execution_file.red.yml', file = f)
        print('```', file = f)

        print('## Executed System', file = f)
        print('The scipt ran on the following system:', file = f)

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
    pipelines = dvcrepo.pipelines
    descendants_stages = dvc_filenames.copy()

    for G in pipelines:
        try:
            for dvc_filename in dvc_filenames:
                descendants_stages.extend(list(nx.descendants(G,dvc_filename)))
        except:
            continue

    all_stages = [s.relpath for s in dvcrepo.stages]
    return [s for s in all_stages if s not in descendants_stages]

def main():

    print('Start executer-python [version '+str(dvc_cc_agent.version.VERSION)+']')
    
    parser = ArgumentParser()
    
    parser.add_argument('git_authentication_json', help='A path to json file which contains the git authentication. This should include the keys: username. email and password.')
    parser.add_argument('git_path_to_working_repository', help='The git working directory. With this you can specify what the main git root is.')
    parser.add_argument('git_working_repository_owner', help='The name of the owner of the git repository which you want to execute.')
    parser.add_argument('git_working_repository_name', help='The git repository name.')
    parser.add_argument('git_name_of_branch', help='The source code jumps to this here defined git tag (with git checkout) and execute dvc repro there. If you want to start from a tag use "tag/YOUR_TAG_NAME"')
    parser.add_argument('dvc_authentication_json', help='A path to json file which contains the dvc authentication. This should include the keys: username and password.')
    parser.add_argument('dvc_servername', help='The servername of the dvc directory.')
    parser.add_argument('dvc_path_to_working_repository', help='The directory that is used for the dvc script.')
    parser.add_argument('--dvc_remote_directory_sshfs', default=None, help='A SSHFS connection to stream the output of DVC REPRO -P.')
    parser.add_argument('--dvc_file_to_execute', default=None, help='This is optional parameter. If this parameter is given it will run \"dvc repro DVC_FILE_TO_EXECUTE\". Is this parameter is not set it will run \"dvc repro -P\"')
    parser.add_argument('--live_output_files', default=None, help='Comma separated string list of files that should be included to the live output for example: "tensorboard,output.json" This could track a tensorboard folder and a output.json file.')
    parser.add_argument('--live_output_update_frequence', default=60, help='The update frequence of the live output in seconds.')
    parser.add_argument('--sshfs_input_dest_rel_paths', nargs='+', default=None,
                        help='This is optional parameter. Here you define all relative paths to the folder that has a SSHFS connection at your project. sshfs_input_dest_rel_paths and sshfs_input_server_settings must be have the same number of elements.')
    parser.add_argument('--sshfs_input_server_settings', nargs='+', default=None,
                        help='This is optional parameter. Here you define all sshfs connections to the folder that has a SSHFS connection at your project. sshfs_input_dest_rel_paths and sshfs_input_server_settings must be have the same number of elements.')
    args = parser.parse_args()
    
    with open(args.git_authentication_json) as f:
        git_authentication_json = json.load(f)
    with open(args.dvc_authentication_json) as f:
        dvc_authentication_json = json.load(f)

    git_own_username = git_authentication_json['username']
    git_own_email = git_authentication_json['email']
    git_own_password = git_authentication_json['password']
    git_path_to_working_repository = args.git_path_to_working_repository
    git_working_repository_owner = args.git_working_repository_owner
    git_working_repository_name = args.git_working_repository_name
    git_name_of_branch = args.git_name_of_branch
    
    dvc_servername = args.dvc_servername
    dvc_path_to_working_repository = args.dvc_path_to_working_repository
    dvc_own_username = dvc_authentication_json['username']
    dvc_own_password = dvc_authentication_json['password']

    if args.dvc_file_to_execute is None:
        dvc_files_to_execute = None
    else:
        dvc_files_to_execute = args.dvc_file_to_execute.replace('\'', '').replace('\"', '').replace('[', '').replace(
            ']', '')
        dvc_files_to_execute = dvc_files_to_execute.split(',')

    print(bcolors.OKBLUE+'SET GIT GLOBAL CONFIGURATIONS   ' + get_time()+bcolors.ENDC)
    command = 'git config --global user.email ' + git_own_email
    print('\t'+str(command))
    subprocess.check_output(command, shell=True)
    command = 'git config --global user.name ' + git_own_username
    print('\t'+str(command))
    subprocess.check_output(command, shell=True)


    print(bcolors.OKBLUE+'CLONE GIT REPOSITORY   ' + get_time()+bcolors.ENDC)
    # clone repository
    #git clone https://$2:$3@$1/$4/$5/
    git_complete_path_to_repo = 'https://' + git_own_username+":"+git_own_password+"@"+git_path_to_working_repository + '/' + git_working_repository_owner + '/'+ git_working_repository_name
    command = 'git clone --recurse-submodules ' + git_complete_path_to_repo + ' repo'
    print('\t' + 'git clone --recurse-submodules ' + 'https://' + git_own_username+":"+"$$$$$$$$$$$$$"+"@"+git_path_to_working_repository + '/' + git_working_repository_owner + '/'+ git_working_repository_name)
    error_message = None
    try:
        print(subprocess.check_output(command, shell=True).decode())
    except Exception as e:
        error_message = str(e)
        error_message = error_message.replace(git_own_password, '$$$$$$$$$')
        error_message  = error_message  + '\nMaybe you used a wrong username or password?'
    if error_message is not None:
        raise Exception(error_message)

    print(bcolors.OKBLUE+'SSHFS TO THE REMOTE-DVC-Directory to save the output file' + get_time()+bcolors.ENDC)
    if args.dvc_remote_directory_sshfs is None:
        print('DO NOT USE SSHFS FOR OUTPUT!')
        sshfs_dvc_remote_directory = os.path.expanduser('~/dvc_remote_directory')
        os.makedirs(sshfs_dvc_remote_directory)
    else:
        print('USE SSHFS FOR OUTPUT!')
        sshfs_dvc_remote_directory = args.dvc_remote_directory_sshfs

    path_to_save_output = sshfs_dvc_remote_directory + '/' + git_working_repository_owner + '/' + git_working_repository_name + '/' + '_'.join(git_name_of_branch.split('_')[:3]) + '/' + '_'.join(git_name_of_branch.split('_')[3:]) + '/'
    try:
        os.makedirs(path_to_save_output)
    except:
        print('Warning: The folder already exists: ' + path_to_save_output)

    print(bcolors.OKBLUE+'CD TO PATH   ' + get_time()+bcolors.ENDC)
    print('\t chdir: repo')
    print(os.chdir('repo'))
    os.makedirs('stdout_stderr')


    #print(bcolors.OKBLUE+'PULL FROM GIT   ' + get_time()+bcolors.ENDC)
    #command = 'git pull origin ' +
    #print(subprocess.check_output(command, shell=True).decode())



    print(bcolors.OKBLUE+'SWITCH GIT BRANCH   ' + get_time()+bcolors.ENDC)
    is_tag = git_name_of_branch.startswith('tag/')
    if is_tag:
        git_name_of_branch = git_name_of_branch[4:]
    if dvc_files_to_execute is None:
        name_of_result_branch  = 'r' + git_name_of_branch
    else:
        name_of_result_branch = 'r' + git_name_of_branch + '___' + ('_'.join(dvc_files_to_execute)).replace('/',
                                                                                                     '_').replace(','
                                                                                                                  '','_').replace('[','').replace(']','').replace(' ','').replace('\'','').replace('\"','')
    if is_tag:
        command = 'git checkout tag/' + git_name_of_branch + ' -b ' + name_of_result_branch
    else:
        command = 'git checkout ' + git_name_of_branch
        print(subprocess.check_output(command, shell=True).decode())
        command = 'git checkout ' + git_name_of_branch + ' -b ' + name_of_result_branch
    print('\t'+command)
    print(subprocess.check_output(command, shell=True).decode())

    for filename in os.listdir():
        if filename.lower() == 'requirements' or  filename.lower() == 'requirements.txt':
            print(bcolors.OKBLUE+'INSTALL '+filename+' with pip.'+bcolors.ENDC)
            command = "pip install --user -r " + filename
            print(subprocess.check_output(command, shell=True).decode())

    print(bcolors.OKBLUE+'WRITE TO config.local FILE   ' + get_time()+bcolors.ENDC)
    print("\n\t['remote \\\"nas\\\"']\n\turl = ssh://"+dvc_own_username+"@"+dvc_servername+':'+dvc_path_to_working_repository+"\n\tpassword = '"+"$$$$$$$$$$$$$"+"'\n\n\t[core]\n\tremote = nas")
    could_not_create_dvcconfigfile = False
    try:
        filecontent = "\n['remote \\\"nas\\\"']\nurl = ssh://"+dvc_own_username+"@"+dvc_servername+':'+dvc_path_to_working_repository+"\npassword = '"+dvc_own_password+"'\n\n[core]\nremote = nas"
        command = "echo \"" + filecontent + "\" > .dvc/config.local"
        subprocess.check_output(command, shell=True).decode()
    except:
        could_not_create_dvcconfigfile = True
    if could_not_create_dvcconfigfile:
        ls_output = subprocess.check_output('ls -a', shell=True).decode()
        raise ValueError('It could not create the dvc config file! Maybe it is not a DVC-Repository? Or the cd command '
                         'did not worked correctly.\n Or the DVC username or password are wrong! \n Here is the ls '
                         'output:\n' + ls_output)

    print('PULL FROM DVC   ' + get_time())
    command = 'dvc pull'
    try:
        print(subprocess.check_output(command, shell=True).decode())
    except:
        print('Some files was not created. You should not be worried about this.')
    
    if args.sshfs_input_dest_rel_paths is not None and len(args.sshfs_input_dest_rel_paths) > 0:
        print(bcolors.OKBLUE+'SET LINKS FOR THE SSHFS FOLDERS   ' + get_time()+bcolors.ENDC)
        for i in range(len(args.sshfs_input_dest_rel_paths)):
            dest_rel = args.sshfs_input_dest_rel_paths[i]
            source_path = args.sshfs_input_server_settings[i]
            command = 'ln -s ' + source_path + ' ' + dest_rel
            print(bcolors.OKBLUE + '   add SSHFS connection for the folder: '+ dest_rel + bcolors.ENDC)
            print(subprocess.check_output(command, shell=True).decode())

    # check dvc status
    command = 'dvc status -c'
    dvc_status = subprocess.check_output(command, shell=True).decode()

    # start copier:
    if args.live_output_files is not None:
        #['something', 'file']
        print(bcolors.OKBLUE+'Start thread to live push output:', args.live_output_files.split(',') + bcolors.ENDC)
        dvc_cc_agent.copy_output_files.Thread(args.live_output_files.split(','),path_to_save_output, args.live_output_update_frequence)

    # start dvc repro
    if dvc_files_to_execute is not None:
        for f in dvc_files_to_execute:
            if f.endswith('.dvc'):
                print(bcolors.OKBLUE+'START DVC REPRO ' + f + '   ' + get_time()+bcolors.ENDC)
                command = 'sh '+os.path.realpath(__file__)[:-7]+'start_dvc_repro.sh ' + f + ' ' + f.replace('/','_') + ' ' + path_to_save_output
                #command = 'sh '+os.path.realpath(__file__)[:-7]+'start_dvc_repro.sh'
                message = subprocess.check_output(command.split(' ')).decode()

                if message.find('ERROR: failed to reproduce') >= 0:
                    print()
                    print('#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####')
                    print()
                    print(message[:message.find('Traceback (most recent call last):')])
                    print()
                    print('#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####')
                    print()

                    err = bcolors.FAIL+'\n#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####\n\n'
                    err = err + message[message.find('Traceback (most recent call last):'):]+bcolors.ENDC

                    raise RuntimeError(err)
                else:
                    print()
                    print('#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####')
                    print()
                    print(message)
                    print()
                    print('#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####+++++#####')
                    print()
            else:
                print('WARNING: A file that should be execute ('+f+') does not ends with .dvc. The job is skipped!')
        subprocess.call(['git','add','stdout_stderr/*'])
    else:
        # TODO USE HERE ALSO THE SCRIPT !!! Currently this will not work!
        print(bcolors.OKBLUE+'START DVC REPRO -P   ' + get_time()+bcolors.ENDC)
        command = 'dvc repro -P' + ' 2>&1 | tee ' + path_to_save_outputdvc-c + '/' + str(time.time()) + ' stdout_stderr'
        print(subprocess.check_output(command, shell=True).decode())
    
    if dvc_files_to_execute is not None:
        print(bcolors.OKBLUE+'REMOVE ALL DVC FILES THAT ARE NOT NEEDED   ' + get_time()+bcolors.ENDC)
        files = get_all_dvc_files_that_are_not_needed(dvc_files_to_execute)
        for f in files:
            print('   - delete File: ' + f)
            os.remove(f)

    print(bcolors.OKBLUE+'Remove ".dvc_cc"-direcotry   ' + get_time()+bcolors.ENDC)
    shutil.rmtree('.dvc_cc')

    print(bcolors.OKBLUE+'Remove "dvc/.hyperopt"-direcotry   ' + get_time()+bcolors.ENDC)
    if os.path.exists('dvc/.hyperopt'):
        shutil.rmtree('dvc/.hyperopt')
    
    print(bcolors.OKBLUE+'WRITE README.md'+bcolors.ENDC)
    write_readme(dvc_status, args.sshfs_input_dest_rel_paths is not None and len(args.sshfs_input_dest_rel_paths) > 0)
    
    print(bcolors.OKBLUE+'GIT-ADD ' + get_time()+bcolors.ENDC)
    command = "git add -A"
    print(subprocess.check_output(command, shell=True).decode())
    
    print(bcolors.OKBLUE+'COMMIT AT GIT   ' + get_time()+bcolors.ENDC)
    if dvc_files_to_execute is not None:
        command = "git commit -m 'run "+str(dvc_files_to_execute)+" in the experiment setup: " + git_name_of_branch + "'"
    else:
        command = "git commit -m 'run all dvc-files in the experiment setup: " + git_name_of_branch + "'"
    print(subprocess.check_output(command, shell=True).decode())
    
    print(bcolors.OKBLUE+'COMMIT AT DVC   ' + get_time()+bcolors.ENDC)
    command = "dvc commit --force"
    print(subprocess.check_output(command, shell=True).decode())





    if 'dagshub.com' in git_path_to_working_repository.lower():
        print(bcolors.OKBLUE + 'For DAGsHub.com: CREATING DAGsHub params.yml.' + get_time() + bcolors.ENDC)
        try:
            os.mkdir('.dagshub')
            print('\tcreate the .dagshub-Folder for dagshub params and dagshub metric files.')
        except:
            print('\t.dagshub-Folder already exist.')
        with open('.dagshub/params.yml', 'w') as f:
            cmd_paraneter_to_dagshub_paramfile(f)
            print('generated_projectname: ' + name_of_result_branch[4:], file=f)

        tensorboard_folders = get_all_tensorboard_folders()
        print('\tFor DAGsHub.com: Found the folling tensorboard folders: '+ str(tensorboard_folders))

        if tensorboard_folders:
            try:
                with open('.dagshub/tensorboard.csv', 'w') as f:
                    print('Name,Value,Timestamp,Step', file=f)
                    for board in tensorboard_folders:
                        tensorboard_scalar_to_dagshub_rows(board,f)
                print('\tFor DAGsHub.com: All tensorboard files are converted to dagshub files.')
            except:
                print('\tFor DAGsHub.com: Tensorboard files could not be converted to dagshub files.')

        subprocess.call(['git','add','.dagshub'])
        subprocess.call(['git', 'commit', '-m', 'Add .dagshub folder with dagshub params file and dagshub metric '
                                                'files.'])




    print(bcolors.OKBLUE+'PUSH TO DVC   ' + get_time()+bcolors.ENDC)
    pushed_successfull = False
    num_of_tries = 0
    while pushed_successfull == False:
        try:
            command = "dvc push"
            print(subprocess.check_output(command, shell=True).decode())
            pushed_successfull = True
        except:
            if num_of_tries < 5:
                # TODO: Smarter way would be to ask already used indexing.
                num_of_tries += 1
                print('Failed ' + str(num_of_tries) + ' (of max 5 tries) to push to dvc.')
            else:
                raise ValueError('It was tried 5 times to push to the remote dvc. This was not possible.')

    print(bcolors.OKBLUE+'PUSH TO GIT   ' + get_time()+bcolors.ENDC)
    pushed_successfull = False
    pushed_failed = False
    num_of_tries = 0
    while pushed_successfull == False and pushed_failed == False:
        try:
            command = 'git push --repo='+git_complete_path_to_repo+' -u origin ' + name_of_result_branch + ':' + name_of_result_branch

            if num_of_tries < 4:
                existing_branches = subprocess.check_output('git branch -a', shell=True).decode()
                num_of_already_existing_branches = len([b for b in existing_branches.split('\n') if b.find(
                    name_of_result_branch) >= 0])
                if num_of_already_existing_branches > 0:
                    command = command + '_' + str(num_of_already_existing_branches+1)
            else:
                command = command + '_' + str(time.time()).replace('.','')

            print(subprocess.check_output(command, shell=True).decode())
            pushed_successfull = True
        except:
            if num_of_tries < 5:
                num_of_tries += 1
            else:
                pushed_failed = True

    if pushed_failed:
        raise ValueError('It was tried 5 times to push to the remote. This was not possible.')







