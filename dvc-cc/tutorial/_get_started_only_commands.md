# Get Started with <img src="../../dvc_cc_logo.png" alt="drawing" width="100"/> (only commands)

## 1) Create an empty GIT-Repository 

- create an empty [GitHub](https://github.com/) or [GitLab](https://gitlab.com/) repository,
- open a console,
- (activate your DVC-CC anaconda environment,)
- pull the empty git repository and
- change the directory to your git project. 

## 2) Generate source code

```bash
mkdir source
wget -O source/train.py https://bit.ly/2krHi8E
```

## 3) Init DVC-CC
```bash
dvc-cc init
```

## 4) Build the DVC-CC hyperopt-file

```bash
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -m summary.yml \
                    -f train.dvc \
                    "python source/train.py --num_of_kernels {{nk}} --activation_function {{af}}"
```

## 5) Run the script in the cluster

```bash
git add -A
git commit -m "build the pipeline for the first test run with DVC-CC"
git push
```

```bash
dvc-cc run the_name_of_this_experiment
```

## 6) Check jobs
```bash
dvc-cc status
```

##<del> 7) The result branch</del>

## 8) Get output files from the experiments
```
dvc-cc output-to-tmp -f tensorboard -d -pos 1
```