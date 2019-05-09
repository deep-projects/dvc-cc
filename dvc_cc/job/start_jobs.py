from argparse import ArgumentParser

import subprocess
import os

DESCRIPTION = 'This script start all jobs for that you define your red-yml-file.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()

    dvc_cc_cache_folder = os.path.expanduser('~/.cache/dvc_cc/')
    list_of_files = [f for f in os.listdir(dvc_cc_cache_folder) if f.endswith('.red.yml')]

    for f in list_of_files:
        print('### RUN faice exec ' + f)
        f = dvc_cc_cache_folder + f
        output = subprocess.check_output(('faice exec '+f).split())
        cc_id = output.decode().split()[-1]
        os.remove(f)

        filename = os.path.expanduser('~/.cache/dvc_cc/list_of_job_ids.csv')
        if os.path.exists(filename):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        cc_id_file = open(filename,append_write)
        if append_write == 'a':
            cc_id_file.write('\n')
        cc_id_file.write(cc_id)
        print(cc_id)
        cc_id_file.close()
