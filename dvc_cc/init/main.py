from argparse import ArgumentParser
# from dvc_cc.job.main_core import *
from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import subprocess
import os


SCRIPT_NAME = 'dvc-cc init'
TITLE = 'tools'
DESCRIPTION = 'Scripts to initial a dvc-cc repository. It throws an exception, if the current project is not a git repository.'

from dvc.repo import Repo
from git import Repo

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-ms', '--mini-sample', help='Creates a mini sample project.', default=False,action='store_true')
    parser.add_argument('-ls', '--large-sample', help='Creates a large sample project.', default=False,action='store_true')
    parser.add_argument('-r','--ram', help='The ram that you need.',default=131072)
    parser.add_argument('-T','--test', help='Run at cctest.',default=False, action='store_true')
    parser.add_argument('-g','--num_of_gpus', help='The number of gpus that you need to ',default=1)
    args = parser.parse_args()
    
    gitrepo = Repo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    os.chdir(git_path)
    
    gitrepo = Repo('.')
    dvcrepo = Repo(".")
    
    dvcrepo.init()
    
    # create dir folder
    os.mkdir('.red')
    
    create_cc_config_file(args)
    
    #TODO: CREATE THE SAMPLE PROJECTS !!!


def create_cc_config_file(args):
    with open('.red/cc_config.yml',"w") as f:
        print("cli:", file=f)
        print("  baseCommand: [executepy]", file=f)
        print("  class: CommandLineTool", file=f)
        print("  cwlVersion: v1.0", file=f)
        print("  doc: some descriptions of the package...", file=f)
        print("  inputs:", file=f)
        print("    git_authentication_json:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 0}", file=f)
        print("      type: File", file=f)
        print("    git_path_to_working_repository:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 1}", file=f)
        print("      type: string", file=f)
        print("    git_working_repository_owner:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 2}", file=f)
        print("      type: string", file=f)
        print("    git_working_repository_name:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 3}", file=f)
        print("      type: string", file=f)
        print("    git_name_of_tag:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 4}", file=f)
        print("      type: string", file=f)
        print("    dvc_authentication_json:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 5}", file=f)
        print("      type: File", file=f)
        print("    dvc_servername:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 6}", file=f)
        print("      type: string", file=f)
        print("    dvc_path_to_working_repository:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {position: 7}", file=f)
        print("      type: string", file=f)
        print("    dvc_data_dir:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {prefix: --data_dir}", file=f)
        print("      type: Directory?", file=f)
        print("    dvc_file_to_execute:", file=f)
        print("      doc: 'SOMETHING'", file=f)
        print("      inputBinding: {prefix: --dvc_file_to_execute}", file=f)
        print("      type: string?", file=f)
    
        print("  outputs: {}", file=f)
        print("container:", file=f)
        print("  engine: nvidia-docker", file=f)
        print("  settings:", file=f)
        print("    gpus: {count: "+str(args.num_of_gpus)+"}", file=f)
        # TODO: ASK FOR THIS!
        print("    image: {url: 'dckr.f4.htw-berlin.de/annusch/dvc_repro_starter_tf2.alpha:dev', auth: {password: '{{cbmi_password}}', username: '{{cbmi_username}}'}}", file=f)
        print("    ram: "+str(args.ram), file=f)
        print("execution:", file=f)
        print("  engine: ccagency", file=f)
        print("  settings:", file=f)
        print("    access:", file=f)
        print("      auth: {password: '{{agency_password}}', username: '{{agency_username}}'}", file=f)    
        if args.test:
            print("      url: https://agency.f4.htw-berlin.de/cctest", file=f)
        else:
            print("      url: https://agency.f4.htw-berlin.de/cc", file=f)
        print("    batchConcurrencyLimit: 12", file=f)
        print("    retryIfFailed: false", file=f)
        print("redVersion: '7'", file=f)
        
        
