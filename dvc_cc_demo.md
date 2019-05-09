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
git clone https://git.tools.f4.htw-berlin.de/annusch/dvc_demo.git

# Go the the project folder
cd dvc_demo


# CONVERT TO A DVC-Project,
# dvc init # This will be called by dvc-cc project create

# Create simple project
dvc-cc project create

# create a .dvc/config.local file: It should look like this
['remote "nas"']
url = ssh://annusch@avocado01.f4.htw-berlin.de/data/ldap/jonas/dvc_demo
ask_password = true

[core]
remote = nas

# push everything
dvc-cc git commit_and_push





# show the dependencies
dvc pipeline show --ascii eval.dvc

# show a metric that 
dvc metrics show -t json -x L1_Test -a




# if you are finish with testing, and this is nothing for you, you can remove the env with:
conda deactivate
conda remove -n the_name_of_your_env --all -y

