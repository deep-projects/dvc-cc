from argparse import ArgumentParser
# from dvc_cc.job.main_core import *

import subprocess
import os

DESCRIPTION = 'CC JOBS run: Start all jobs at your cc server.'

def main():
    
    output = subprocess.check_output('faice exec ~/.cache/dvc_cc/created_job_description.red.yml --variables ~/.cache/dvc_cc/secrets.yml'.split())
    cc_id = output.decode().split()[-1]
    
    os.remove('~/.cache/dvc_cc/created_job_description.red.yml')

    filename = '~/.cache/dvc_cc/list_of_job_ids.csv'
    if os.path.exists(filename):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    cc_id_file = open(filename,append_write)
    if append_write == 'a':
        cc_id_file.write('\n')
    cc_id_file.write(cc_id)
    cc_id_file.close()