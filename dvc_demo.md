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

# Clone the git: here is it the following link
git clone https://git.tools.f4.htw-berlin.de/annusch/dvc_demo.git

# Go the the project folder
cd dvc_demo


# CONVERT TO A DVC-Project,
# dvc init # This will be called by dvc-cc project create

# Create simple project
dvc-cc project create --mini_project

# instead of just calling "python create_some_data.py", we define with 
# we use the --no-exec command, so that we can demonstrate later the dvc repro -P
dvc run -d create_some_data.py \
        -o mydata.npy \
        --no-exec \
        -f _create_data.dvc \
        python create_some_data.py

# we do this also for the train.py and for the eval.py
dvc run -d mydata.npy \
        -d train.py \
        -o train_model.npy \
        -m train_metric.json \
        --no-exec \
        -f _train.dvc \
        python train.py

dvc run -d mydata.npy \
        -d train_model.npy \
        -d eval.py \
        -m test_metric.json \
        -f eval.dvc \
        --no-exec
        python eval.py


# NOW we can run the experiment
dvc repro -P

# If we delete one file, for example the test_metric.json and call dvc repro -P again, it will only run the stage that is needed
rm test_metric.json
dvc repro -P


# show the dependencies
dvc pipeline show --ascii eval.dvc

# show a metric that 
dvc metrics show -t json -x L1_Test -a




# if you are finish with testing, and this is nothing for you, you can remove the env with:
conda deactivate
conda remove -n the_name_of_your_env --all -y

