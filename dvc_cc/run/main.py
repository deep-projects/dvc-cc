#!/usr/bin/env python3

import dvc_cc.run.helper as helper
from argparse import ArgumentParser
from dvc.repo import Repo
from git import Repo
import yaml
import os
from subprocess import check_output
import configparser

import numpy as np
import subprocess

DESCRIPTION = 'This script starts one or multiple dvc jobs in a docker.'

def get_main_git_directory_path():
    gitrepo = Repo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def get_gitinformation():
    # TODO: use the intern python-git for this.
    out = check_output(["git", "config", "--get", "remote.origin.url"]).decode("utf8")
    _,_, gitrepo,gitowner,gitname = out.split('/')
    gitname = gitname[:gitname.find('.git')+4]
    return gitrepo,gitowner,gitname

def create_new_tag():
    all_tags = check_output(["git", "tag"]).decode("utf8").split('\n')[:-1]
    pre_tag = [i.split('_')[1] for i in all_tags] 
    pre_tag = [int(tag) for tag in pre_tag if tag.isdigit()]
    if len(pre_tag) > 0:
        new_tag = np.max(pre_tag) + 1
    else:
        new_tag = 1
    new_tag = 'cc_%0.4d' % new_tag
    return new_tag

def get_mount_values_for_a_direcotry(path):
    mount = [m.split(' ') for m in check_output(["mount"]).decode("utf8").split('\n')]
    for m in mount:
        if len(m) == 6 and m[2] == path:
            username = m[0].split('@')[0]
            servername = m[0].split('@')[1].split(':')[0]
            path = m[0].split('@')[1].split(':')[1]
            return username, servername, path
    return None, None, None

def get_dvcurl():
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
    return dvc_url, dvc_server, dvc_path

