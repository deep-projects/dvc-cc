from argparse import ArgumentParser
# from dvc_cc.job.main_core import *
from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes
import yaml
import subprocess
import os


SCRIPT_NAME = 'dvc-cc init'
TITLE = 'tools'
DESCRIPTION = 'Scripts to initial a dvc-cc repository. It throws an exception, if the current project is not a git repository.'

from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
 
def get_main_git_directory_path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--not-interactive', help='If this parameter is set, it will not ask the user for the parameters. All parameters are set to default values.',default=False, action='store_true')
    args = parser.parse_args()

    if not args.not_interactive:
        print('Define the settings for this project:')

        num_of_gpus = None
        while num_of_gpus is None:
            num_of_gpus = input('Number of GPUs (default 0): ')
            if num_of_gpus == '':
                num_of_gpus = 0
            elif num_of_gpus.isdigit():
                num_of_gpus = int(num_of_gpus)
            else:
                print('Warning: Did not understand your answer. Please use integer values i.e. 0,1,2,3,...')
                num_of_gpus = None

        ram = None
        while ram is None:
            ram = input('RAM in GB (default 100): ')
            if ram == '':
                ram = 100
            elif ram.isdigit():
                ram = int(ram)
            else:
                print('Warning: Did not understand your answer. Please use integer values i.e. 10,100,...')
                ram = None
        docker_image = input('docker_image default (dckr.f4.htw-berlin.de/deepprojects/dvc_repro_starter_tf2.alpha:dev): ')
        # TODO check the input string...
        if docker_image == '':
            docker_image = 'dckr.f4.htw-berlin.de/deepprojects/dvc_repro_starter_tf2.alpha:dev'
            docker_image_needs_credentials = False
        else:
            docker_image_needs_credentials = None
            while docker_image_needs_credentials is None:
                docker_image_needs_credentials = input('Does this docker image needs credentials? [y,n]:')
                if docker_image_needs_credentials.lower().startswith('y'):
                    docker_image_needs_credentials = True
                elif docker_image_needs_credentials.lower().startswith('n'):
                    docker_image_needs_credentials = False
                else:
                    print('Warning: Did not understand your answer. Please use y or n.')
                    docker_image_needs_credentials = None

        batch_concurrency_limit = None
        while batch_concurrency_limit is None:
            batch_concurrency_limit = input('Batch concurrency limit (default 12): ')
            if batch_concurrency_limit == '':
                batch_concurrency_limit = 12
            elif batch_concurrency_limit.isdigit():
                batch_concurrency_limit = int(number_of_gpus)
            else:
                print('Warning: Did not understand your answer. Please use integer values i.e. 1,4,12,...')
                batch_concurrency_limit = None

        engine = input('The engine you want to use (default: ccagency)')
        if engine == '':
            engine = 'ccagency'
        engine_url = input('The engine-url you want to use (default: https://agency.f4.htw-berlin.de/cc)')
        if engine_url == '':
            engine_url = 'https://agency.f4.htw-berlin.de/cc'

    else:
        # set default values
        num_of_gpus = 0 ##
        ram = 131072
        docker_image = 'dckr.f4.htw-berlin.de/deepprojects/dvc_repro_starter_tf2.alpha:dev'
        docker_image_needs_credentials = False
        batch_concurrency_limit = 12
        engine = 'ccagency'
        engine_url = 'https://agency.f4.htw-berlin.de/cc'


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
    #TODO: Allow interactive sessions.
    #TODO: Allow more parameters to set in the config.
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
        print("    git_name_of_tag:", file=f)
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
        print("    dvc_file_to_execute:", file=f)
        print("      doc: 'This is optional parameter. If this parameter is given it will run \"dvc repro DVC_FILE_TO_EXECUTE\". Is this parameter is not set it will run \"dvc repro -P\"'", file=f)
        print("      inputBinding: {prefix: --dvc_file_to_execute}", file=f)
        print("      type: string?", file=f)
    
        print("  outputs: {}", file=f)
        print("container:", file=f)
        if num_of_gpus == 0:
            print("  engine: docker", file=f)
        else:
            print("  engine: nvidia-docker", file=f)
        print("  settings:", file=f)
        if num_of_gpus > 0:
            print("    gpus: {count: "+str(num_of_gpus)+"}", file=f)
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
        print("redVersion: '7'", file=f)
        
        
