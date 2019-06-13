#!/bin/bash

STARTINGDIR=$PWD

echo "			####################################"
echo "			# -1. Step:                        #"
echo "			# Remove the project               #"
echo "			####################################"
cd ~
fusermount -u -z ${HOME}/pcam_with_dvc_cc_sshfs/repo/data

if [ -d "$HOME/pcam_with_dvc_cc_sshfs" ]
then
    echo 'Remove the directory ~/pcam_with_dvc_cc_sshfs.'
    rm -rf ~/pcam_with_dvc_cc_sshfs
fi

#cd ~/Documents/github/dvc-cc-NEW/tests/
#./test_script4.sh



mkdir ~/pcam_with_dvc_cc_sshfs
cd ~/pcam_with_dvc_cc_sshfs


echo "			#########################"
echo "			# 1. Step:              #"
echo "			# Create GIT Repository #"
echo "			#########################"

echo "import gitlab
import time
gl = gitlab.Gitlab('https://git.tools.f4.htw-berlin.de/',private_token='1oxzXp1MyJ1Yz6KEnxyS')
gl.auth()

try:
    gl_id = gl.projects.get('annusch/pcam_with_dvc_cc_sshfs').get_id()
    gl.projects.delete(gl_id)
    time.sleep(5)
    print('Deleted the git repo: pcam_with_dvc_cc_sshfs')
except:
    print('No git repo found.')

project = gl.projects.create({'name': 'pcam_with_dvc_cc_sshfs'})" >> ~/pcam_with_dvc_cc_sshfs/create_git_repo.py

python ~/pcam_with_dvc_cc_sshfs/create_git_repo.py

# Save the git credential
git config --global credential.helper 'cache --timeout 1000'

# clone empty git repository
git clone https://git.tools.f4.htw-berlin.de/annusch/pcam_with_dvc_cc_sshfs.git repo

cd repo

echo "			###############"
echo "			# 2. Step:    #"
echo "			# Init DVC-CC #"
echo "			###############"
dvc-cc init

git add -A
git commit -m 'init project, with "dvc-cc init"'

git push --set-upstream origin master

echo "			##################"
echo "			# 3. Step:       #"
echo "			# SET DVC-CC-URL #"
echo "			##################"
dvc remote add -d dvc_connection ssh://annusch@avocado01.f4.htw-berlin.de/data/ldap/jonas/pcam_with_dvc_cc_sshfs
dvc remote modify dvc_connection ask_password true
dvc push
dvc pull

echo "			######################################"
echo "			# 4. Step:                           #"
echo "			# Download Script for PCAM-Datensatz #"
echo "			######################################"

mkdir dvc
mkdir code
mkdir data

sshfs annusch@avocado01.f4.htw-berlin.de:/data/ldap/jonas/pcam_with_dvc_cc_sshfs_DATA ~/pcam_with_dvc_cc_sshfs/repo/data/

echo "
set -eu

mkdir -p data

cd data



## for download from google per command line we need gdown
pip install gdown

# Trainings-Data
gdown https://drive.google.com/uc?id=1Ka0XfEMiwgCYPdTI-vv6eUElOBnKFKQ2
gdown https://drive.google.com/uc?id=1269yhu3pZDP8UYFQs-NYs3FPwuK-nGSG

# Validation-Data
gdown https://drive.google.com/uc?id=1hgshYGWK8V-eGRy8LToWJJgDU_rXWVJ3
gdown https://drive.google.com/uc?id=1bH8ZRbhSVAhScTS0p9-ZzGnX91cHT3uO

# Test-Data
gdown https://drive.google.com/uc?id=1qV65ZqZvWzuIVthK8eVDhIwrbnsJdbg_
gdown https://drive.google.com/uc?id=17BHrSrwWKjYsOgTMmoqrIjDy6Fa2o_gP

# Meta-Files
gdown https://drive.google.com/uc?id=1XoaGG3ek26YLFvGzmkKeOz54INW0fruR
gdown https://drive.google.com/uc?id=16hJfGFCZEcvR3lr38v3XCaD5iH1Bnclg
gdown https://drive.google.com/uc?id=19tj7fBlQQrd4DapCjhZrom_fA4QlHqN4

# unzip all files and remove all .gz files
gzip -d *.gz" > code/download_pcam_dataset.sh

echo "			###########################"
echo "			# 4.1 Step:               #"
echo "			# Download PCAM-Datensatz #"
echo "			###########################"

