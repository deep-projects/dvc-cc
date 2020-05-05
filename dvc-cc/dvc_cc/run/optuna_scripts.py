def write_optuna_analyse_script(path, input_branch_name):
    analyse_script = """{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pickle\n",
    "import pandas as pd\n",
    "import optuna\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "with open('study.p','rb') as f:\n",
    "    study = pickle.load(f)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "print(study.best_value)\n",
    "print()\n",
    "print(study.best_trial)\n",
    "print()\n",
    "print(study.best_params)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = study.trials_dataframe()\n",
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df.groupby('state')['number'].count()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "optuna.visualization.plot_optimization_history(study)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "optuna.visualization.plot_parallel_coordinate(study)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# please set the parameters i.e.: params=[params_bz, params_end_model_kernels]\n",
    "#optuna.visualization.plot_slice(study, params=...)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "dvc-cc",
   "language": "python",
   "name": "dvc-cc"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}"""
    with open(path, 'w') as f:
        print(analyse_script, file=f)










def write_optuna_paramfunction_script(path, inputs):
    with open(path, 'w') as f:
        pre_text = """# !/usr/bin/env python
# coding: utf-8

convert_to_realinput = {}

"""
        print(pre_text, file=f)

        for k in inputs:
            t,v = inputs[k]
            if v.find('-') > 0:
                if t == 'float':
                    print('convert_to_realinput[\'' + k + '\'] = lambda x: x * ('+v[v.find('-') + 1:]+' - '+v[:v.find('-')]+') + '+v[:v.find('-')]+'', file=f)
                else:
                    print('convert_to_realinput[\'' + k + '\'] = lambda x: int(x  * (1 + '+v[v.find('-') + 1:]+' - '+v[:v.find('-')]+') + '+v[:v.find('-')] + ')', file=f)
            elif v.find(',') > 0:
                print(
                    'convert_to_realinput[\'' + k + '\'] = lambda x: ['+v+'][int(x * (1 + ' + str(v.count(',')) + '))]', file=f)




















