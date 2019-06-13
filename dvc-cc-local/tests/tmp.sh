#!/bin/bash
STARTINGDIR=$PWD
echo `dirname $0`
cd ~
echo `ls`
echo `dirname $0`
cd $STARTINGDIR
echo `ls`
cp data_for_testscript4/script_for_test4_train.py ~/test_pcam/repo/code/train.py

exit 0