def check_git_repo(args):
    gitrepo = Repo('.')
    if args.yes == False:
        files_are_not_commited = False        
        untracked_files = [f for f in gitrepo.untracked_files if not f.startswith('.dvc_cc')]
        if len(untracked_files) > 0:
            print('Warning: Some files are untracked: ' + str(untracked_files))
            files_are_not_commited = True
        changed_files = [f.a_path for f in gitrepo.index.diff(None) if not f.a_path.startswith('.dvc_cc')] 
        if len(changed_files) > 0:
            print('Warning: Some files are changed: ' + str(changed_files))
            files_are_not_commited = True
        if files_are_not_commited:
            user_answer = input("Do you want continue? (y/n): ")
            if user_answer.lower().strip().startswith('n'):
                print('You abort this command. You could use "git add -A", "git commit -m \'some message\'" and "git push" to commit this file.')
                exit(1)
    """ No need for this, because this script pushes the results and the not pushed commits also.
    if check_output(["git", "status"]).decode("utf8").split('\n')[1].startswith('Your branch is ahead'):
        print('Warning: You did not push the last commit. Use "git push".')
        if args.yes == False:
            user_answer = input("Do you want continue? (y/n): ")
            if user_answer.lower().strip().startswith('n'):
                print('You abort this command. Please push your commit first.')
                exit(1)
    """
    return

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('experimentname', help='The name of the experiment that should be used. This can help you to search between all files.')
    parser.add_argument('-ne','--no-exec', help='If true the experiment get defined, but it will not run at a server.', default=False, action='store_true')
    # TODO: parser.add_argument('-l','--local', help='Run the experiment locally!', default=False, action='store_true')
    # TODO: parser.add_argument('-q','--question', help='A question that you want to answer with that experiment.')
    parser.add_argument('-f','--dvc-files', help='The DVC files that you want to execute. If this is not set, it will search for all DVC files in this repository and use this. You can set multiple dvc files with: "first_file.dvc,second_file.dvc" or you can use "first_file.dvc|second_file.dvc" to run in a row the files in the same branch.')
    parser.add_argument('-y','--yes', help='If this paramer is set, than it will not ask if some files are not commited or it the remote is not on the last checkout.', default=False, action='store_true')
    parser.add_argument('-r','--num_of_repeats', help='If you want to repeat the job multiple times, than you can set this value to a larger value than 1.', default=1)
    args = parser.parse_args()
    
    project_dir = get_main_git_directory_path()

    os.chdir(project_dir)
    
    gitrepo = Repo('.')
    dvcrepo = Repo('.')

    # Check if all files are checked and pushed.
    check_git_repo(args)


    git_path,git_owner,git_name = get_gitinformation()

    dvc_url, dvc_server, dvc_path = get_dvcurl()

    new_tag = create_new_tag() + '_' + args.experimentname
    
    data_username, data_server, data_path = get_mount_values_for_a_direcotry(project_dir+'/data')
    data_password = '{{'+data_server+'_password}}'
    use_external_data_dir = data_server is not None

    if args.dvc_files is None:
        dvc_files = [[f[2:]] for f in helper.getListOfFiles(add_only_files_that_ends_with='.dvc')]
    else:
        dvc_files = []
        dvc_files_tmp = args.dvc_files.replace(' ', '').split(',')
        for dvc_files_branch in dvc_files_tmp:
            dvc_files.append([])
            dvc_files_file = dvc_files_branch.split('|')
            for i in range(len(dvc_files_file)):
                dvc_files[-1].append(dvc_files_file[i])
                if not dvc_files_file[i].endswith('.dvc'):
                    print('Error: You define with -f which dvc files you want to exec. One or more files does not ends with .dvc. Please use only DVC files.')
                    exit(1)
    print(dvc_files)
         

    if len(dvc_files) == 0:
        print('Error: There exist no job to execute! Create DVC-Files with "dvc run --no-exec ..." to define the jobs. Or check the .dvc_cc/dvc_cc_ignore file. All DVC-Files that are defined there are ignored from this script.')
    else:
        paths = []
        os.mkdir('.dvc_cc/' + new_tag)
    
        for i in range(len(dvc_files)):
            dvcfiles_to_execute = str(dvc_files[i])[1:-1].replace("'","").replace('"','').replace(' ','')
            path = '.dvc_cc/' + new_tag + '/' +  dvcfiles_to_execute.replace(",","_").replace('/','___') + '.yml'
            for i in range(args.num_of_repeats):
                paths.append(path)

            with open(path,"w") as f:
                #print("batches:", file=f)
                print("  - inputs:", file=f)
                print("      git_authentication_json:", file=f)
                print("        class: File", file=f)
                print("        connector:", file=f)
                print("          access: {username: '{{"+git_path.replace('.', '_').replace('-','_')+"_username}}', password: '{{"+git_path.replace('.', '_').replace('-','_')+"_password}}', email: '{{"+git_path.replace('.', '_').replace('-','_')+"_email}}'}", file=f)
                print("          command: connector_variable_to_file", file=f)
                print("      git_path_to_working_repository: \""+git_path+"\"", file=f)
                print("      git_working_repository_owner: \""+git_owner+"\"", file=f)
                print("      git_working_repository_name: \""+git_name+"\"", file=f)
                print("      git_name_of_tag: \""+new_tag+"\"", file=f)
                print("      dvc_authentication_json:", file=f)
                print("        class: File", file=f)
                print("        connector:", file=f)
                print("          access: {username: '{{"+dvc_server.replace('.', '_').replace('-','_')+"_username}}', password: '{{"+dvc_server.replace('.', '_').replace('-','_')+"_password}}'}", file=f)
                print("          command: connector_variable_to_file", file=f)
                print("      dvc_servername: \""+dvc_server+"\"", file=f)
                print("      dvc_path_to_working_repository: \""+dvc_path+"\"", file=f)
    
                if use_external_data_dir:
                    print("      dvc_data_dir:", file=f)
                    print("        class: Directory", file=f)
                    print("        connector:", file=f)
                    print("            command: \"red-connector-ssh\"", file=f)
                    print("            mount: true", file=f)
                    print("            access:", file=f)
                    print("              host: '"+data_server+"'", file=f)
                    print("              port: 22", file=f)
                    print("              auth:", file=f)
                    print("                username: '"+data_username+"'", file=f)
                    print("                password: '"+data_password+"'", file=f)
                    print("              dirPath: '"+data_path+"'", file=f)
                print("      dvc_file_to_execute: '" + dvcfiles_to_execute + "'", file=f)
                print("    outputs: {}", file=f)
        for path in paths:
            subprocess.call(['git', 'add', path])
        subprocess.call(['git', 'add', '.dvc_cc/cc_config.yml'])
        subprocess.call(['git', 'add', '.dvc_cc/cc_agency_experiments.yml'])
        subprocess.call(['git', 'commit', '-m', '\'Build new Pipeline: ' + path + '\''])
        subprocess.call(['git', 'tag', '-a', new_tag, '-m', '\'automatic tagging of the experiment.\''])
        print('Added new job: ' + new_tag)
        try: 
            subprocess.call(['git', 'push'])
            subprocess.call(['git', 'push', 'origin', '--tags'])
        except:
            if args.no_exec:
                print('Warning: The project could not pushed to the remote repository. You can ignore this, because you run this command with: --no-exec.')
            else:
                print('ERROR: The project could not pushed to the remote repository and could not started. Maybe you do not have access to the internet? The job is now defined, but you need to call "dvc-cc run-all-defined" to run this job.')
                args.no_exec = True
                

        # Execute the job.
        if args.no_exec == False:
            # build .red.yml.file
            with open('.dvc_cc/tmp.red.yml',"w") as f:
                print("batches:", file=f)
                for path in paths:
                    with open(path,"r") as r:
                        print(r.read(), file=f)
                with open('.dvc_cc/cc_config.yml',"r") as r:
                    print(r.read(), file=f)
            
            output = subprocess.check_output(('faice exec .dvc_cc/tmp.red.yml').split())
            cc_id = output.decode().split()[-1]
            print('The experiment ID is: ' + cc_id)
            #os.remove('.dvc_cc/tmp.red.yml')
        else:
            cc_id = None

        # write the job to the cc_agency_experiments.yml.
        if os.path.exists('.dvc_cc/cc_agency_experiments.yml'):
            with open(".dvc_cc/cc_agency_experiments.yml", 'r') as stream:
                try:
                    data = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        else:
            data = {}
        data[new_tag] = {'id': cc_id,'files': paths}
        with open('.dvc_cc/cc_agency_experiments.yml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

        subprocess.call(['git', 'add', '.dvc_cc/cc_agency_experiments.yml'])
        subprocess.call(['git', 'commit', '-m', '\'Update cc_agency_experiments.yml: ' + path + '\''])
        try:
            subprocess.call(['git', 'push'])
        except:
            if args.no_exec == False:
                print('ERROR: It could not pushed to git!')


check_output(["git", "status"]).decode("utf8")
        
# TODO: CHECK IF A COMMIT WAS DONE BEFORE A NEW PROJEC

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
