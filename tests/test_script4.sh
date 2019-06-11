#!/bin/bash


####################################
# -1. Step:                        #
# Remove the project               #
####################################
cd ~
rm -rf ~/test_pcam
#cd ~/Documents/github/dvc-cc-NEW/tests/
#./test_script4.sh



mkdir ~/test_pcam
cd ~/test_pcam


#########################
# 1. Step:              #
# Create GIT Repository #
#########################

echo -e "\n
\n
import gitlab\n
import time\n
gl = gitlab.Gitlab('https://git.tools.f4.htw-berlin.de/', private_token='1oxzXp1MyJ1Yz6KEnxyS')\n
gl.auth()\n
\n
try:\n
    gl_id = gl.projects.get('annusch/test_pcam').get_id()\n
    gl.projects.delete(gl_id)\n
    time.sleep(2)
except:\n
    print('Fine')\n
\n
project = gl.projects.create({'name': 'test_pcam'})\n" >> ~/test_pcam/create_git_repo.py

python ~/test_pcam/create_git_repo.py

# Save the git credential
git config --global credential.helper 'cache --timeout 1000'

# clone empty git repository
git clone https://git.tools.f4.htw-berlin.de/annusch/test_pcam.git repo

cd repo

###############
# 2. Step:    #
# Init DVC-CC #
###############
dvc-cc init

git add -A
git commit -m 'init project'

git push --set-upstream origin master


###########################
# 3. Step:                #
# Download PCAM-Datensatz #
###########################





