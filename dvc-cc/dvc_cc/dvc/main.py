import sys
import os
from dvc_cc.bcolors import *
import subprocess
from subprocess import check_output
from pathlib import Path

SCRIPT_NAME = 'dvc-cc dvc'
TITLE = 'tools'
DESCRIPTION = 'With this script you can call everything what you can do with dvc. For example you could be interested ' \
              'in calling '+ bcolors.OKBLUE+'dvc pipeline show --ascii dvc/train.dvc --commands'+ bcolors.ENDC + ', ' \
              'for visualizing the pipeline. For more information visit https://dvc.org/doc/get-started/visualize.' \
              'This script converts the dvc-cc hyperopt-files to dvc files, ' \
              'call the command, and reconvert the scripts back to hyperopt-files.'



def main():
    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv or len(argv) == 0:
        print(DESCRIPTION)
    else:
        try:
            #####################################
            # Rename the hyperopt-files to .dvc #
            #####################################
            if os.path.exists('dvc') and os.path.exists(str(Path('dvc/.hyperopt'))):
                list_of_hyperopt_files = [f for f in os.listdir(str(Path('dvc/.hyperopt'))) if f.endswith('.hyperopt')]
                for f in list_of_hyperopt_files:
                    os.rename('dvc/.hyperopt/' + f, 'dvc/' + f[:-9] + '.dvc')
            else:
                list_of_hyperopt_files = []

            subprocess.call(['dvc']+sys.argv[1:])

        finally:
            #############################
            # Rename the hyperopt-files #
            #############################
            for f in list_of_hyperopt_files:
                if os.path.exists(str(Path('dvc/'+f[:-9]+'.dvc'))):
                    os.rename(str(Path('dvc/'+f[:-9]+'.dvc')), str(Path('dvc/.hyperopt/' + f)))
                else:
                    print(bcolors.WARNING+'Warning: File ' + str(Path('dvc/'+f[:-9]+'.dvc')) + ' not found.'+bcolors.ENDC)