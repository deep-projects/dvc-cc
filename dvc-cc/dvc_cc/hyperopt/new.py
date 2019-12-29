import sys
from git import Repo as GITRepo
from dvc_cc.hyperopt.variable import *
import subprocess
import uuid
import os
from dvc_cc.bcolors import *
from pathlib import Path
def get_main_git_directory_Path():
    gitrepo = GITRepo('.')
    git_path = gitrepo.common_dir.split('/.git')[0]
    return git_path


DESCRIPTION = 'Use this to define your pipeline with or without hyperparameters. It is the same use as '\
              +bcolors.OKBLUE+'dvc run --no-exec'+bcolors.ENDC + '.. If you want use ' \
               'hyperparameters you can set use i.e. {{a}} for the hyperparameter a. The script will ask you ' \
               'for the type of the hyperparameter. You can also set the type directly with i.e. {{a:int}}. ' \
               'You should use " for your command!\n' \
               'I.E.: '+bcolors.OKBLUE+'dvc-cc hyperopt new -d data.npy -o tensorboard -m summary.json "python train.py --learning-rate {{lr}} --batch-size {{bs}}"'+bcolors.ENDC


def main():

    # go to the main git directory.
    #os.chdir(str(Path(get_main_git_directory_str(Path()))

    if not os.path.exists('dvc'):
        os.mkdir('dvc')
    
    if not os.path.exists(str(Path('dvc/.hyperopt'))):
        os.mkdir(str(Path('dvc/.hyperopt')))

    if len(sys.argv) == 1:
        print(DESCRIPTION)
        exit(0)

    # get all existent variables
    vc = VariableCache()
    hyperopt_files = [f for f in os.listdir(str(Path('dvc/.hyperopt'))) if f.endswith('.hyperopt')]
    for f in hyperopt_files:
        vc.register_dvccc_file(str(Path('dvc/.hyperopt/'+f)))

    # create the dvc file
    dvc_filename = None
    output_name = None
    for i in range(len(sys.argv)-1):
        if sys.argv[i] == '-f':
            dvc_filename = 'dvc/'+sys.argv[i + 1].replace('/', '_').replace('\\\\', '_').replace(' ', '_')
            if not dvc_filename.endswith('.dvc'):
                dvc_filename = dvc_filename + '.dvc'
            sys.argv[i + 1] = dvc_filename
        elif sys.argv[i] == '-o' or sys.argv[i] == '-O' or sys.argv[i] == '-m' or sys.argv[i] == '-M':
            output_name = sys.argv[i+1]
            output_name = 'dvc/'+output_name.replace('/', '_').replace('\\\\', '_').replace('.', '_').replace(' ', '_')
            if not output_name.endswith('.dvc'):
                output_name = output_name + '.dvc'

    if dvc_filename is not None:
        subprocess.call(['dvc', 'run', '--no-exec'] + sys.argv[1:])
    elif output_name is not None:
        dvc_filename = str(Path(output_name))
        subprocess.call(['dvc', 'run', '--no-exec', '-f', dvc_filename] + sys.argv[1:])
    else:
        dvc_filename = str(Path('dvc/'+ str(uuid.uuid4())+'.dvc'))
        subprocess.call(['dvc', 'run', '--no-exec', '-f', dvc_filename] + sys.argv[1:])


    if ' '.join(sys.argv[1:]).find('{{') >= 0:
        new_hyperopt_filename = str(Path('dvc/.hyperopt/'+dvc_filename[4:-4]+'.hyperopt'))
        os.rename(dvc_filename, new_hyperopt_filename)

        try:
            vc.register_dvccc_file(new_hyperopt_filename)
        except KeyboardInterrupt as ki:
            # Delete the file if the user want to cancel the job
            os.remove(new_hyperopt_filename)
            raise ki
        vc.update_dvccc_files()

        subprocess.call(['git', 'add', str(Path('dvc/.hyperopt/*'))])
    else:
        subprocess.call(['git', 'add', str(Path(dvc_filename))])




