import sys
sys.path.insert(0,'code')
sys.path.insert(0,'code/helper')

from subprocess import check_output

def get_name_of_experiment(args=None):
    out = check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    name_of_experiment = current.strip("*").strip()

    args_dict = vars(args)

    experiment_settings = ''
    for k in args_dict:
        v = str(args_dict[k]).replace('.','_').replace(',','_').replace('-','_')
        experiment_settings = experiment_settings + '_' + v


    # TODO: Need to use the args!
    print('The name of the experiment is: ', name_of_experiment + experiment_settings)
    return name_of_experiment + experiment_settings


if __name__ == '__main__':
    print(get_name_of_experiment())
