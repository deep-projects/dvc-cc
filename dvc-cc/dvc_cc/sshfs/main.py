#!/usr/bin/env python3
import sys
import os
from subprocess import check_output
from argparse import ArgumentParser
import keyring
import requests
import yaml
from dvc_cc.bcolors import *
from pathlib import Path
from git import Repo as GITRepo
import json

DESCRIPTION = 'This script saves the SSHFS connection that was created with this script and can reconnect to this source.'


def get_main_git_directory_Path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def get_mount_values_for_a_direcotry(path):
    mount = [m.split(' ') for m in check_output(["mount"]).decode("utf8").split('\n')]
    for m in mount:
        if len(m) == 6 and m[2] == path:
            username = m[0].split('@')[0]
            servername = m[0].split('@')[1].split(':')[0]
            path = m[0].split('@')[1].split(':')[1]
            return username, servername, path
    return None, None, None

def reconnect():
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
            print('unmount ' + str(key))
            print(check_output(['fusermount', '-u', key]).decode("utf8"))

def new_sshfs_connection(sshfs_parameters):
    project_dir = get_main_git_directory_Path()

    dest = os.path.realpath(os.path.expanduser(sshfs_parameters[-1]))
    dest_rel = dest[len(project_dir) + 1:]
    # Prüfe ob Ordner existiert und lege ihn gegebenfalls neu an
    if not os.path.exists(dest):
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

    # Führe den SSHFS-Kommando aus
    #TODO: use password from keyring or ask for it!
    print(check_output(["sshfs"] + sshfs_parameters[:-1] + [dest]).decode("utf8"))

    # Finden der wichtigen Parameter
    data_username, data_server, data_path = get_mount_values_for_a_direcotry(dest)

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
    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv or len(argv) == 0:
        print(DESCRIPTION)
        print()
    elif len(argv) == 1 and 'reconnect'[:len(argv[0])] == argv[0]:
        print('Reconnect ALL SSHFS connections')
        reconnect()
    elif len(argv) == 1 and 'unmount'[:len(argv[0])] == argv[0]:
        print('UNMOUNT ALL SSHFS connections')
        unmount()
    elif len(argv) == 1:
        print('NEW SSHFS connection to data folder')
        new_sshfs_connection(argv + ['data'])
    else:
        print('NEW SSHFS connection')
        new_sshfs_connection(argv)

