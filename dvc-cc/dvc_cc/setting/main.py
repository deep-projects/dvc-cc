from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

import os
import yaml
import requests
import keyring
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
from argparse import ArgumentParser
import datetime
from pathlib import Path

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_main_git_directory_Path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path

def show_all():
    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if 'gpus' in settings['container']['settings']:
        if 'count' in settings['container']['settings']['gpus']:
            print('%23s : %s' % ('num-of-gpus', str(settings['container']['settings']['gpus']['count'])))
        elif 'devices' in settings['container']['settings']['gpus']:
            print('%23s : %s' % ('num-of-gpus', len(settings['container']['settings']['gpus']['devices'])))
        else:
            print('ERROR: Something is wrong with gpu configuration in the file .dvc_cc/cc_config.yml. Please delete the file and run again "dvc-cc init" to recreate the configuration file.')
    else:
        print('%23s : %s' % ('num-of-gpus' , str(None)))

    print('%23s : %s GB' % ('ram' , str(int(settings['container']['settings']['ram']/1000))))
    print('%23s : %s' % ('docker-image' , str(settings['container']['settings']['image']['url'])))
    print('%23s : %s' % ('batch-concurrency-limit' , str(settings['execution']['settings']['batchConcurrencyLimit'])))
    print('%23s : %s' % ('retry-if-failed' , str(settings['execution']['settings']['retryIfFailed'])))
    print('%23s : %s' % ('engine' , str(settings['execution']['engine'])))
    print('%23s : %s' % ('engine-url' , str(settings['execution']['settings']['access']['url'])))
    print()
    print('If you want help by reconfiguration the settings, please call "dvc-cc init".')

def setting_ram():
    parser = ArgumentParser(description='Show or set the RAM.')
    parser.add_argument('--set',help='Set the RAM in GB.', type=int, default=None)
    args = parser.parse_args()

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if args.set is None:
        print('%23s : %s GB' % ('ram' , str(int(settings['container']['settings']['ram']/1000))))
    else:
        settings['container']['settings']['ram'] = int(args.set * 1000)
        with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as outfile:
            yaml.dump(settings, outfile)

def setting_docker_image():
    parser = ArgumentParser(description='Show or set the docker image.')
    parser.add_argument('--set',help='Set the docker image.', type=str, default=None)
    args = parser.parse_args()

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if args.set is None:
        print('%23s : %s' % ('docker-image' , str(settings['container']['settings']['image']['url'])))
    else:
        settings['container']['settings']['image']['url'] = args.set
        with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as outfile:
            yaml.dump(settings, outfile)

def setting_batch_concurrency_limit():
    parser = ArgumentParser(description='Show or set the batch concurrency limit.')
    parser.add_argument('--set',help='Set the batch concurrency limit.', type=int, default=None)
    args = parser.parse_args()

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if args.set is None:
        print('%23s : %s' % ('batch-concurrency-limit' , str(settings['execution']['settings']['batchConcurrencyLimit'])))
    else:
        settings['execution']['settings']['batchConcurrencyLimit'] = args.set
        with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as outfile:
            yaml.dump(settings, outfile)

def setting_engine():
    parser = ArgumentParser(description='Show or set the engine.')
    parser.add_argument('--set',help='Set the engine.', type=str, default=None)
    args = parser.parse_args()

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if args.set is None:
        print('%23s : %s' % ('engine' , str(settings['execution']['engine'])))
    else:
        settings['execution']['engine'] = args.set
        with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as outfile:
            yaml.dump(settings, outfile)

def setting_engine_url():
    parser = ArgumentParser(description='Show or set the engine URL.')
    parser.add_argument('--set',help='Set the engine URL.', type=str, default=None)
    args = parser.parse_args()

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if args.set is None:
        print('%23s : %s' % ('engine-url' , str(settings['execution']['settings']['access']['url'])))
    else:
        settings['execution']['settings']['access']['url'] = args.set
        with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as outfile:
            yaml.dump(settings, outfile)


def setting_retry_if_failed():
    parser = ArgumentParser(description='Show or set the setting: Retry if failed.')
    parser.add_argument('--set',help='Set the setting: Retry if failed.', type=bool, default=None)
    args = parser.parse_args()

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if args.set is None:
        print('%23s : %s' % ('retry-if-failed' , str(settings['execution']['settings']['retryIfFailed'])))
    else:
        settings['execution']['settings']['retryIfFailed'] = args.set
        with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as outfile:
            yaml.dump(settings, outfile)

def setting_num_of_gpus():
    parser = ArgumentParser(description='Show or set the number of GPUs.')
    parser.add_argument('--set',help='Set the number of GPUs.', type=int, default=None)
    args = parser.parse_args()

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    if args.set is None:
        

        if 'gpus' in settings['container']['settings']:
            if 'count' in settings['container']['settings']['gpus']:
                print('%23s : %s' % ('num-of-gpus' , str(settings['container']['settings']['gpus']['count'])))
            elif 'devices' in settings['container']['settings']['gpus']:
                print('%23s : %s' % ('num-of-gpus' , len(settings['container']['settings']['gpus']['devices'])))
            else:
                print('ERROR: Something is wrong with gpu configuration in the file .dvc_cc/cc_config.yml. Please delete the file and run again "dvc-cc init" to recreate the configuration file.')
        else:
            print('%23s : %s' % ('num-of-gpus' , str(None)))
    else:
        if args.set <= 0:
            if 'gpus' in settings['container']['settings']:            
                settings['container']['settings']['gpus'].pop('count',None)
                settings['container']['settings']['gpus'].pop('devices',None)
                settings['container']['settings'].pop('gpus',None)
                settings['container']['settings'].pop('vendor',None)
        else:
            settings['container']['settings']['gpus'] = {'count':args.set, 'vendor':"nvidia"}
        with open(str(Path('.dvc_cc/cc_config.yml')), 'w') as outfile:
            yaml.dump(settings, outfile)



SCRIPT_NAME = 'dvc-cc setting'
TITLE = 'tools'
DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'
MODES = OrderedDict([
    ('all', {'main': show_all, 'description': 'Show all setting information.'}),
    ('--all', {'main': show_all, 'description': 'Show all setting information.'}),
    ('ram', {'main': setting_ram, 'description': ''}),
    ('docker-image', {'main': setting_docker_image, 'description': 'Show or set the docker image.'}),
    ('batch-concurrency-limit', {'main': setting_batch_concurrency_limit, 'description': 'Show or set the batch concurrency limit.'}),
    ('engine', {'main': setting_engine, 'description': 'Show or set the engine.'}),
    ('engine-url', {'main': setting_engine_url, 'description': 'Show or set the engine URL.'}),
    ('retry-if-failed', {'main': setting_retry_if_failed, 'description': 'Show or set the setting: Retry if failed.'}),
    ('num-of-gpus', {'main': setting_num_of_gpus, 'description': 'Show or set the number of GPUs.'}),
])


def main():
    cli_modes(SCRIPT_NAME, TITLE, DESCRIPTION, MODES, VERSION)