def write_optuna_execution_script(path, inputs, input_branch_name, jobs, num_of_trials):

    with open(path,'w') as f:
        pre_text = """# !/usr/bin/env python
# coding: utf-8

import optuna
import pickle
import os
import subprocess
from optuna.samplers import TPESampler
from optuna.samplers import CmaEsSampler
from param_dict import *

use_CmaEsSampler = False

with open('cc_execution_file.red.yml','r') as f:
    red_yml_ori = f.read()

def create_experiment_function(start_trial_number):
    def run_experiment(trial):
        from dvc_cc.hyperopt.variable import VariableCache
        import numpy as np
        import time
        import os
        from pathlib import Path
        import subprocess
        import json

        trial_id = trial.number - start_trial_number
        #print(trial_id)
        if trial_id > 0 and trial_id < XXXJOBSXXX:
            time.sleep(trial_id*0.5)

        vc = VariableCache()
        list_of_hyperopt_files = [f for f in os.listdir(str(Path('dvc/.hyperopt'))) if f.endswith('.hyperopt')]
        for f in list_of_hyperopt_files:
            f = str(Path('dvc/.hyperopt/' + f))
            vc.register_dvccc_file(f)
"""

        pre_text = pre_text.replace('XXXJOBSXXX', str(jobs))
        pre_text = pre_text.replace('XXXTRIALSXXX', str(num_of_trials))
        pre_text = pre_text.replace('XXXBRANCHNAMEXXX', str(input_branch_name))
        print(pre_text, file=f)

        print('        values = []', file=f)
        for k in inputs:
            print('        ', file=f)
            print('        # ' + k, file=f)
            t,v = inputs[k]
            if v.find('-') > 0:
                if t == 'float':
                    print('        if use_CmaEsSampler:', file=f)
                    print('            s = trial.suggest_uniform("'+k+'", 0, 1)', file=f)
                    print('            values.append(convert_to_realinput[\''+k+'\'](s))', file=f)
                    print('        else:', file=f)
                    print('            values.append(trial.suggest_uniform("'+k+'", '+v[:v.find('-')]+','+v[v.find('-')+1:]+')'+')', file=f)
                else:
                    print('        if use_CmaEsSampler:', file=f)
                    print('            s = trial.suggest_uniform("'+k+'", 0, 1)', file=f)
                    print('            values.append(convert_to_realinput[\''+k+'\'](s))', file=f)
                    print('        else:', file=f)
                    print('            values.append(trial.suggest_int("'+k+'", '+v[:v.find('-')]+','+v[v.find('-')+1:]+')'+')', file=f)
            elif v.find(',') > 0:
                print('        if use_CmaEsSampler:', file=f)
                print('            s = trial.suggest_uniform("' + k + '", 0, 1)', file=f)
                print('            values.append(convert_to_realinput[\''+k+'\'](s))', file=f)
                print('        else:', file=f)
                print('            values.append(trial.suggest_categorical("'+k+'", ['+v+'])' +')', file=f)
            else:
                print('        values.append('+v+')', file=f)

        end_text = """
        result_branch = 'rXXXBRANCHNAMEXXX_'+str(trial.number)
        dvc_save_path = 'dvc/' + result_branch
        os.mkdir(dvc_save_path)
        vc.set_values_for_hyperopt_files(values, dvc_save_path=dvc_save_path)


        # Create RED-YMLnano
        red_yml = red_yml_ori.replace('XXXBRANCHNAMEXXX_XXXXXXXXXX', result_branch)
        with open(dvc_save_path+'/cc_execution_file.red.yml','w') as f:
            print(red_yml, file=f)


        # START RUN
        time.sleep(10)
        p = 'faice exec '+dvc_save_path+'/cc_execution_file.red.yml'# --disable-retry'
        message = subprocess.call(p.split(' '))

        result = None
        while result is None:
            time.sleep(np.random.randint(60))
            try:
                with open('metrics.json', 'r') as f:
                    metrics = json.load(f)
                metrics = {m[:m.find('__')]:metrics[m] for m in metrics}
                if result_branch in metrics:
                    result = metrics[result_branch]
            except:
                pass

        return result
    return run_experiment

def save_study(study, trial):
    #if trial.number % (XXXJOBSXXX - 1) == XXXJOBSXXX - 2:
    try:
        pickle.dump(study, open('study.p','wb'))
        print('Saved Study!')
    except:
        pass
        
def trial_log_callback_converted(study, trial):
    parameters = {p: convert_to_realinput[p](trial.params[p]) for p in trial.params}
    print("TRIAL_NO={}, PARAMS={}, VALUE={}".format(trial.number, parameters, trial.value))


if os.path.isfile('study.p'):
    print('Load existing study (study.p).')
    study = pickle.load(open('study.p','rb'))
    print()
    print(study.trials_dataframe().groupby('state')['number'].count())
    print()
    last_used_id = study.trials_dataframe()['number'].max()
    print('Last used study number (ID): ',last_used_id)
    print()
    run_experiment = create_experiment_function(last_used_id)
else:
    print('Create new study.')
    if use_CmaEsSampler: # CmaEs (no Bayesian method, but relative)
        study = optuna.create_study(direction='minimize', sampler=CmaEsSampler(warn_independent_sampling=False,independent_sampler=TPESampler()))
    else: # TPE (Bayesian method, but independent)
        study = optuna.create_study(direction='minimize', sampler=TPESampler())
    run_experiment = create_experiment_function(0)

print('Load Helper functions')
git_pusher = subprocess.Popen(['python', 'git_pusher.py'])
current_path = os.getcwd()
os.chdir(current_path[:current_path[:current_path.rfind('_')].rfind('_')]+'_MetricGetter')
metric_getter = subprocess.Popen(['python', 'get_metrics.py'])
os.chdir(current_path)

print('Start optimization')
if use_CmaEsSampler:
    study.optimize(run_experiment, n_trials=XXXTRIALSXXX, n_jobs=XXXJOBSXXX, callbacks = [save_study,trial_log_callback_converted])
else:    
    study.optimize(run_experiment, n_trials=XXXTRIALSXXX, n_jobs=XXXJOBSXXX, callbacks = [save_study])

print('Finish training, save study.')
pickle.dump(study, open('study.p','wb'))

print('Kill helper processes.')
metric_getter.kill()
git_pusher.kill()

"""
        end_text = end_text.replace('XXXJOBSXXX', str(jobs))
        end_text = end_text.replace('XXXTRIALSXXX', str(num_of_trials))
        end_text = end_text.replace('XXXBRANCHNAMEXXX', str(input_branch_name))
        print(end_text, file=f)













def write_git_pusher_script(path):
    with open(path,'w') as f:
        script = """# !/usr/bin/env python
# coding: utf-8

import git
import time

g = git.Git()
while True:
    time.sleep(0.5)
    g.add('dvc/*')
    status = g.status()
    #print(status)
    #print()
    #print()
    #print(status.find('Changes to be committed'))
    if status.find('Changes to be committed') >= 0:
        print('*', end='', flush=True)
        g.commit(m='"ADD DVC/RCC-Branches"')
        g.push()
"""
        print(script, file=f)











    write_metric_getter_script(metric_path + '/get_metrics.py', input_branch_name,
                               'loss.metric', jobstarter_path+'/metrics.json')


