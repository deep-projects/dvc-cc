#!/usr/bin/env python3

import os
from subprocess import check_output
import configparser
from argparse import ArgumentParser
from dvc.repo import Repo
from git import Repo
import numpy as np

DESCRIPTION = 'This script must be run at a git repro and creates for the current batch a new job for cc. To start the job you need to "call dvc_cc job run"'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('dvc-file', help='DVC-File-To-Create-A-Job',default=False, action='store_true')
    parser.add_argument('name', help='The name of the job.',default=None)
    args = parser.parse_args()
    
    gitrepo = Repo('.')
    git_path = gitrepo.common_dir.common_dir.split('/.git')[0]
    os.chdir(git_path)
    
    gitrepo = Repo('.')
    dvcrepo = Repo(".")

    
    out = check_output(["git", "config", "--get", "remote.origin.url"]).decode("utf8")
    _,_, gitrepo,gitowner,gitname = out.split('/')
    gitname = gitname[:gitname.find('.git')+4]

    dvc_url = []
    try:
      with open(".dvc/config","r") as fi:
        for ln in fi:
            if ln.startswith("url = "):
              dvc_url.append(ln)
    except:
      print('No .dvc/config was found.')
    try:
      with open(".dvc/config.local","r") as fi:
        for ln in fi:
            if ln.startswith("url = "):
              dvc_url.append(ln)
    except:
      print('No .dvc/config.local was found.')

    if len(dvc_url) != 1:
      if len(dvc_url) == 0:
        print('no url was found. please set the url in the .dvc/config file.')
      if len(dvc_url) > 1:
        print('multiple url was found. only one url is currently allowed')
      print('Please specifier the servername and the repository.')
      dvc_server = input("dvc_servername: ")
      dvc_path = input("dvc_path_to_working_repository: ")
    else:
      dvc_url = dvc_url[0].split('@')[1]
      dvc_server = dvc_url[:dvc_url.find('/')]
      dvc_path = dvc_url[dvc_url.find('/'):].rstrip()

    def get_name_of_branch():
        out = check_output(["git", "branch"]).decode("utf8")
        current = next(line for line in out.split("\n") if line.startswith("*"))
        return current.strip("*").strip()


    git_path_to_working_repository = gitrepo
    git_working_repository_owner = gitowner
    git_working_repository_name = gitname
    git_name_of_tag = get_name_of_branch() # TODO !!!!
    dvc_servername = dvc_server
    dvc_path_to_working_repository = dvc_path


    #TODO SEARCH FOR TAGS AND CREATE THE NEW TAG!!!!

    
    #path = os.path.expanduser('~/.cache/dvc_cc/job_description_gpus_'+str(args.num_of_gpus)+'_ram_'+str(args.ram)+'_cctest_'+str(args.test)+'.red.yml')
    
    all_tags = check_output(["git", "tag"]).decode("utf8").split('\n')[:-1]
    pre_tag = [i.split('_')[0] for i in all_tags] 
    pre_tag = [int(tag) for tag in pre_tag if tag.isdigit()] 
    new_tag = np.max(pre_tag) + 1
    new_tag = 'result_%0.4d_' % new_tag + args.name
    
    #file_exist = os.path.isfile(path)

    #TODO CHECK DATA DIR is LN OR SSHFS ; FOR THIS YOU CAN USE "mount"
    # READ THE FOLLOWING MESSAGES:
    data_server = 'avocado01.f4.htw-berlin.de'
    data_username = 'annusch'
    data_path = '/data/ldap/jonas/_testproject_DATA'
    use_external_data_dir = True

    print('Using external Data: ' + str(use_external_data_dir))


    dvc_files = [d for d in os.listdir() if d.endswith('.dvc') and not d.startswith('_') and d != '.dvc']

    if len(dvc_files) == 0:
        print('There exist no job to execute!')
    else:
        run_every_dvc_file_in_own_docker = True
        for i in range(len(dvc_files) if run_every_dvc_file_in_own_docker else 1):
            path = prepath + '_' +  dvc_files[i] + '.red.yml'
            
            with open(path,"w") as f:
                print("batches:", file=f)
                print("  - inputs:", file=f)
                print("      git_authentication_json:", file=f)
                print("        class: File", file=f)
                print("        connector:", file=f)
                print("          access: {username: '{{"+git_path_to_working_repository.replace('.', '_').replace('-','_')+"_username}}', password: '{{"+git_path_to_working_repository.replace('.', '_').replace('-','_')+"_password}}', email: '{{"+git_path_to_working_repository.replace('.', '_').replace('-','_')+"_email}}'}", file=f)
                print("          command: connector_variable_to_file", file=f)
                print("      git_path_to_working_repository: \""+git_path_to_working_repository+"\"", file=f)
                print("      git_working_repository_owner: \""+git_working_repository_owner+"\"", file=f)
                print("      git_working_repository_name: \""+git_working_repository_name+"\"", file=f)
                print("      git_name_of_tag: \""+git_name_of_tag+"\"", file=f)
                print("      dvc_authentication_json:", file=f)
                print("        class: File", file=f)
                print("        connector:", file=f)
                print("          access: {username: '{{"+dvc_servername.replace('.', '_').replace('-','_')+"_username}}', password: '{{"+dvc_servername.replace('.', '_').replace('-','_')+"_password}}'}", file=f)
                print("          command: connector_variable_to_file", file=f)
                print("      dvc_servername: \""+dvc_servername+"\"", file=f)
                print("      dvc_path_to_working_repository: \""+dvc_path_to_working_repository+"\"", file=f)
    
                if use_external_data_dir:
                    print("      dvc_data_dir:", file=f)
                    print("        class: Directory", file=f)
                    print("        connector:", file=f)
                    print("            command: \"red-connector-ssh\"", file=f)
                    print("            mount: true", file=f)
                    print("            access:", file=f)
                    print("              host: '"+data_server+'"', file=f)
                    print("              port: 22", file=f)
                    print("              auth:", file=f)
                    print("                username: '"+data_username+"'", file=f)
                    print("                password: '"+data_password+"'", file=f)
                    print("              dirName: '"+data_path+"'", file=f)
                if run_every_dvc_file_in_own_docker:
                    print("      dvc_file_to_execute: '" + dvc_files[i] + "'", file=f)
                print("    outputs: {}", file=f)


        print('Added new job: ' + git_path_to_working_repository + ' / ' + git_working_repository_owner + ' / ' + git_working_repository_name + ' ; Branch: ' + git_name_of_tag)


#
#### Improvements:
#
# - it should be possible to check if this repo already are in the yaml file and than it should not be pushed in the file!
# 
# - the BETTER solution is to use yaml see below:
#
#
# from ruamel.yaml import YAML
# yaml = YAML(typ='safe')
#
#red = {
#  'batches': [{
#     'inputs': {},
#     'outputs': {}
#   }]
#}
#
#with open(path, 'w') as f:
#  yaml.dump(red, f)
#
