#!/bin/bash



#########################################
# 7. Step:                              #
# Remove the hyperopt project              #
#########################################
cd ~
fusermount -u -z ${HOME}/test_repo/avocado
fusermount -u -z ${HOME}/test_repo/repo/data
rm -rf ~/test_repo
cd ~/Documents/github/dvc-cc-NEW/tests/
#./test_script3.sh
