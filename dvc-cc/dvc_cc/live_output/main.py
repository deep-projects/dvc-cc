#!/usr/bin/env python3

import os
from argparse import ArgumentParser
import subprocess
import shutil
from dvc_cc.bcolors import *
from pathlib import Path

DESCRIPTION = 'With this script you can mount or unmount the live output directory.'

def get_gitinformation():
    # TODO: use the intern python-git for this.
    out = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode("utf8")
    if out.startswith('https://'):
        _,_, gitrepo,gitowner,gitname = out.split('/')
    else:
        gitrepo = out[4:out.find(':')]
        gitowner = out[out.find(':')+1:out.find('/')]
        gitname = out[out.find('/')+1:]

    gitname = gitname[:gitname.find('.git')+4]
    return gitrepo,gitowner,gitname


def get_dvcurl():
    dvc_url = []
    try:
      with open(str(Path(".dvc/config.local")), "r") as fi:
        for ln in fi:
            if ln.startswith("url = ") or ln.startswith("url="):
              dvc_url.append(ln)
    except:
        print('No .dvc/config.local was found.')
        try:
          with open(str(Path(".dvc/config")), "r") as fi:
            for ln in fi:
                if ln.startswith("url =") or ln.startswith("url="):
                  dvc_url.append(ln)
        except:
          print('No .dvc/config was found.')

    if len(dvc_url) != 1:
        if len(dvc_url) == 0:
            print(bcolors.WARNING+'Warning: no url was found. please set the url in the .dvc/config or .dvc/config.local file.'+ bcolors.ENDC)
        if len(dvc_url) > 1:
            print(bcolors.WARNING+'Warning: Multiple url was found. only one url is currently allowed'+bcolors.ENDC)
        print('\tPlease specifier the servername and the repository.')
        dvc_server = input("\tdvc_servername: ")
        dvc_path = input("\tdvc_path_to_working_repository: ")
    return dvc_url[0].split('=')[1].replace(' ', '').replace('\n', '').split('://')[1]

def main():
    parser = ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-um', '--umount', dest='umount', action='store_true', default=False,
                        help='If this parameter is set, the live output dir will be umount else it will be mount.')
    args = parser.parse_args()

    if not args.umount:
        if not os.path.exists('tmp_live_output'):
            os.mkdir('tmp_live_output')
            _, git_owner, git_name = get_gitinformation()
            dvc_url = get_dvcurl()
            command = 'sshfs ' + dvc_url + '/' +  git_owner + '/' + git_name + ' tmp_live_output'
            with open(str(Path('.gitignore')), "a+") as f:
                f.write('\ntmp_live_output')
            print(command)
            subprocess.call(command.split(' '))
        else:
            print(bcolors.WARNING+'Warning: tmp_live_output already exists. Use --umount to umount and delete this directory and try again.'+bcolors.ENDC)
    elif args.umount:
        if os.path.exists('tmp_live_output'):
            try:
                subprocess.call(['fusermount','-u','tmp_live_output'])
            finally:
                shutil.rmtree('tmp_live_output')
        else:
            print(bcolors.WARNING+'Warning: tmp_live_output does not exists.'+bcolors.ENDC)
