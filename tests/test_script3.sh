#!/bin/bash

mkdir ~/test_repo
cd ~/test_repo


##################################
# 1. Step:                       #
# GIT with LOCAL (remote) server #
##################################
#git init --bare ~/test_repo/storage_git/myproject.git

#git remote add origin ~/test_repo/storage_git/myproject.git

echo "import gitlab
import time
gl = gitlab.Gitlab('https://git.tools.f4.htw-berlin.de/', private_token='1oxzXp1MyJ1Yz6KEnxyS')
gl.auth()

try:
    gl_id = gl.projects.get('annusch/project1').get_id()
    gl.projects.delete(gl_id)
    time.sleep(2)
except:
    print('Fine')

project = gl.projects.create({'name': 'project1'})" >> ~/test_repo/create_git_repo.py
python ~/test_repo/create_git_repo.py

git config --global credential.helper 'cache --timeout 1000'

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
cp .git/config .git/config_tmp

git submodule add https://github.com/mastaer/create_mnist_data.git create_dataset

cp .git/config_tmp .git/config
rm .git/config_tmp


rm .gitmodules
git add .gitmodules
git rm --cached create_dataset
rm -rf .git/modules/create_dataset

rm create_dataset/.git

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
# 5- Step:                              #
# SETUP A PROJECT                       #
#########################################
echo "import numpy as np\nimport json\n\ntrain_data = np.load('data/mnist1.npz')\nx = train_data['x_train']\ny = train_data['y_train']\n\nx_pred = np.array(train_data['x_train'].mean(axis=(1,2)) / 15.0, dtype=int)\n\nacc = (y==x_pred).sum() / float(y.shape[0])\n\ndata = {}  \ndata['acc'] = acc+np.random.random()/100.\n\nwith open('train_acc.json', 'w') as outfile:\n      json.dump(data, outfile)" >> train.py
echo "import numpy as np\nimport json\n\ntrain_data = np.load('data/mnist2.npz')\nx = train_data['x_test']\ny = train_data['y_test']\n\nx_pred = np.array(train_data['x_test'].mean(axis=(1,2)) / 15.0, dtype=int)\n\nacc = (y==x_pred).sum() / float(y.shape[0])\n\ndata = {}  \ndata['acc'] = acc +np.random.random()/100.\n\nwith open('test_acc.json', 'w') as outfile:\n      json.dump(data, outfile)" >> test.py
dvc run -d data/mnist1.npz -m train_acc.json --no-exec python train.py 
dvc run -d data/mnist2.npz -d train_acc.json -m test_acc.json --no-exec python test.py 

echo "import numpy as np\nimport json\n\ntrain_data = np.load('data/mnist3.npz')\nx = train_data['x_train']\ny = train_data['y_train']\n\nx_pred = np.array(train_data['x_train'].mean(axis=(1,2)) / 15.0, dtype=int)\n\nacc = (y==x_pred).sum() / float(y.shape[0])\n\ndata = {}  \ndata['acc'] = acc+np.random.random()/100.\n\nwith open('train_acc2.json', 'w') as outfile:\n      json.dump(data, outfile)" >> train2.py
echo "import numpy as np\nimport json\n\ntrain_data = np.load('data/mnist1.npz')\nx = train_data['x_test']\ny = train_data['y_test']\n\nx_pred = np.array(train_data['x_test'].mean(axis=(1,2)) / 15.0, dtype=int)\n\nacc = (y==x_pred).sum() / float(y.shape[0])\n\ndata = {}  \ndata['acc'] = acc +np.random.random()/100.\n\nwith open('test_acc2.json', 'w') as outfile:\n      json.dump(data, outfile)" >> test2.py
echo "import numpy as np\nimport json\n\ntrain_data = np.load('data/mnist1.npz')\nx = train_data['x_test']\ny = train_data['y_test']\n\nx_pred = np.array(train_data['x_test'].mean(axis=(1,2)) / 15.0, dtype=int)\n\nacc = (y==x_pred).sum() / float(y.shape[0])\n\ndata = {}  \ndata['acc'] = acc +np.random.random()/100.\n\nwith open('test_acc3.json', 'w') as outfile:\n      json.dump(data, outfile)" >> test3.py
dvc run -d data/mnist3.npz -m train_acc2.json --no-exec python train2.py 
dvc run -d data/mnist1.npz -d train_acc2.json -m test_acc2.json --no-exec python test2.py 
dvc run -d data/mnist1.npz -d train_acc2.json -m test_acc3.json --no-exec python test3.py 

git add -A
git commit -m 'build pipeline'
git push

#########################################
# 6. Step:                              #
#   DVC-CC INIT                         #
#########################################
dvc-cc init
dvc-cc run "ONE_FILE" -f "test_acc2.json.dvc"
dvc-cc run "ONE_FILE_IN_DIRECTORY" -f "create_dataset/create_dataset.dvc"
dvc-cc run "MULTIPLE_FILES_IN_2_PIPELINES" -f "test_acc.json.dvc,test_acc2.json.dvc|train_acc2.json.dvc"
dvc-cc run "just_an_experimentname"

dvc-cc run "MULTIPLE_FILES_IN_2_PIPELINES" -f "test_acc.json.dvc,test_acc2.json.dvc|train_acc2.json.dvc" --no-exec


#cd ~/test_repo/repo
git pull


#########################################
# 7. Step:                              #
# Remove the dummy project              #
#########################################
#cd ~
#fusermount -u -z ${HOME}/test_repo/avocado
#fusermount -u -z ${HOME}/test_repo/repo/data
#rm -rf ~/test_repo
#cd ~/Documents/github/dvc-cc-NEW/tests/
#./test_script3.sh
