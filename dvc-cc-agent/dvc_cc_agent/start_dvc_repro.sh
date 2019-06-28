#!/bin/bash

timestamp() {
  date +"%T"
}

dvc repro $1 2>&1 | tee $2/$1_test stdout_stderr/test