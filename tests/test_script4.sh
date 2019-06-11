#!/bin/bash

echo "			####################################"
echo "			# -1. Step:                        #"
echo "			# Remove the project               #"
echo "			####################################"
cd ~

if [ -d "$HOME/test_pcam" ]
then
    echo 'Remove the directory ~/test_pcam.'
    rm -rf ~/test_pcam
fi

#cd ~/Documents/github/dvc-cc-NEW/tests/
#./test_script4.sh



mkdir ~/test_pcam
cd ~/test_pcam


echo "			#########################"
echo "			# 1. Step:              #"
echo "			# Create GIT Repository #"
echo "			#########################"

echo "import gitlab
import time
gl = gitlab.Gitlab('https://git.tools.f4.htw-berlin.de/',private_token='1oxzXp1MyJ1Yz6KEnxyS')
gl.auth()

try:
    gl_id = gl.projects.get('annusch/test_pcam').get_id()
    gl.projects.delete(gl_id)
    time.sleep(5)
    print('Deleted the git repo: test_pcam')
except:
    print('No git repo found.')

project = gl.projects.create({'name': 'test_pcam'})" >> ~/test_pcam/create_git_repo.py

python ~/test_pcam/create_git_repo.py

# Save the git credential
git config --global credential.helper 'cache --timeout 1000'

# clone empty git repository
git clone https://git.tools.f4.htw-berlin.de/annusch/test_pcam.git repo

cd repo

echo "			###############"
echo "			# 2. Step:    #"
echo "			# Init DVC-CC #"
echo "			###############"
dvc-cc init

git add -A
git commit -m 'init project'

git push --set-upstream origin master

echo "			##################"
echo "			# 3. Step:       #"
echo "			# SET DVC-CC-URL #"
echo "			##################"
dvc remote add -d dvc_connection ssh://annusch@avocado01.f4.htw-berlin.de/data/ldap/jonas/test_pcam
dvc remote modify dvc_connection ask_password true
dvc push
dvc pull

echo "			######################################"
echo "			# 4. Step:                           #"
echo "			# Download Script for PCAM-Datensatz #"
echo "			######################################"

mkdir dvc
mkdir code
mkdir mkdir data
echo "
cd data

## for download from google per command line we need gdown
# pip install gdown

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
    dvc run -d code/download_pcam_dataset.sh -o data/camelyonpatch_level_2_split_test_meta.csv -o data/camelyonpatch_level_2_split_train_meta.csv -o data/camelyonpatch_level_2_split_valid_meta.csv -o data/camelyonpatch_level_2_split_test_x.h5 -o data/camelyonpatch_level_2_split_train_x.h5 -o data/camelyonpatch_level_2_split_valid_x.h5 -o data/camelyonpatch_level_2_split_test_y.h5 -o data/camelyonpatch_level_2_split_train_y.h5 -o data/camelyonpatch_level_2_split_valid_y.h5 -f dvc/download_pcam_dataset.dvc --no-exec sh code/download_pcam_dataset.sh

    dvc repro -P
    dvc push
fi

echo "			####################################################"
echo "			# 4.2 Step:                                        #"
echo "			# Cheat: Use the DVC-File that was created earlier #"
echo "			####################################################"

if [ "$DOWNLOAD" -eq 0 ]
then
    echo "PULL DATASET from DVC"
    echo "cmd: sh code/download_pcam_dataset.sh
wdir: ..
deps:
- path: code/download_pcam_dataset.sh
  md5: 5bc12eddeda6dcf151cb45ae39d6cc2b
outs:
- path: data/camelyonpatch_level_2_split_test_meta.csv
  cache: true
  metric: false
  persist: false
  md5: 3455fd69135b66734e1008f3af684566
- path: data/camelyonpatch_level_2_split_train_meta.csv
  cache: true
  metric: false
  persist: false
  md5: 5a3dd671e465cfd74b5b822125e65b0a
- path: data/camelyonpatch_level_2_split_valid_meta.csv
  cache: true
  metric: false
  persist: false
  md5: 67589e00a4a37ec317f2d1932c7502ca
- path: data/camelyonpatch_level_2_split_test_x.h5
  cache: true
  metric: false
  persist: false
  md5: 2614b2e6717d6356be141d9d6dbfcb7e
- path: data/camelyonpatch_level_2_split_train_x.h5
  cache: true
  metric: false
  persist: false
  md5: 01844da899645b4d6f84946d417ba453
- path: data/camelyonpatch_level_2_split_valid_x.h5
  cache: true
  metric: false
  persist: false
  md5: 81cf9680f1724c40673f10dc88e909b1
- path: data/camelyonpatch_level_2_split_test_y.h5
  cache: true
  metric: false
  persist: false
  md5: 11ed647efe9fe457a4eb45df1dba19ba
- path: data/camelyonpatch_level_2_split_train_y.h5
  cache: true
  metric: false
  persist: false
  md5: 0781386bf6c2fb62d58ff18891466aca
- path: data/camelyonpatch_level_2_split_valid_y.h5
  cache: true
  metric: false
  persist: false
  md5: 94d8aacc249253159ce2a2e78a86e658
md5: be8e94a1e0938d84c07e510cd822bdb7" > dvc/download_pcam_dataset.dvc
    dvc pull
fi

exit 0





