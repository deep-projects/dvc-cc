# DVC-CC

DVC-CC was developed for machine learning projects with the main target of reproducibility, simplicity and **scalability**.

- Reproducibility means that all experiments created in parallel or sequentially can be reproduced by you and others who have access to your GIT and DVC repository.
- Scalability means that these scripts ensure that you can run them on your cluster system.
- Simplicity means that it should not cause too much more workload.

To archive this target, DVC-CC is based on the two softwares [Open-source Version Control System for Machine Learning Projects (DVC)](https://dvc.org/) and [Curious Containers (CC)](https://www.curious-containers.cc/).
- DVC allows you to define stages that describe which command line to call, what dependencies, output, and metrics exist for this command. With the defined stages, DVC knows the pipeline of executions and ensures that changed dependencies are executed again.
- CC is used in the backend to run your scripts in a docker on your cluster system.


## Install
```
pip install cc-faice
pip install https://github.com/mastaer/dvc-cc/releases/tag/dvc_cc-0.2.0-py3-none-any.whl
```

## Basic Usage

### Init

1. You should create a git repository
2. Run the command: `dvc-cc init`
3. Create a directory on a storage server and add a DVC remote to this directory. I.e.:
    ```
    # dvc remote add -d dvc_connection ssh://annusch@avocado01.f4.htw-berlin.de/data/ldap/jonas/test_pcam
    dvc remote add -d dvc_connection ssh://YOURUSERNAME@YOURSERVER/PATHTODIRECTORY
    dvc remote modify dvc_connection ask_password true
    dvc push
    ```
4. check and set the settings with `dvc-cc setting all`

### Define your pipeline with DVC

You can use DVC to define your pipeline.

```
dvc run -d DEPENDENCY -o SOMEOUTPUT -m SOMEMETRIC.json --no-exec python train.py
```

### RUN the defined pipeline on the server
```
dvc-cc run THE_EXPERIMENT_NAME
```

### check status
```
# get an overview over all started jobs:
dvc-cc status --all

# get a detailed view of the last runned job.
dvc-cc status -d
```


## Acknowledgements
The CAMELYON CNNs software is developed at CBMI (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6).


