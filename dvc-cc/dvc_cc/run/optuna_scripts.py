def write_optuna_execution_script(path, inputs, input_branch_name):
    with open(path,'w') as f:

        print('# !/usr/bin/env python', file=f)
        print('# coding: utf-8', file=f)
        print('', file=f)

        print('def run_experiment(trial):', file=f)
        print('    from dvc_cc.hyperopt.variable import VariableCache', file=f)
        print('    import numpy as np', file=f)
        print('    import time', file=f)
        print('    vc = VariableCache()', file=f)
        print("    list_of_hyperopt_files = [f for f in os.listdir(str(Path('dvc/.hyperopt'))) if f.endswith('.hyperopt')]", file=f)
        print('    for f in list_of_hyperopt_files:', file=f)
        print("        f = str(Path('dvc/.hyperopt/' + f))", file=f)
        print('        vc.register_dvccc_file(f)', file=f)
        print('', file=f)

        print('    values = []', file=f)
        for k in inputs:
            t,v = inputs[k]
            if v.find('-') > 0:
                if t == 'float':
                    print('    values.append(trial.suggest_uniform("'+k+'", '+v[:v.find('-')]+','+v[v.find('-')+1:]+')'+')', file=f)
                else:
                    print('    values.append(trial.suggest_int("'+k+'", '+v[:v.find('-')]+','+v[v.find('-')+1:]+')'+')', file=f)
            elif v.find(',') > 0:
                print('    values.append(trial.suggest_categorical("'+k+'", ['+v+'])'
                      +')', file=f)
            else:
                print('    values.append('+v+') // ' + k, file=f)

        print("    result_branch = '"+input_branch_name+"_'+str(time.time_ns())", file=f)
        print("    dvc_save_path = 'dvc/' + result_branch", file=f)
        print('    os.mkdir(dvc_save_path)', file=f)
        print('    vc.set_values_for_hyperopt_files(values, dvc_save_path=dvc_save_path)', file=f)
        print('', file=f)
        print('    # Create RED-YMLnano', file=f)
        print("    with open('cc_execution_file_optuna.red.yml','r') as f:", file=f)
        print('        red_yml = f.read()', file=f)
        print("    red_yml = red_yml.replace('rcc_0032_MetricTest_XXXXXXXXXX', result_branch)", file=f)
        print("    with open(dvc_save_path+'/cc_execution_file.red.yml','w') as f:", file=f)
        print('        print(red_yml, file=f)', file=f)
        print('', file=f)
        print("    subprocess.call(('git add '+dvc_save_path+'/*').split(' '))", file=f)
        print('    subprocess.call("git commit -m \'SOMETHING\'".split(\' \'))', file=f)
        print('    subprocess.call("git push".split(\' \'))', file=f)
        print('', file=f)
        print('    # START RUN', file=f)
        print("    p = 'faice exec '+dvc_save_path+'/cc_execution_file.red.yml'# --disable-retry'", file=f)
        print("    message = subprocess.call(p.split(' '))", file=f)
        print('    result = None', file=f)
        print('    while result is None:', file=f)
        print('        time.sleep(np.random.randint(60))', file=f)
        print("        with open('metrics.json', 'r') as f:", file=f)
        print('            metrics = json.load(f)', file=f)
        print("        metrics = {m[:m.find('__')]:metrics[m] for m in metrics}", file=f)
        print('        if result_branch in metrics:', file=f)
        print('            result = metrics[result_branch]', file=f)
        print('', file=f)
        print('    return result', file=f)
        print('', file=f)
        print('import optuna', file=f)
        print('', file=f)
        print("study = optuna.create_study(direction='minimize',", file=f)
        print("                            study_name='study_1', ", file=f)
        print("                            storage='sqlite:///"+input_branch_name+".db?timeout=99999',", file=f)
        print('                            load_if_exists=True', file=f)
        print('                           )', file=f)
        print('', file=f)
        print('study.optimize(startbla, n_trials=300,n_jobs=150)', file=f)


# parameters
#metric_path = 'loss.metric'
#input_branch = 'cc_0032_MetricTest'
#save_summary = '../learn-subjectivity/metrics.json'
def write_metric_getter_script(path, input_branch_name, metric_path, save_summary):
    with open(path,'w') as f:
        print('# !/usr/bin/env python', file=f)
        print('# coding: utf-8', file=f)
        print('', file=f)
        print('import git\nimport json\nimport os\nimport time\n', file=f)
        print('', file=f)
        print('g = git.Git()', file=f)
        print('', file=f)
        print("metric_path = '"+metric_path+"'", file=f)
        print("input_branch = '"+input_branch_name+"'", file=f)
        print("save_summary = '" + save_summary + "'", file=f)
        print('', file=f)
        print('metrics = {}', file=f)
        print('if not os.path.isfile(save_summary):', file=f)
        print("    with open(save_summary, 'w') as f:", file=f)
        print('        json.dump(metrics, f)', file=f)
        print('else:', file=f)
        print("    with open(save_summary, 'r') as f:", file=f)
        print('        metrics = json.load(f)', file=f)
        print('', file=f)
        print('while True:', file=f)
        print('    g.pull()', file=f)
        print('    time.sleep(1)', file=f)
        print("    all_branches = [b.split('/')[-1] for b in g.branch('-a').split() if", file=f)
        print("                    b.startswith('remotes/origin/r' + input_branch)]", file=f)
        print('    new_branches = [b for b in all_branches if b not in metrics.keys()]', file=f)
        print('    for b in new_branches:', file=f)
        print('        g.checkout(b)', file=f)
        print("        with open(metric_path, 'r') as f:", file=f)
        print('            metrics[b] = float(f.read())', file=f)
        print("    with open(save_summary, 'w') as f:", file=f)
        print('        json.dump(metrics, f)', file=f)
        print('    if len(new_branches):', file=f)
        print("        print('New-Branches: ', new_branches)", file=f)
        print('', file=f)



def create_optuna_directories(input_branch_name, vc):
    # 1. copy current directory
    import shutil
    jobstarter_path = '../'+os.getcwd().split('/')[-1]+'_'+input_branch_name.split('_')[1]+'_JobStarter'
    shutil.copytree('.', jobstarter_path)

    metric_path = '../' + os.getcwd().split('/')[-1] + '_MetricGetter'
    if not os.path.exists(metric_path):
        shutil.copytree('.', jobstarter_path)

    # 2. get input values
    inputs = {}
    for v in vc.list_of_all_variables:
        inp = input(str(v.varname + ' (' + v.vartype + '): '))
        inputs[v.varname] = [v.vartype, inp]

    # 3. Create optuna script
    write_optuna_execution_script(path=jobstarter_path+'/run_optuna.py',inputs=inputs, input_branch_name=input_branch_name)

    # 4. Create metrics getter script
    # TODO: The 'loss.metric' must be a variable !
    write_metric_getter_script(path=metric_path + '/get_metrics.py', input_branch_name,
                               'loss.metric', jobstarter_path+'/metrics.json')