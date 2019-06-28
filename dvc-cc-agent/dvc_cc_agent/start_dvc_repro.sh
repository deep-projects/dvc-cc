#!/bin/bash

timestamp() {
  date +"%T"
}
echo "dvc repro `$1` 2>&1 | tee `$2`/`$1`_test stdout_stderr/test"
dvc repro $1 2>&1 | tee $2/$1_test stdout_stderr/test