#!/usr/bin/env python3
import sys
import os
from subprocess import check_output
import subprocess
from argparse import ArgumentParser
import keyring
import requests
import yaml
from dvc_cc.bcolors import *
from pathlib import Path
from git import Repo as GITRepo
import json
import time
import pexpect

DESCRIPTION = 'This script saves the SSHFS connection that was created with this script and can reconnect to this ' \
              'source. You can also use the "--keyring-service str_name" parameter.'


def get_main_git_directory_Path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def get_mount_values_for_a_direcotry(path):
    mount = [m.split(' ') for m in check_output(["mount"]).decode("utf8").split('\n')]
    for m in mount:
        if len(m) == 6 and (m[2] == path or m[2] == os.getcwd() + '/' + path):
            username = m[0].split('@')[0]
            servername = m[0].split('@')[1].split(':')[0]
            path = m[0].split('@')[1].split(':')[1]
            return username, servername, path
    return None, None, None

def reconnect(keyring_service='red'):
    project_dir = get_main_git_directory_Path()
    path_to_sshfs_json = str(Path(os.path.join(project_dir, '.dvc_cc/sshfs.json')))

    if os.path.exists(path_to_sshfs_json):
        with open(path_to_sshfs_json, "r") as jsonFile:
            data = json.load(jsonFile)

        for key in data.keys():
            new_sshfs_connection([data[key]["username"] + '@' + data[key]["server"] + ':' + data[key]["remote_path"], key])

def unmount():
    project_dir = get_main_git_directory_Path()
    path_to_sshfs_json = str(Path(os.path.join(project_dir, '.dvc_cc/sshfs.json')))

    if os.path.exists(path_to_sshfs_json):
        with open(path_to_sshfs_json, "r") as jsonFile:
            data = json.load(jsonFile)

        for key in data.keys():
            if get_mount_values_for_a_direcotry(key)[0] is not None:
                print(check_output(['fusermount', '-u', key]).decode("utf8"))
                time.sleep(1)

def new_sshfs_connection(sshfs_parameters, keyring_service = 'red'):
    project_dir = get_main_git_directory_Path()

    dest = os.path.realpath(os.path.expanduser(sshfs_parameters[-1]))
    dest_rel = dest[len(project_dir) + 1:]

    # Prüfe ob Ordner existiert und lege ihn gegebenfalls neu an
    if not os.path.exists(dest):
        print(dest, os.path.exists(dest))
        os.makedirs(dest)
    # Prüfen ob eine SSHFS-Verbindung für das Ziel bereits vorliegt
    elif get_mount_values_for_a_direcotry(dest)[0] is not None:
        # Wenn Ja
        # Unmount aktuelle Verbindung
        print('Unmount last connection!')
        print(check_output(['fusermount', '-u', dest]).decode("utf8"))

    # Schreibe den Ordner in die .gitignore!
    f= open(str(Path(os.path.join(project_dir, '.gitignore'))),"a+")
    f.write('\n'+dest_rel)
    f.close()

    # call the sshfs command with the password from keyring if possible.
    username = None
    pw_keyring = None
    username_keyring = None
    if sshfs_parameters[-2].find('@') > 0:
        username, server = sshfs_parameters[-2].split('@')
        server = server.split(':')[0]
        server = server.replace('.','_').replace('-','_')

        pw_keyring = server + '_password'
        username_keyring = server + '_username'

        pw_keyring = keyring.get_password(keyring_service, pw_keyring)
        username_keyring = keyring.get_password(keyring_service, username_keyring)

    if pw_keyring is not None and username_keyring is not None and username == username_keyring:
        # see here https://stackoverflow.com/questions/28823639/how-to-automatically-input-ssh-private-key-passphrase-with-pexpect
        bash = pexpect.spawn('bash', echo=True)
        bash.sendline('echo READY')
        bash.expect_exact('READY')
        bash.sendline('sshfs ' + ' '.join(sshfs_parameters[:-1]) + ' ' + dest)
        bash.expect('password')
        bash.sendline(pw_keyring)
        bash.sendline('echo COMPLETE')
        bash.expect_exact('COMPLETE')
        bash.sendline('exit')
        bash.expect_exact(pexpect.EOF)

    else:
        print(subprocess.call(['sshfs'] + sshfs_parameters[:-1] + [dest]))
    # Finden der wichtigen Parameter
    data_username, data_server, data_path = get_mount_values_for_a_direcotry(dest)
    if data_server is None or data_server == 'null':
        raise ValueError('The connection is lost. Maybe you do not have the rights?')

    # Bei gelingen: Erstelle einen neuen Eintrag oder aktualliesiere den alten Eintrag
    path_to_sshfs_json = str(Path(os.path.join(project_dir, '.dvc_cc/sshfs.json')))
    if os.path.exists(path_to_sshfs_json):
        with open(path_to_sshfs_json, "r") as jsonFile:
            data = json.load(jsonFile)
    else:
        data = {}

    new_sshfs_connection = {
        dest_rel: {
            "server": data_server,
            "remote_path": data_path,
            "username": data_username}}

    data.update(new_sshfs_connection)



    with open(path_to_sshfs_json, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2, sort_keys=True)


def main():

    argv_tmp = sys.argv[1:]
    argv = []
    found_keyring_service = False
    keyring_service = 'red'
    for i in argv_tmp:
        if i == '--keyring-service':
            found_keyring_service = True
        elif found_keyring_service:
            keyring_service = i
            found_keyring_service = False
        else:
            argv.append(i)

    if '-h' in argv or '--help' in argv or len(argv) == 0:
        print(DESCRIPTION)
        print()
    elif len(argv) == 1 and 'reconnect'[:len(argv[0])] == argv[0]:
        print('Reconnect ALL SSHFS connections')
        reconnect(keyring_service)
    elif len(argv) == 1 and 'unmount'[:len(argv[0])] == argv[0]:
        print('UNMOUNT ALL SSHFS connections')
        unmount()
    elif len(argv) == 1:
        print('NEW SSHFS connection to data folder')
        new_sshfs_connection(argv + ['data'], keyring_service)
    else:
        print('NEW SSHFS connection')
        new_sshfs_connection(argv, keyring_service)

