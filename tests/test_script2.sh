#!/bin/bash

mkdir ~/test_repo
cd ~/test_repo


##################################
# 1. Step:                       #
# GIT with LOCAL (remote) server #
##################################
#git init --bare ~/test_repo/storage_git/myproject.git

#git remote add origin ~/test_repo/storage_git/myproject.git

echo -e "\n
\n
import gitlab\n
import time\n
gl = gitlab.Gitlab('https://git.tools.f4.htw-berlin.de/', private_token='TA5fBL-ypdtqrL9nUF3N')\n
gl.auth()\n
\n
try:\n
    gl_id = gl.projects.get('annusch/project1').get_id()\n
    gl.projects.delete(gl_id)\n
    time.sleep(2)
except:\n
    print('Fine')\n
\n
project = gl.projects.create({'name': 'project1'})\n" >> ~/test_repo/create_git_repo.py
python ~/test_repo/create_git_repo.py

git config --global credential.helper 'cache --timeout 7200'

git clone https://git.tools.f4.htw-berlin.de/annusch/project1.git repo

cd repo

dvc init

git add -A
git commit -m 'init project'

git push --set-upstream origin master

mkdir ~/test_repo/avocado/
sshfs annusch@avocado01.f4.htw-berlin.de:/data/ldap/jonas/ ~/test_repo/avocado/

rm -R ~/test_repo/avocado/_testproject_DVC
rm -R ~/test_repo/avocado/_testproject_DATA

mkdir ~/test_repo/avocado/_testproject_DVC
mkdir ~/test_repo/avocado/_testproject_DATA

##################################
# 2. Step:                       #
# DVC with LOCAL (remote) server #
##################################
dvc remote add -d dvc_connection ssh://annusch@avocado01.f4.htw-berlin.de/data/ldap/jonas/_testproject_DVC
dvc remote modify dvc_connection ask_password true
dvc push

###################################
# 3. Step:                        #
# Create SSHFS to an empty folder #
###################################

mkdir data

# maybe need to install: sudo apt-get install openssh-server
sshfs annusch@avocado01.f4.htw-berlin.de:/data/ldap/jonas/_testproject_DATA ~/test_repo/repo/data/
#sshfs $(id -un)@$(hostname -f):${HOME}/test_repo/data_sshfs/ data/

#########################################
# 4. Step:                              #
# Download the submodule                #
# and creates the data in the sshfs-dir #
# the data can be that large that I do  #
# not want them in my computer          #
# or I don't want them multiple times   #
# in different repos in my computer     #
#########################################
git submodule add https://github.com/mastaer/create_mnist_data.git create_dataset

dvc repro -P

#echo -e "data\ncreate_dataset\ndata/*\ncreate_dataset/*\n" >> .dvcignore


#########################################
# 4. Step:                              #
# Push Everything                       #
#########################################
git add -A
git commit -m 'create the dataset'
git push --set-upstream origin master
dvc push

#########################################
# 5. Step:                              #
# SETUP A PROJECT                       #
#########################################
echo -e "import numpy as np\nimport json\n\ntrain_data = np.load('data/mnist1.npz')\nx = train_data['x_train']\ny = train_data['y_train']\n\nx_pred = np.array(train_data['x_train'].mean(axis=(1,2)) / 15.0, dtype=int)\n\nacc = (y==x_pred).sum() / float(y.shape[0])\n\ndata = {}  \ndata['acc'] = acc+np.random.random()/100.\n\nwith open('train_acc.json', 'w') as outfile:\n      json.dump(data, outfile)" >> train.py

echo -e "import numpy as np\nimport json\n\ntrain_data = np.load('data/mnist2.npz')\nx = train_data['x_test']\ny = train_data['y_test']\n\nx_pred = np.array(train_data['x_test'].mean(axis=(1,2)) / 15.0, dtype=int)\n\nacc = (y==x_pred).sum() / float(y.shape[0])\n\ndata = {}  \ndata['acc'] = acc +np.random.random()/100.\n\nwith open('test_acc.json', 'w') as outfile:\n      json.dump(data, outfile)" >> test.py

dvc run -d data/mnist1.npz -m train_acc.json --no-exec python train.py 
dvc run -d data/mnist2.npz -d train_acc.json -m test_acc.json --no-exec python test.py 


#########################################
# 6. Step:                              #
# TEST EXECUTEPY                        #
#########################################


git add -A
git commit -m 'build pipeline'
git push
git tag -a 001_firstexperiment -m 'First message!'
git tag -a 002_secondexperiment -m 'Second message!'
git push origin --tags











cd ..

git clone --recurse-submodules https://git.tools.f4.htw-berlin.de/annusch/project1.git myproject1
cd myproject1

git checkout tags/001_firstexperiment -b result_001_firstexperiment
ln -s ../data_sshfs data
dvc repro -P
git add -A
git commit -m 'result_001_firstexperiment'
git push -u origin result_001_firstexperiment
dvc push

cd ..

git clone --recurse-submodules https://git.tools.f4.htw-berlin.de/annusch/project1.git myproject2
cd myproject2

git checkout tags/002_secondexperiment -b result_002_secondexperiment
ln -s ../data_sshfs data
dvc repro -P
git add -A
git commit -m 'result_002_secondexperiment'
git push -u origin result_002_secondexperiment
dvc push

cd ..
cd repo
git pull
dvc pull


git branch -a
git checkout result_001_firstexperiment
dvc pull
git checkout result_002_secondexperiment
dvc pull

# Here comes the error
dvc metrics show -a

#########################################
# 7. Step:                              #
# Remove the dummy project              #
#########################################
cd ~
fusermount -u -z ${HOME}/test_repo/avocado
fusermount -u -z ${HOME}/test_repo/repo/data
rm -rf ~/test_repo
