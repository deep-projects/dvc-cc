from argparse import ArgumentParser
import subprocess
from subprocess import check_output
import os
from dvc_cc.bcolors import *
from pathlib import Path

SCRIPT_NAME = 'dvc-cc init'
TITLE = 'tools'
DESCRIPTION = 'Scripts to initial a dvc-cc repository. It throws an exception, if the current project is not a git repository.'

from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
 
def get_main_git_directory_Path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

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

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--not-interactive', help='If this parameter is set, it will not ask the user to set the values. All values will set by default values.',default=False, action='store_true')
    args = parser.parse_args()
    gitrepo,gitowner,gitname = get_gitinformation()

    if not args.not_interactive:
        print('These settings refer to the required hardware resources in the cluster.')
        print('If you do not set an argument it will take the default values.')

        print()
        print('Please enter the number of GPUs that you want on the cluster. Hint: In the most Deep Learning '
              'scripts, you want to use 1 GPU in the docker container.')
        num_of_gpus = None
        while num_of_gpus is None:
            num_of_gpus = input(bcolors.OKBLUE+'\tNumber of GPUs'+bcolors.ENDC+' (default 0): ')
            if num_of_gpus == '':
                num_of_gpus = 0
            elif num_of_gpus.isdigit():
                num_of_gpus = int(num_of_gpus)
            else:
                print(bcolors.FAIL + '\tWarning: Did not understand your answer. Please use integer values i.e. 0,1,2,3,...' + bcolors.ENDC)
                num_of_gpus = None

        print()
        print('Please enter the RAM that you want on the cluster.')
        ram = None
        while ram is None:
            ram = input(bcolors.OKBLUE+'\tRAM in GB'+bcolors.ENDC+' (default 20): ')
            if ram == '':
                ram = 20000 # 20 GB
            elif ram.isdigit():
                ram = int(ram)*1000
            else:
                print(bcolors.FAIL + '\tWarning: Did not understand your answer. Please use integer values i.e. 10,100,...'+bcolors.ENDC)
                ram = None

        print()
        print('Please enter the Docker Image in which your script gets executed at the cluster.')
        print('   You can choose from the following:')
        print('     - "tf2", if you want to work with TensorFlow 2.0.')
        print('     - "tf1", if you want to work with TensorFlow 1.5.')
        print('     - "torch", if you want to work with PyTorch 1.2.')
        print('     - "large", if you want to work with PyTorch 1.2 or/and TensorFlow 2.0.')
        print('     - "basic", if you want install it by yourself via the Requirements.txt.')
        print('   You can also enter a URL to your own Docker Image.')
        print('   If you need more informations take a look at the following site: https://bit.ly/2mgbiVK')
        docker_image = input(bcolors.OKBLUE+'\tDocker Image'+bcolors.ENDC+' (default: "large"): ')
        if docker_image == '' or docker_image.lower() == 'large':
            docker_image = 'docker.io/deepprojects/dvc-cc_large:dev'
            docker_image_needs_credentials = False
        elif docker_image.lower() == 'tf2':
            docker_image = 'docker.io/deepprojects/dvc-cc_tensorflow:2.0'
            docker_image_needs_credentials = False
        elif docker_image.lower() == 'tf1':
            docker_image = 'docker.io/deepprojects/dvc-cc_tensorflow:1.15'
            docker_image_needs_credentials = False
        elif docker_image.lower() == 'torch':
            docker_image = 'docker.io/deepprojects/dvc-cc_pytorch:1.2'
            docker_image_needs_credentials = False
        elif docker_image.lower() == 'basic':
            docker_image = 'docker.io/deepprojects/dvc-cc_basic:10.0'
            docker_image_needs_credentials = False
        else:
            docker_image_needs_credentials = None
            while docker_image_needs_credentials is None:
                docker_image_needs_credentials = input('\tDoes this docker image needs '
                                                       ''+bcolors.OKBLUE+'credentials'+bcolors.ENDC+'? [y,n]:')
                if docker_image_needs_credentials.lower().startswith('y'):
                    docker_image_needs_credentials = True
                elif docker_image_needs_credentials.lower().startswith('n'):
                    docker_image_needs_credentials = False
                else:
                    print(bcolors.FAIL+'\tWarning: Did not understand your answer. Please use y or n.'+bcolors.ENDC)
                    docker_image_needs_credentials = None
        print('You will use the Docker Image: '+ docker_image)
        print()
        batch_concurrency_limit = None
        print('The batch concurrency limit describes how many jobs you can start in parallel.')
        print('You can lower the number to 1, if you do not want the jobs from one experiment runs in parallel.')
        while batch_concurrency_limit is None:
            batch_concurrency_limit = input(bcolors.OKBLUE+'\tBatch concurrency limit'+bcolors.ENDC+' (default 12): ')
            if batch_concurrency_limit == '':
                batch_concurrency_limit = 12
            elif batch_concurrency_limit.isdigit():
                batch_concurrency_limit = int(batch_concurrency_limit)
            else:
                print(bcolors.FAIL+'\tWarning: Did not understand your answer. Please use integer values i.e. 1,4,12,...'+bcolors.ENDC)
                batch_concurrency_limit = None

        print()
        print('The name of the engine you want to use. This describes the cluster that you want to use.')
        print('At the HTW we have the engines "dt", "cc" and "cctest".')

        engine = input('\tThe '+bcolors.OKBLUE+'engine'+bcolors.ENDC+' you want to use (default: dt): ')
        if engine == '' or engine == 'dt':
            engine = 'ccagency'
            engine_url = 'https://agency.f4.htw-berlin.de/dt'
        elif engine == 'cc':
            engine = 'ccagency'
            engine_url = 'https://agency.f4.htw-berlin.de/cc'
        elif engine == 'cctest':
            engine = 'ccagency'
            engine_url = 'https://agency.f4.htw-berlin.de/cctest'
        else:
            print('\tThis engine is unknown. Please specify the engine-url:')
            engine_url = input('The ' + bcolors.OKBLUE + 'engine-url' + bcolors.ENDC + ' you want to use: ')

        print('You will use the engine "' +engine+'" with the url "'+engine_url+'".')

        print()
        print('All large files created by your script and defined as output files by DVC are stored on the DVC server.')
        print('At the HTW we have the storage server "dt1" and "avocado01".')
        dvc_remote_server = input('\tThe remote '+bcolors.OKBLUE+'DVC server'+bcolors.ENDC+' that you want use ('
                                                                                          'default: dt1): ')
        if dvc_remote_server == '' or dvc_remote_server.lower() == 'dt' or dvc_remote_server.lower() == 'dt1':
            dvc_remote_server = 'dt1.f4.htw-berlin.de'
        elif dvc_remote_server.lower() == 'avocado' or dvc_remote_server.lower() == 'avocado01':
            dvc_remote_server = 'avocado01.f4.htw-berlin.de'
        print('You will use the following DVC server "' + dvc_remote_server + '".')


        print()
        print('Here you can enter the folder where you want to store the DVC files on the DVC Storage Server.')
        if dvc_remote_server == 'avocado01.f4.htw-berlin.de':
            dvc_folder_default_value = '/data/ldap/Data-Version-Control-Cache/' + gitrepo + '/' + gitowner + '/' + \
                                       gitname
        else:
            dvc_folder_default_value = '~/' + gitrepo + '/' + gitowner + '/' + gitname
        dvc_remote_path = input('\tThe remote '+bcolors.OKBLUE+'DVC folder'+bcolors.ENDC+' that you want use ('
                                                                                         'default: '+dvc_folder_default_value+'): ')
        if dvc_remote_path == '':
            dvc_remote_path = dvc_folder_default_value

        print()
        print('The username with that you can access the DVC storage server "'+dvc_remote_server+'".')
        dvc_remote_user = input('\tThe '+bcolors.OKBLUE+'username'+bcolors.ENDC+' for the remote DVC folder: ')
        if dvc_remote_user == '':
            dvc_remote_user = input('Do you really want to use the connection to the remote dvc folder without credentials? [n,y]')
            if not dvc_remote_user.lower().startswith('y'):
                dvc_remote_user = input('The username for the remote DVC folder: ')
        print()
    else:
        # set default values
        num_of_gpus = 0 ##
        ram = 131072
        docker_image = 'docker.io/deepprojects/dvc-cc_large:dev'
        docker_image_needs_credentials = False
        batch_concurrency_limit = 12
        engine = 'ccagency'
        engine_url = 'https://agency.f4.htw-berlin.de/dt'
        dvc_remote_server = 'dt1.f4.htw-berlin.de'
        dvc_remote_path = '~/' + gitrepo + '/' + gitowner + '/' + gitname
        dvc_remote_user = ''

    # Change the directory to the main git directory.
    #os.chdir(str(Path(get_main_git_directory_str(Path()))
    
    gitrepo = GITRepo('.')
    try:
        dvcrepo = DVCRepo('.')

        #TODO: this can be removed!?
        if not os.path.exists('.dvc'):
            dvcrepo.init()
    except:
        subprocess.call(['dvc', 'init'])
        dvcrepo = DVCRepo('.')

    if dvc_remote_path.startswith('~'):
        if dvc_remote_server == 'dt1.f4.htw-berlin.de':
            dvc_remote_path = '/mnt/md0/' + dvc_remote_user + dvc_remote_path[1:]
        else:
            dvc_remote_path = '/home/'+ dvc_remote_user + dvc_remote_path[1:]


    # set remote dvc connection
    if dvc_remote_user == '':
        subprocess.call(
            ['dvc', 'remote', 'add', '--force', '-d', 'dvc_connection', 'ssh://' + dvc_remote_server + ':' + dvc_remote_path])
        subprocess.call(['dvc', 'remote', 'modify', 'dvc_connection', 'ask_password', 'false'])
    else:
        subprocess.call(['dvc', 'remote', 'add', '--force', '-d', 'dvc_connection',
                         'ssh://' + dvc_remote_user + '@' + dvc_remote_server + ':' + dvc_remote_path])
        subprocess.call(['dvc', 'remote', 'modify', 'dvc_connection', 'ask_password', 'true'])
    # test remote connection
    subprocess.call(['dvc','push'])

    try:
        subprocess.call(['ssh', dvc_remote_user + '@' + dvc_remote_server, "mkdir -p "+dvc_remote_path+" ; chmod 774 "+dvc_remote_path+" ; setfacl -d -m u::rwX,g::rwX,o::- "+dvc_remote_path])
    except:
        print(bcolors.WARNING+'Warning: Currently acl is not installed on the server! You will maybe have problems by sharing the same remote dvc folder!'+bcolors.ENDC)


    # create the main folder of the dvc_cc software package.
    if not os.path.exists('.dvc_cc'):
        os.mkdir('.dvc_cc')
    
    # create the config file.    
    if os.path.exists(str(Path('.dvc_cc/cc_config.yml'))):
        os.remove('.dvc_cc/cc_config.yml')

    create_cc_config_file(num_of_gpus,ram,docker_image, docker_image_needs_credentials, batch_concurrency_limit, engine, engine_url)
    subprocess.call(['git', 'add', '.dvc_cc/cc_config.yml'])
    #TODO: CREATE THE SAMPLE PROJECTS !!!


