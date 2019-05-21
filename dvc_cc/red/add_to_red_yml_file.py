#!/usr/bin/env python3

import os
from subprocess import check_output
import configparser
from argparse import ArgumentParser

DESCRIPTION = 'This script must be run at a git repro and creates for the current batch a new job for cc. To start the job you need to "call dvc_cc job run"'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-m','--multiple_jobs', help='For each dvc file this command will create a own job. If this is not set, it will run "dvc repro -P" to run all dvc files in the same experiment and push it ones.',default=False, action='store_true')
    parser.add_argument('-r','--ram', help='The ram that you need.',default=131072)
    parser.add_argument('-T','--test', help='Run at cctest.',default=False, action='store_true')
    parser.add_argument('-g','--num_of_gpus', help='The number of gpus that you need to ',default=1)
    
    args = parser.parse_args()

    run_every_dvc_file_in_own_docker = args.multiple_jobs
    
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

    if os.path.isdir(os.path.expanduser('~/.cache')) == False:
        os.mkdir(os.path.expanduser('~/.cache'))
    if os.path.isdir(os.path.expanduser('~/.cache/dvc_cc')) == False:
        os.mkdir(os.path.expanduser('~/.cache/dvc_cc'))
####
    path = os.path.expanduser('~/.cache/dvc_cc/job_description_gpus_'+str(args.num_of_gpus)+'_ram_'+str(args.ram)+'_cctest_'+str(args.test)+'.red.yml')
    file_exist = os.path.isfile(path)

    if os.path.exists('_data.ini'):
        config = configparser.ConfigParser()
        config.read('_data.ini')
        use_external_data_dir = True
        if 'data_server' in config["'remote \"nas\"'"]:
            data_server = config["'remote \"nas\"'"]['data_server']
        else:
            print('WARNING: No data_server is set in the "_data.ini" file!')
            data_server = git_working_repository_name
        if 'data_username' in config["'remote \"nas\"'"]:
            data_username = config["'remote \"nas\"'"]['data_username']
        else:
            data_username = '{{'+ data_server + '_USERNAME}}'
        if 'data_path' in config["'remote \"nas\"'"]:
            data_path = config["'remote \"nas\"'"]['data_path']
        else:
            data_path = '{{' + data_server + '_' + git_working_repository_name + '_DATA_PATH}}'
        data_password = '{{' + data_server + '_PASSWORD}}'
        if data_server == git_working_repository_name:
            data_server = '{{' + data_server + '}}'
    else:
        use_external_data_dir = False

    print('Using external Data: ' + str(use_external_data_dir))


    if file_exist:
      with open(path) as f:
          lines = f.read().splitlines()
      if len(lines) < 3:
        file_exist = False

    dvc_files = [d for d in os.listdir() if d.endswith('.dvc') and not d.startswith('_') and d != '.dvc']

    if len(dvc_files) == 0:
        print('There exist no job to execute!')
    else:
        with open(path,"w") as f:
          print("batches:", file=f)
          
          for i in range(len(dvc_files) if run_every_dvc_file_in_own_docker else 1):
              
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

          if file_exist:
            for i in range(1,len(lines)):
              print(lines[i], file=f)
          else:
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
            print("    batchConcurrencyLimit: 9", file=f)
            print("    retryIfFailed: false", file=f)
            print("redVersion: '7'", file=f)
            print("", file=f)

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
