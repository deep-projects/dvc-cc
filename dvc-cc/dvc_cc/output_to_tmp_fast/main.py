#!/usr/bin/env python3

import os
from argparse import ArgumentParser
import re
import random
import dvc
from dvc.repo import Repo as DVCRepo
from git import Git
import subprocess
import time
import numpy as np
import getpass
from pathlib import Path

DESCRIPTION = 'This script gives you the possibility to get all output files that match some regex over different branches and saves them in a tmp folder.'


def create_output_dir(root_dir, path_to_output = None):
    """ This function creates the output dir to save the data.
    Args:
        root_dir (str): The root dir of the project. This could be repo.root_dir and this is the part where the .gitignore will be wroten to.
        path_to_output (str): default=None

    Returns:
        str: The foldername that was created. If no folder could be created, it will return None
    """
    if path_to_output is None:
        path_to_output = 'tmp_' + str(random.getrandbits(32))
    if os.path.exists(Path(path_to_output)):
        print('Error the path '+ Path(path_to_output) +' already exists. First remove this folder.')
        return None

    # Create folder and write them to .gitignore
    os.mkdir(path_to_output)
    f= open(Path(os.path.join(root_dir, '.gitignore')),"a+")
    f.write('\n'+path_to_output)
    f.close()
    subprocess.call(['git', 'add', '.gitignore'])
    subprocess.call(['git', 'commit','-m','update .gitignore'])
    subprocess.call(['git', 'push'])
    print('Create folder ' + path_to_output + ' and wrote this to .gitignore')
    return path_to_output



def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('path_to_dvc_file', type=str, default = None,
                        help='The path to the dvc file.')
    parser.add_argument('the_output_filename', type=str, default = None,
                        help='The path to the dvc file.')

    args = parser.parse_args()

    repo = DVCRepo()
    g = Git()
    starting_branch = g.branch().split('*')[1].split('\n')[0][1:]

    # Set the password only once!
    if args.download_stages:
        remote_name = repo.config.config['core']['remote']
        remote_settings = repo.config.config['remote "' + remote_name + '"']
        if 'ask_password' in remote_settings and remote_settings['ask_password']:
            remote_settings['password'] = getpass.getpass('Password for ' + remote_settings['url'] + ': ')
            remote_settings['ask_password'] = False

    if not args.no_save:
        path_to_output = create_output_dir(repo.root_dir, args.path_to_output)
        if path_to_output is None:
            exit(1)
    else:
        path_to_output = 'NONE'

    list_of_allowed_dvccc_ids = None

    if args.list_of_pos is not None:

        list_of_allowed_dvccc_ids = []
        for pos in args.list_of_pos:
            try:
                if pos.find(':') > -1:
                    pos = np.array(pos.split(':'), dtype=int)
                    list_of_allowed_dvccc_ids.extend(np.arange(*pos))
                else:
                    pos = int(pos)
                    if pos >= 0:
                        list_of_allowed_dvccc_ids.append(pos)
                    else:
                        raise ValueError('ERROR: The parameters ' + str(
                            pos) + ' from --list-of-pos must be positive.')
            except:
                raise ValueError('ERROR: The parameters ' + str(
                    pos) + ' from --list-of-pos must be an integer or a slicings. i.e.1: 12 14    i.e.2: 12:15:2')

        list_of_allowed_dvccc_ids = np.array(list_of_allowed_dvccc_ids)

    try:
        file_counter = 0
        saved_files = {}
        for branch in repo.brancher(all_branches=True):
            outs = []
            branch_names = []
            if branch.lower() != 'working tree':

                # check if this is a result branch:
                is_dvccc_result_branch = branch.startswith('rcc_')

                # search for all output files in the current branch
                is_branch_of_interest1 = args.regex_name_of_branch is None or re.match(args.regex_name_of_branch,
                                                                                       branch)
                is_branch_of_interest2 = args.exclude_regex_name_of_branch is None or not re.match(
                    args.exclude_regex_name_of_branch, branch)

                is_allowed_dvccc_id = True
                if list_of_allowed_dvccc_ids is not None and is_dvccc_result_branch:
                    if not int(branch.split('_')[1]) in list_of_allowed_dvccc_ids:
                        is_allowed_dvccc_id = False

                if is_branch_of_interest1 and is_branch_of_interest2 and is_dvccc_result_branch and is_allowed_dvccc_id:
                    print(branch)
                    g.checkout(branch)
                    #TODO: This would be nice, but its too sloow!
                    repo.checkout()

                    print('\tIt is a branch of interest!')
                    #TODO: repo.stages is very slow!
                    for stage in repo.stages():
                        for out in stage.outs:
                            valid_msg = check_out_if_its_valid(out, args.regex_name_of_file, args.exclude_regex_name_of_file, args.allow_dir)
                            print('\t\t\t',out, valid_msg)
                            if valid_msg == 'not_in_local_cache' and args.download_stages:
                                g.pull()
                                repo.pull(stage.relpath)
                                time.sleep(1)
                                valid_msg = check_out_if_its_valid(out, args.regex_name_of_file, args.exclude_regex_name_of_file, args.allow_dir)
                                print(valid_msg)
                            if valid_msg == 'valid':
                                outs.append(out)
                                branch_names.append(branch)                  
                            elif valid_msg == 'not_created' and args.no_warning == False:
                                print('Warning: A output file of interest has not yet been created. ' +
                                        '(file: ' + str(out) + '; branch: ' + branch + ')')
                            elif valid_msg == 'not_in_local_cache' and args.no_warning == False:
                                print('Warning: A output file of interest is not on the local cache. ' +
                                        '(file: ' + out.cache_path + '; branch: ' + branch +
                                        ')\n You can use this script with -d and it will download the missing stage.')

                # create a link for each output file of interest in the current branch
                for out, branch_name in zip(outs, branch_names):
                    # create the output file name
                    if args.rename_file:
                        out_filename = branch_name + '_' + str(out).replace('/','_')
                    else:
                        out_filename = str(out).replace('/','_')
                    out_filepath = os.path.join(repo.root_dir, path_to_output, out_filename) 
                    
                    file_was_already_saved = False
                    renamer_index = 2
                    file_can_be_saved = False
                    tmp_out_filepath = out_filepath

                    while not file_can_be_saved and not file_was_already_saved:
                        if tmp_out_filepath not in saved_files:
                            file_can_be_saved = True
                            out_filepath = tmp_out_filepath
                            saved_files[out_filepath] = out.checksum
                        elif saved_files[tmp_out_filepath] == out.checksum:
                            file_was_already_saved = True
                        else:
                            tmp_out_filepath = out_filepath + '_' + str(renamer_index)
                            renamer_index += 1
                    if file_can_be_saved:
                        if args.debug:
                            print(out.cache_path, ' -> ', out_filepath)
                        if args.no_save is False:
                            if out.isfile():
                                os.link(out.cache_path, out_filepath)
                            elif out.isdir():
                                os.mkdir(out_filepath)
                                for cache in out.dir_cache:
                                    dirfile_cache_path = repo.cache.local.get(cache['md5'])
                                    dirfile_outpath = os.path.join(out_filepath,cache['relpath'])
                                    os.makedirs(os.path.dirname(dirfile_outpath), exist_ok=True)
                                    os.link(dirfile_cache_path, dirfile_outpath)

                        file_counter += 1
        
        print(str(file_counter) + ' files are linked to ' + path_to_output + '.')

    # return always to the starting branch!
    finally:
        g.checkout(starting_branch)
        repo.checkout()