def create_cc_config_file(num_of_gpus,ram,docker_image, docker_image_needs_credentials, batch_concurrency_limit, engine, engine_url):
    with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as f:
        print("cli:", file=f)
        print("  baseCommand: [dvc-cc-agent]", file=f)
        print("  class: CommandLineTool", file=f)
        print("  cwlVersion: v1.0", file=f)
        print("  doc: some descriptions of the package...", file=f)
        print("  inputs:", file=f)
        print("    git_authentication_json:", file=f)
        print("      doc: 'A path to json file which contains the git authentication. This should include the keys: username. email and password.'", file=f)
        print("      inputBinding: {position: 0}", file=f)
        print("      type: File", file=f)
        print("    git_path_to_working_repository:", file=f)
        print("      doc: 'The git working directory. With this you can specify what the main git root is.'", file=f)
        print("      inputBinding: {position: 1}", file=f)
        print("      type: string", file=f)
        print("    git_working_repository_owner:", file=f)
        print("      doc: 'The name of the owner of the git repository which you want to execute.'", file=f)
        print("      inputBinding: {position: 2}", file=f)
        print("      type: string", file=f)
        print("    git_working_repository_name:", file=f)
        print("      doc: 'The git repository name.'", file=f)
        print("      inputBinding: {position: 3}", file=f)
        print("      type: string", file=f)
        print("    git_name_of_branch:", file=f)
        print("      doc: 'The source code jumps to this here defined git tag (with git checkout) and execute dvc repro there.'", file=f)
        print("      inputBinding: {position: 4}", file=f)
        print("      type: string", file=f)
        print("    dvc_authentication_json:", file=f)
        print("      doc: 'A path to json file which contains the dvc authentication. This should include the keys: username and password.'", file=f)
        print("      inputBinding: {position: 5}", file=f)
        print("      type: File", file=f)
        print("    dvc_servername:", file=f)
        print("      doc: 'The servername of the dvc directory.'", file=f)
        print("      inputBinding: {position: 6}", file=f)
        print("      type: string", file=f)
        print("    dvc_path_to_working_repository:", file=f)
        print("      doc: 'The directory that is used for the dvc script.'", file=f)
        print("      inputBinding: {position: 7}", file=f)
        print("      type: string", file=f)
        print("    dvc_data_dir:", file=f)
        print("      doc: 'This is optional parameter. Here you can specify a sshfs folder for the \"data\" folder.'", file=f)
        print("      inputBinding: {prefix: --data_dir}", file=f)
        print("      type: Directory?", file=f)
        print("    dvc_remote_directory_sshfs:", file=f)
        print("      doc: 'A SSHFS connection to stream the output of DVC REPRO -P.'", file=f)
        print("      inputBinding: {prefix: --dvc_remote_directory_sshfs}", file=f)
        print("      type: Directory?", file=f)
        print("    dvc_file_to_execute:", file=f)
        print("      doc: 'This is optional parameter. If this parameter is given it will run \"dvc repro DVC_FILE_TO_EXECUTE\". Is this parameter is not set it will run \"dvc repro -P\"'", file=f)
        print("      inputBinding: {prefix: --dvc_file_to_execute}", file=f)
        print("      type: string?", file=f)

        print("    live_output_files:", file=f)
        print("      doc: 'Comma separated string list of files that should be included to the live output for example: tensorboard,output.json This could track a tensorboard folder and a output.json file.'", file=f)
        print("      inputBinding: {prefix: --live_output_files}", file=f)
        print("      type: string?", file=f)
        print("    live_output_update_frequence:", file=f)
        print("      doc: 'The update frequence of the live output in seconds.'", file=f)
        print("      inputBinding: {prefix: --live_output_update_frequence}", file=f)
        print("      type: int?", file=f)

        print("  outputs: {}", file=f)
        print("container:", file=f)
        print("  engine: docker", file=f)
        print("  settings:", file=f)
        if num_of_gpus > 0:
            print("    gpus:", file=f)
            print("      count: "+str(num_of_gpus), file=f)
            print("      vendor: \"nvidia\"", file=f)

        # TODO: ASK FOR THIS!
        print("    image:", file=f)
        print("      url: '"+docker_image+"'", file=f)
        if docker_image_needs_credentials:
            print("      auth:", file=f)
            print("        password: '{{docker_image_password}}'", file=f)
            print("        username: '{{docker_image_username}}'", file=f)
        print("    ram: "+str(ram), file=f)
        print("execution:", file=f)
        print("  engine: " + engine, file=f)
        print("  settings:", file=f)
        print("    access:", file=f)
        print("      auth: {password: '{{agency_password}}', username: '{{agency_username}}'}", file=f)    
        print("      url: " + engine_url, file=f)
        print("    batchConcurrencyLimit: "+str(batch_concurrency_limit), file=f)
        print("    retryIfFailed: false", file=f)
        print("redVersion: '8'", file=f)
        
        
