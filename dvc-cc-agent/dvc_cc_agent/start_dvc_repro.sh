#!/bin/bash

timestamp() {
  date +"%y_%m_%d_%H_%M_%S_%N"
}
tmstmp=$( timestamp )
echo "DVC REPRO $1 2>&1 | tee $3$2_$tmstmp stdout_stderr/$2_$tmstmp"
export PYTHONUNBUFFERED=true
dvc repro $1 2>&1 | tee $3$2_$tmstmp stdout_stderr/$2_$tmstmp

if [ $? -eq 0 ]
then
  echo "Successfully executed script"
  exit 0;
else
  # Redirect stdout from echo command to stderr.
  echo "Script exited with error." >&2
  exit 1;
fi
