from argparse import ArgumentParser
import subprocess
from subprocess import check_output
import os
from dvc_cc.bcolors import *


SCRIPT_NAME = 'dvc-cc init'
TITLE = 'tools'
DESCRIPTION = 'Scripts to initial a dvc-cc repository. It throws an exception, if the current project is not a git repository.'

from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
 
def get_main_git_directory_path():
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
        print('In the next steps you need to define some settings for your project.')
        print('If you do not set an argument it will take the default values.')

        print()
        num_of_gpus = None
        while num_of_gpus is None:
            num_of_gpus = input(bcolors.OKBLUE+'Number of GPUs'+bcolors.ENDC+' (default 0): ')
            if num_of_gpus == '':
                num_of_gpus = 0
            elif num_of_gpus.isdigit():
                num_of_gpus = int(num_of_gpus)
            else:
                print(bcolors.FAIL + '\tWarning: Did not understand your answer. Please use integer values i.e. 0,1,2,3,...' + bcolors.ENDC)
                num_of_gpus = None

        print()
        ram = None
        while ram is None:
            ram = input(bcolors.OKBLUE+'RAM in GB'+bcolors.ENDC+' (default 20): ')
            if ram == '':
                ram = 20000 # 20 GB
            elif ram.isdigit():
                ram = int(ram)*1000
            else:
                print(bcolors.FAIL + '\tWarning: Did not understand your answer. Please use integer values i.e. 10,100,...'+bcolors.ENDC)
                ram = None

        print()
        docker_image = input(bcolors.OKBLUE+'Docker Image'+bcolors.ENDC+' default (docker.io/deepprojects/dvc-cc_large-dockerfile:dev): ')
        if docker_image == '':
            docker_image = 'docker.io/deepprojects/dvc-cc_large-dockerfile:dev'
            docker_image_needs_credentials = False
        else:
            docker_image_needs_credentials = None
            while docker_image_needs_credentials is None:
                docker_image_needs_credentials = input('Does this docker image needs '+bcolors.OKBLUE+'credentials'+bcolors.ENDC+'? [y,n]:')
                if docker_image_needs_credentials.lower().startswith('y'):
                    docker_image_needs_credentials = True
                elif docker_image_needs_credentials.lower().startswith('n'):
                    docker_image_needs_credentials = False
                else:
                    print(bcolors.FAIL+'\tWarning: Did not understand your answer. Please use y or n.'+bcolors.ENDC)
                    docker_image_needs_credentials = None

        print()
        batch_concurrency_limit = None
        while batch_concurrency_limit is None:
            batch_concurrency_limit = input(bcolors.OKBLUE+'Batch concurrency limit'+bcolors.ENDC+' (default 12): ')
            if batch_concurrency_limit == '':
                batch_concurrency_limit = 12
            elif batch_concurrency_limit.isdigit():
                batch_concurrency_limit = int(batch_concurrency_limit)
            else:
                print(bcolors.FAIL+'\tWarning: Did not understand your answer. Please use integer values i.e. 1,4,12,...'+bcolors.ENDC)
                batch_concurrency_limit = None

        print()
        engine = input('The '+bcolors.OKBLUE+'engine'+bcolors.ENDC+' you want to use (default: ccagency): ')
        if engine == '':
            engine = 'ccagency'
        engine_url = input('The engine-url you want to use (default: https://agency.f4.htw-berlin.de/dt): ')
        if engine_url == '':
            engine_url = 'https://agency.f4.htw-berlin.de/dt'

        print()
        dvc_remote_server = input('The remote '+bcolors.OKBLUE+'DVC server'+bcolors.ENDC+' that you want use (default: dt1.f4.htw-berlin.de): ')
        if dvc_remote_server == '':
            dvc_remote_server = 'dt1.f4.htw-berlin.de'
        print()



        dvc_remote_path = input('The remote '+bcolors.OKBLUE+'DVC folder'+bcolors.ENDC+' that you want use (default: '+gitrepo + '/' + gitowner + '/' +gitname+'): ')
        if dvc_remote_path == '':
            dvc_remote_path = gitrepo + '/' + gitowner + '/' + gitname

        print()
        dvc_remote_user = input('The '+bcolors.OKBLUE+'username'+bcolors.ENDC+' for the remote DVC folder: ')
        if dvc_remote_user == '':
            dvc_remote_user = input('Do you really want to use the connection to the remote dvc folder without credentials? [n,y]')
            if not dvc_remote_user.lower().startswith('y'):
                dvc_remote_user = input('The username for the remote DVC folder: ')
        print()
        print()
    else:
        # set default values
        num_of_gpus = 0 ##
        ram = 131072
        docker_image = 'docker.io/deepprojects/dvc-cc_large-dockerfile:dev'
        docker_image_needs_credentials = False
        batch_concurrency_limit = 12
        engine = 'ccagency'
        engine_url = 'https://agency.f4.htw-berlin.de/dt'
        dvc_remote_server = 'dt1.f4.htw-berlin.de'
        dvc_remote_path = gitrepo + '/' + gitowner + '/' + gitname
        dvc_remote_user = ''

    # Change the directory to the main git directory.
    os.chdir(get_main_git_directory_path())
    
    gitrepo = GITRepo('.')
    try:
        dvcrepo = DVCRepo('.')

        #TODO: this can be removed!?
        if not os.path.exists('.dvc'):
            dvcrepo.init()
    except:
        subprocess.call(['dvc', 'init'])
        dvcrepo = DVCRepo('.')

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
    if os.path.exists('.dvc_cc/cc_config.yml'):
        os.remove('.dvc_cc/cc_config.yml')

    create_cc_config_file(num_of_gpus,ram,docker_image, docker_image_needs_credentials, batch_concurrency_limit, engine, engine_url)
    subprocess.call(['git', 'add', '.dvc_cc/cc_config.yml'])
    #TODO: CREATE THE SAMPLE PROJECTS !!!


def create_cc_config_file(num_of_gpus,ram,docker_image, docker_image_needs_credentials, batch_concurrency_limit, engine, engine_url):
    with open('.dvc_cc/cc_config.yml',"w") as f:
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
        
        
