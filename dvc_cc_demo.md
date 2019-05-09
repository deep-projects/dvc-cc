# First you should install Anaconda and create an environment 
conda create --name the_name_of_your_env pip git numpy appdirs decorator -y

# activate the environment
conda activate the_name_of_your_env   # in older versions: source activate the_name_of_your_env

# download source code
git clone https://github.com/mastaer/dvc-cc.git

# install the software that you need to run the code
pip install dvc-cc/dep/cc_core-7.0.0-py3-none-any.whl --ignore-installed   # soon this will be:  pip install cc-core
pip install dvc-cc/dep/cc_faice-7.0.0-py3-none-any.whl --ignore-installed  # soon this will be:  pip install cc-faice
pip install dvc-cc/dist/dvc_cc-0.1.0-py3-none-any.whl --ignore-installed

# GO to github or gitlab and create a new project: i.e. the project name: dvc_demo

# Create a Folder on a server for the extern dvc directory

# Clone the git: 
git clone https://git.tools.f4.htw-berlin.de/annusch/demo_dvc.git

# Go the the project folder
cd demo_dvc


# CONVERT TO A DVC-Project,
# dvc init # This will be called by dvc-cc project create

# Create simple project
dvc-cc project create

# create a .dvc/config.local file: It should look like this (nano .dvc/config.local)
['remote "nas"']
url = ssh://annusch@avocado01.f4.htw-berlin.de/data/ldap/jonas/demo_dvc
ask_password = true

[core]
remote = nas

# create the dataset
dvc repro _generate_data.dvc

# push everything
dvc-cc git commit_and_push

# build a experiment in a branch
dvc-cc git branch first_experiment

# add the following line to nano code/argparser.py
    parser.add_argument('-n','--num_of_samples', default=10)
# edit line 26 from code/train.py to
num_of_samples = int(args.num_of_samples)

# Create some sub-experiments:
dvc-cc project dummy -p "-n 2"
dvc-cc project dummy -p "-n 5"
dvc-cc project dummy -p "-n 10"
dvc-cc project dummy -p "-n 20"
dvc-cc project dummy -p "-n 100"

dvc-cc git commit_and_push

# create red yml file
dvc-cc red add_job -T

# run the job
dvc-cc jobs run




# show the dependencies code/argparser.py
dvc pipeline show --ascii eval.dvc

# show a metric that 
dvc metrics show -t json -x L1_Test -a



# if you are finish with testing, and this is nothing for you, you can remove the env with:
conda deactivate
conda remove -n the_name_of_your_env --all -y

