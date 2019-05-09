import os
from argparse import ArgumentParser

DESCRIPTION = 'This script delete all RED yml files.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()

    dvc_cc_cache_folder = os.path.expanduser('~/.cache/dvc_cc/')
    list_of_files = [f for f in os.listdir(dvc_cc_cache_folder) if f.endswith('.red.yml')]

    for f in list_of_files:
        f = dvc_cc_cache_folder + f
        os.remove(f)
    print('Deleted the .red.yml-files.')


    