# parameters
#metric_path = 'loss.metric'
#input_branch = 'cc_0032_MetricTest'
#save_summary = '../learn-subjectivity/metrics.json'
def write_metric_getter_script(path, input_branch_name, metric_path, save_summary):
    with open(path,'w') as f:
        script = """# !/usr/bin/env python
# coding: utf-8

import git
import json
import os
import time


g = git.Git()

metric_path = 'XXXMETRICXXX'
input_branch = 'XXXBRANCHNAMEXXX'
save_summary = 'XXXSAVELOCATIONXXX'

metrics = {}
if not os.path.isfile(save_summary):
    with open(save_summary, 'w') as f:
        json.dump(metrics, f)
else:
    with open(save_summary, 'r') as f:
        metrics = json.load(f)

while True:
    g.pull()
    time.sleep(30)
    all_branches = [b.split('/')[-1] for b in g.branch('-a').split() if
                    b.startswith('remotes/origin/r' + input_branch)]
    new_branches = [b for b in all_branches if b not in metrics.keys()]
    for b in new_branches:
        g.checkout(b)
        with open(metric_path, 'r') as f:
            metrics[b] = float(f.read())
    with open(save_summary, 'w') as f:
        json.dump(metrics, f)
    if len(new_branches):
        print('+', end='', flush=True)

        """
        script = script.replace('XXXSAVELOCATIONXXX', str(save_summary))
        script = script.replace('XXXMETRICXXX', str(metric_path))
        script = script.replace('XXXBRANCHNAMEXXX', str(input_branch_name))
        print(script, file=f)













def get_batch_concurrency_limit():
    from pathlib import Path
    import yaml

    with open(str(Path(".dvc_cc/cc_config.yml")), 'r') as stream:
        settings = yaml.safe_load(stream)

    return settings['execution']['settings']['batchConcurrencyLimit']












def create_optuna_directories(input_branch_name, vc):
    # 1. copy current directory
    import os
    import shutil
    import subprocess

    cwd = os.getcwd()
    folder_name = os.getcwd().split('/')[-1]
    jobstarter_path = '../'+folder_name+'_'+input_branch_name.split('_')[1]+'_JobStarter'
    shutil.copytree('.', jobstarter_path)
    os.chdir(jobstarter_path)
    print('GIT CLEAN -F')
    subprocess.call('git clean -f'.split(' '))
    subprocess.call('git reset --hard'.split(' '))
    p = subprocess.Popen('rm -fR tmp_*', shell=True)
    p.communicate()
    p.wait()
    os.chdir(cwd)

    metric_path = '../' + folder_name + '_MetricGetter'
    if not os.path.exists(metric_path):
        shutil.copytree(jobstarter_path, metric_path)

    # 2. get input values
    inputs = {}
    for v in vc.list_of_all_variables:
        inp = input(str(v.varname + ' (' + v.vartype + '): '))
        inputs[v.varname] = [v.vartype, inp]

    bcl = get_batch_concurrency_limit()
    print()
    print('It is possible that ' + str(bcl) + ' (Batch Concurrency Limit) jobs can run in parallel.')
    num_of_trials = input('How many trials do you want?: ')

    # 3. Create optuna script,
    print('Write: ', jobstarter_path+'/run_optuna.py')
    write_optuna_execution_script(path=jobstarter_path+'/run_optuna.py', inputs=inputs, input_branch_name=input_branch_name, jobs=bcl, num_of_trials=num_of_trials)
    print('Write: ', jobstarter_path+'/param_dict.py')
    write_optuna_paramfunction_script(path=jobstarter_path+'/param_dict.py', inputs=inputs)

    print('Write: ', jobstarter_path + '/git_pusher.py')
    write_git_pusher_script(jobstarter_path+'/git_pusher.py')
    # 4. analyse script
    print('Write: ', jobstarter_path + '/analyse_optuna.ipynb')
    write_optuna_analyse_script(jobstarter_path+'/analyse_optuna.ipynb', input_branch_name)

    # 5. Create metrics getter script
    # TODO: The 'loss.metric' must be a variable !
    print('Write: ', jobstarter_path + '/get_metrics.py')
    write_metric_getter_script(metric_path + '/get_metrics.py', input_branch_name,
                               'loss.metric', jobstarter_path+'/metrics.json')

    print('The following files was generated: ')
    print('   - ' + jobstarter_path + '/run_optuna.py')
    print('   - ' + jobstarter_path + '/param_dict.py')
    print('   - ' + jobstarter_path+'/git_pusher.py')
    print('   - ' + jobstarter_path+'/analyse_optuna.ipynb')
    print('   - ' + metric_path + '/get_metrics.py')
    print()
    print('Please check the files. If you are satisfied, you can start the hyper optimization by calling ')
    print('python run_optuna.py from the directory '+ jobstarter_path + '. Check the jupyter notebook ')
    print('analyse_optuna.ipynb to see the hyper optimization results.')