DOWNLOAD=0
if [ "$DOWNLOAD" -eq 1 ]
then
    dvc run -d code/download_pcam_dataset.sh -O data/camelyonpatch_level_2_split_test_meta.csv -O data/camelyonpatch_level_2_split_train_meta.csv -O data/camelyonpatch_level_2_split_valid_meta.csv -O data/camelyonpatch_level_2_split_test_x.h5 -O data/camelyonpatch_level_2_split_train_x.h5 -O data/camelyonpatch_level_2_split_valid_x.h5 -O data/camelyonpatch_level_2_split_test_y.h5 -O data/camelyonpatch_level_2_split_train_y.h5 -O data/camelyonpatch_level_2_split_valid_y.h5 -f dvc/download_pcam_dataset.dvc --no-exec sh code/download_pcam_dataset.sh
fi



if [ "$DOWNLOAD" -eq 0 ]
then
    echo "PULL DATASET from DVC"
    echo "cmd: sh code/download_pcam_dataset.sh
wdir: ..
deps:
- path: code/download_pcam_dataset.sh
  md5: 0319785babf8e5321a2553d5c8fc39ef
outs:
- path: data/camelyonpatch_level_2_split_test_meta.csv
  cache: false
  metric: false
  persist: false
  md5: 3455fd69135b66734e1008f3af684566
- path: data/camelyonpatch_level_2_split_train_meta.csv
  cache: false
  metric: false
  persist: false
  md5: 5a3dd671e465cfd74b5b822125e65b0a
- path: data/camelyonpatch_level_2_split_valid_meta.csv
  cache: false
  metric: false
  persist: false
  md5: 67589e00a4a37ec317f2d1932c7502ca
- path: data/camelyonpatch_level_2_split_test_x.h5
  cache: false
  metric: false
  persist: false
  md5: 2614b2e6717d6356be141d9d6dbfcb7e
- path: data/camelyonpatch_level_2_split_train_x.h5
  cache: false
  metric: false
  persist: false
  md5: 01844da899645b4d6f84946d417ba453
- path: data/camelyonpatch_level_2_split_valid_x.h5
  cache: false
  metric: false
  persist: false
  md5: 81cf9680f1724c40673f10dc88e909b1
- path: data/camelyonpatch_level_2_split_test_y.h5
  cache: false
  metric: false
  persist: false
  md5: 11ed647efe9fe457a4eb45df1dba19ba
- path: data/camelyonpatch_level_2_split_train_y.h5
  cache: false
  metric: false
  persist: false
  md5: 0781386bf6c2fb62d58ff18891466aca
- path: data/camelyonpatch_level_2_split_valid_y.h5
  cache: false
  metric: false
  persist: false
  md5: 94d8aacc249253159ce2a2e78a86e658
md5: 6c6f9823f5d28d2ec2175edcf7ce212a" > dvc/download_pcam_dataset.dvc
    dvc pull
    
fi

echo "data
.idea" > .gitignore

dvc repro -P
dvc push





# copy training file !
cd $STARTINGDIR
cp data_for_testscript4/train.ipynb ~/pcam_with_dvc_cc_sshfs/repo/code/train.ipynb

# start some jobs
cd ~/pcam_with_dvc_cc_sshfs/repo
git add -A
git commit -m 'add code/train.py'

# RUN ONE - WITHOUT HAVING THE DOWNLOADED DATA IN THE CACHE !!!
dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.1

git add dvc/train_network.dvc

dvc-cc run 'first_test'

sleep 60

# push the data to the dvc cache
dvc push
# RUN ONE - NOW WITH DATA IN CACHE
dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.2

git add dvc/train_network.dvc

dvc-cc run -r 2 -nb 'try_learning_rate_0.2'



# RUN TWO: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.5

git add dvc/train_network.dvc

dvc-cc run -r 2 -nb 'try_learning_rate_0.5'



# RUN THREE: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.1

git add dvc/train_network.dvc

dvc-cc run -r 2 -nb 'try_learning_rate_0.1'





# RUN FOUR: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.05

git add dvc/train_network.dvc

dvc-cc run -r 2 -nb 'try_learning_rate_0.05'





# RUN FIVE: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.01

git add dvc/train_network.dvc

dvc-cc run -r 2 -nb 'try_learning_rate_0.01'





### Now download all tensorboard files where the learning rate was changed
# get all new branches
dvc-cc git sync
# pull all files
dvc pull -a
# write all files to one stage
dvc-cc output-to-tmp -d -b 'bcc_.*learning_rate.*' -f 'tensorboards/tb' -r

exit 0





