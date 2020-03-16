#!/bin/bash

timestamp() {
  date +"%y_%m_%d_%H_%M_%S_%N"
}
tmstmp=$( timestamp )
echo "DVC REPRO $1 2>&1 | tee $3$2_$tmstmp stdout_stderr/$2_$tmstmp"
export PYTHONUNBUFFERED=true
dvc repro $1 2>&1 | tee $3$2_$tmstmp stdout_stderr/$2_$tmstmp
