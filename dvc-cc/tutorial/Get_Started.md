# Get Started

## 1) Create an empty GIT-Repository
Create an empty [github](https://github.com/) or [Gitlab](https://gitlab.com/) repository and change the directory to the empty git repository.

## 2) Download source code
Now you could write your own script that you want to run on the cluster. For this tutorial you can do the following lines of code to get a source code:
```bash
mkdir source
wget -o source/train.py https://github.com/deep-projects/dvc-cc/blob/master/dvc-cc/tutorial/train.py
```
This script gets some parameters, train a network and save tensorflow data, the model and metric files.
![Here is an image shown that describes the input parameters and output files of this script.](get_started_pipeline.png)

## 3) Init DVC-CC
Before you start to work with DVC-CC you need to configure DVC-CC for this project. You can do this with:
```bash
dvc-cc init
```
If you have access to the deep.TEACHING cluster you can leave everything to the default value, except the number of GPUs, set this to 1.

> **Even more**: On [this site](_settings.md) you can find all informations about the settings of DVC-CC.

## 4) Build the DVC-CC hyperopt-file.

> **Even more**: <details><summary>After Execution</summary>
<p>

**Without** DVC-CC we would calling the script multiple times with different parameters to get multiple results and compare this
hyperparameters. I.e.:

- call: "python source/train.py --num-of-kernels 32"
- call: "python source/train.py --num-of-kernels 64"
- call: "python source/train.py --num-of-kernels 64 --activation_function tanh"
- ...

This proceed has multiple problems that needs to solve:
1. You need to make sure that the output of your script gets not overwritten
    and make the name memorable.
    - How do you make clear which parameters and input files you used?
    - What if you want to run it multiple times?
    - How to you make clear, how the source code looked as the output files was created?
2. This workflow works if you run your script on one computer and start one job at a time. But if you have access to a cluster
    you would like to run the experiments in parallel.
    
This two problems are the reason why DVC-CC exists. DVC-CC is a wrapper that make it easy to integrate DVC with CC.
**DVC** can handle all problems that are described at the first point by desribing processing pipeline and saving checksumes to
each dependency and output file, to make sure that the pipeline is unchanged. **CC** is a infrastructure software that
used the RED file for describing a job that can be sent to a cluster where it gets exectured.

You can think DVC-CC as a high level wrapper to make it easy to write everytime a reproduceable code by using DVC with GIT
and send jobs over the CC interface to the cluster.

</p>
</details>








All the scripts

To archive our goal of a reproduceable pipeline we need to define it

In this step we define the pipeline that describes what needs to be run to


```bash
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -m summary.yml \
                    -f train.dvc \
                    "python source/train.py --num_of_kernels {{nk}} --activation_function {{af}}"
```

!TODO: Screenshot of the setting of the parameters!

| name | <sup>saved in git</sup> | <sup>saved in dvc cache</sup> | <sup>save the checksum</sup> | <sup>description</sup>                                                                                       |
|:----:|:------------:|:------------------:|:-----------------:|---------------------------------------------------------------------------------------------------|
|  -d  |     <sup>False</sup>    |        <sup>False</sup>       |        <sup>True</sup>       | <sup>You use this to define dependencies (inputs) or everything from what this stage depends on.</sup>       |
|  -o  |     <sup>False</sup>    |        <sup>True</sup>        |        <sup>True</sup>       | <sup>Large output files or folders</sup>                                                                                |
|  -O  |     <sup>True</sup>     |        <sup>False</sup>       |        <sup>True</sup>       | <sup>Small output files or folders </sup>                                                                               |
|  -m  |     <sup>True</sup>     |        <sup>True</sup>        |        <sup>True</sup>       | <sup>Metrics are output files but have a special feature that you can use with `dvc metrics show`</sup>  |
|  -M  |     <sup>True</sup>     |        <sup>False</sup>       |        <sup>True</sup>       | <sup>Metrics see above. Find more information about metrics [here](https://dvc.org/doc/commands-reference/metrics-show). </sup>  

> **Even more**: Can you set all parameters? For help and a solution go to [this site](_set_all_parameters.md).

> **Even more**: If you have multiple scripts (i.e., preprocessing.py, train.py and eval.py) you can create one or multiple pipelines. See [this site](_complex_pipeline.md) for more information.

> **Even more**: We created here .hyperopt-files. If you do not have any hyper parameters and want to use DVC directly you can take a look at [this site](_only_dvc.md).


#
#
#
#
#
#
#
#


## 1) Create your first DVC-CC-Project
Create a **Git** repository at github or gitlab. Next go to the repository and run `dvc-cc init`. This will set interactively all information that dvc-cc needs to work. All the information describes the connection to CC, DVC and which server and docker setting do you need to run your code. As CBMI user you can use the default values. Just use your correct CBMI username and use one GPU for this script.
```
dvc-cc init
```

## 2) Create the source code

No we can create some code like a simple fully connected network. Just create the file **source/train.py**:
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int,default=None)
parser.add_argument('--num_of_hidden_layers', type=int,default=1)
parser.add_argument('--num_of_kernels', type=int,default=64)
parser.add_argument('--dropout_rate', type=float,default=0.2)
parser.add_argument('--learning_rate', type=float,default=0.001)
parser.add_argument('--activation_function', type=str,default='relu')
parser.add_argument('--batch_size', type=int,default=1000)
parser.add_argument('--epochs', type=int,default=10)
parser.add_argument('--dataset', type=str,default='fashion_mnist')
args = parser.parse_args()

import numpy as np
if not args.seed is None:
    np.random.seed(args.seed)
import tensorflow as tf
if not args.seed is None:
    tf.random.set_seed(args.seed+100)
import yaml
import time

################
### LOAD DATASET
################
if args.dataset not in ['fashion_mnist','mnist','cifar10','cifar100']:
    raise ValueError('Did not find a dataset with this Name.')

num_of_tries = 0
while num_of_tries < 100:
    try:
        if args.dataset == 'fashion_mnist':
            (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
            num_of_tries = 99999999
        elif args.dataset == 'mnist':
            (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
            num_of_tries = 99999999
        elif args.dataset == 'cifar10':
            (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
            num_of_tries = 99999999
        elif args.dataset == 'cifar100':
            (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar100.load_data()
            num_of_tries = 99999999
        else:
            raise ValueError('Did not find a dataset with this Name.')
    except:
        if num_of_tries < 12:
            num_of_tries += 1
            time.sleep(10)
        else:
            raise ValueError('The data could not be downloaded.')

x_train, x_test = x_train / 255.0, x_test / 255.0

################
### BUILD MODEL
################
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Flatten(input_shape=x_train.shape[1:]))
for i in range(args.num_of_hidden_layers):
    model.add(tf.keras.layers.Dense(args.num_of_kernels, activation=args.activation_function))
    model.add(tf.keras.layers.Dropout(args.dropout_rate))
model.add(tf.keras.layers.Dense(y_train.max()+1, activation='softmax'))

model.summary()

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
              loss='sparse_categorical_crossentropy',
              metrics=['acc'])

callbacks = [
  # Interrupt training if `val_loss` stops improving for over 2 epochs
  tf.keras.callbacks.EarlyStopping(patience=100, monitor='val_loss'),
  # Write TensorBoard logs to `./logs` directory
  tf.keras.callbacks.TensorBoard(log_dir='tensorboard'),
  tf.keras.callbacks.ModelCheckpoint(
            filepath='model.h5',
            save_best_only=True,
            monitor='val_loss',
            verbose=2)
]

################
### TRAIN MODEL
################
model.fit(x_train, y_train, epochs=args.epochs, batch_size=args.batch_size, validation_split=0.1,callbacks=callbacks)
################
### TEST MODEL
################
model.evaluate(x_test, y_test)

################
### SAVE SUMMARY
################
summary = {'loss': float(np.min(model.history.history['loss'])),
            'val_loss': float(np.min(model.history.history['val_loss'])),
            'acc': float(np.max(model.history.history['acc'])),
            'val_acc': float(np.max(model.history.history['val_acc']))
          }
with open('summary.yml', 'w') as f:
    yaml.dump(summary, f)
```

## 3) Build the pipeline and push it to git

There exists two ways to work with DVC-CC. First you just work with DVC like you always would do it. But the recommend way is to use DVC-CC instead for it.

### 3.1) Pure DVC
If we do not have any hyper parameter we can work easily with DVC and define the dependencies and output files of our
script. DVC will handle everything else:
```
dvc run --no-exec -d source/train.py \
                  -o tensorboard \
                  -o model.h5 \
                  -m summary.yml \
                  -f train.dvc \
                  "python source/train.py --seed 100 --num_of_hidden_layers 3 --num_of_kernels 128 --dropout_rate 0.1 --learning_rate 0.01 --activation_function relu --batch_size 512 --epochs 1000 --dataset mnist"
```
### 3.2) The DVC-CC way
Everytime we changed some dependency or parameter we would need to rerun this command. If you want do some kind of
hyperoptimization this could be very frustrating. For this kind you should use `dvc-cc hyperopt new`:
```
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -m summary.yml \
                    -f train.dvc \
                    "python source/train.py --seed {{seed:int}} --num_of_hidden_layers {{nh:int}} --num_of_kernels {{nk:int}} --dropout_rate {{dr:float}} --learning_rate {{lr:float}} --activation_function {{af:[relu,tanh]}} --batch_size {{bs:int}} --epochs {{e:int}} --dataset {{d:[mnist,fashion_mnist,cifar10,cifar100]}}"
```
It looks similar to the `dvc run` command but instead of setting the parameter you can use variables with {{A_Variable_Name}}.
In the upper case we define the types of the variable.  If you want to find out more about the parameters `-d`, `-o`, `-O`, `-m` and `-M` check the dvc documentation: https://dvc.org/doc/commands-reference/run .


    
| name | <sup>saved in git</sup> | <sup>saved in dvc cache</sup> | <sup>save the checksum</sup> | <sup>description</sup>                                                                                       |
|:----:|:------------:|:------------------:|:-----------------:|---------------------------------------------------------------------------------------------------|
|  -d  |     <sup>False</sup>    |        <sup>False</sup>       |        <sup>True</sup>       | <sup>You use this to define dependencies (inputs) or everything from what this stage depends on.</sup>       |
|  -o  |     <sup>False</sup>    |        <sup>True</sup>        |        <sup>True</sup>       | <sup>Large output files</sup>                                                                                |
|  -O  |     <sup>True</sup>     |        <sup>False</sup>       |        <sup>True</sup>       | <sup>Small output files </sup>                                                                               |
|  -m  |     <sup>True</sup>     |        <sup>True</sup>        |        <sup>True</sup>       | <sup>Metrics are also output files but have a special feature that you can use with `dvc metrics show`</sup>  |
|  -M  |     <sup>True</sup>     |        <sup>False</sup>       |        <sup>True</sup>       | <sup>Metrics see above. Find more information about metrics here: https://dvc.org/doc/commands-reference/metrics-show </sup>                                                                                |



### 3.3) Always commit and push your changes
Add the end of editing your source code or pipeline you should always commit your changes. If you do not do this, this can be lost by using dvc-cc.
```
git add -A
git commit -m 'Create the Pipeline'
git push
```
## 4) Manage your hyperparameters
You can use `dvc-cc hyperopt var all` to get an overview over your parameters. You get the name of the variable, the datatype and fix values that are set. This value you can set with:
```
dvc-cc hyperopt var e --set 1000
```
This parameter is used for the epoch and is now set to 1000. So every experiment runs maximal 1000 epochs. With `dvc-cc hyperopt var e --set None` you can set the value back to the original. All parameters that are None are our hyperparameter that we want currently analyse and make different experiments with it. You get ask to set this hyperparameter in the command `dvc-cc run`.

## 5) Run the pipeline

If the pipeline is defined we can run our job with:
```
dvc-cc run 'YourExperimentName'
```
If we used dvc-cc hyperopt the run command will ask us to set the parameter or choise a hyperoptimizator. The difference between RandomSearch-Local and RandomSearch-Global is how the drawn is done. In the RS-Local it will draw each RS-Local seperatly. You get a kind of gridsearch with randomized width of the grid. If you use instead RS-Global it will draw for each experiment the own hyperparameters. If you want to use RandomSearch, than Random-Search-Global is normally what you want.

To set the values A and B of the beta distribution you can use parallel the command `dvc-cc hyperopt plot-beta` to get a feeling for the parameter. If you just want a uniform distribution just use the values A=1 and B=1.

## 6) Check the jobs:
We can check the running job with `dvc-cc status`. There are a lot of parameters, check the help to get more information about it. Just to define some parameters:
- `-n 5` give you the information for the last 5 runs.
- `-d` gives you a detailed describtion
- `-s` gives you a summary
- `-f` shows only failed runs
- `-at` gives you the information for all runs that you ever did. You can use this to check jobs from other branches or if the CC job id is missing.
I.E.:
```
# Show the last job
dvc-cc status
# Show a summary for the last 20 jobs that was started
dvc-cc status -s -n 20
# Show a detailed output for the last job that was failed in all of your experiments.
dvc-cc status -f -d -at
```
## 7) Get the output files
```
# get all remote branches and create them local
dvc-cc git sync
# download from the DVC server the missing files and save all output files in this case all tensorboard in a tmp directory of your first job that you created.
dvc-cc output-to-tmp --allow-dir -f tensorboard -d -p 1 -r
```
Now you just could run `tensorboard --logdir=.` to combare the different results.

## 8) Hints
### 8.1) A lot of branches
DVC-CC creates alot of input and result branches. To just show your working branches just use:
```
dvc-cc git branch
```
### 8.2) Live output data
You can use `dvc-cc live-output` to mount the directory that is used for the live output of the data. You can find there log files with the std out. If you want more files to be in the live output you need to set this in the `dvc-cc run` command. I.E.:
```
dvc-cc run -l tensorboard 'YourExperimentName'
```
This will save the tensorboard in the live output. To umount the live output directory just run `dvc-cc live-output -um`.

### 8.3) Working with jupyter notebook
If you want to work with a jupyter notebook to make fast changes but run parallel larger experiments on the server you just can use DVC-CC ;-)

If you call `dvc-cc run` with the `-nb` parameter it will convert all jupyter notebook to py files so that they can be executed on the server. By defining your pipeline you would just use a .py file instead of the ipynb file.

If the first line of a cell starts with `#%% dvc-cc-hide` it will ignore this cell by converting from a jupyter notebook to a py file. If you have a multiline commend that starts with `"""dvc-cc-show` than this commend will be uncommend and will be executed on the server. With this you can define some code that only runs in your jupyter notebook or only runs on the server in the py file.

### 8.4) Large Data-Files
You can connect to some data per SSHFS to your `data` folder. This will than also connected in per SSHFS in the server.

### 8.5) Download all DVC files parallel.
Create a second git repository and create a hardlink from the second git repository .dvc/cache to the first git repository .dvc/cache. They use now the same DVC cache but can work on different branches. If this is done, you can call `dvc-cc git sync -d -l` to create a unlimited loop that download all files to the DVC cache that are needed, and create all git branches.

