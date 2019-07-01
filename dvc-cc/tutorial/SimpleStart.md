# Tutorial #1

## 0) Install DVC-CC
If you use work on **Apple** you need to install dulwich first:
```
TODO
```
### 0.1) Install with poetry
Download the dvc-cc git repository and go to the folder dvc-cc/dvc-cc and activate the dvc-cc environment from poetry.
```
poetry install
```
or just build a wheel package and install it with pip:
```
poetry install
pip install dist/........whl
```

### 0.2) Install it with pip
If you do not need the newest version you can use the following pip installation to install the package.
```
TODO: pip install .....
```

## 1) Create your first DVC-CC-Project
Create a **Git** repository at github or gitlab. Next go to the repository and run `dvc-cc init`. This will set interactively all information that dvc-cc needs to work. All the information describes the connection to CC, DVC and which server and docker setting do you need to run your code. As CBMI user you can use the default values. Just use your correct CBMI username and use one GPU for this script.
```
dvc-cc init
```

## 2) Create the source code

No we can create some code like a simple fully connected network. Just create the file **source/train.py**:
```
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

| name | saved in git | saved in dvc cache | save the checksum | description                                                                                       |
|:----:|:------------:|:------------------:|:-----------------:|---------------------------------------------------------------------------------------------------|
|  -d  |     False    |        False       |        True       | You use this to define dependencies (inputs) or everything from what this stage depends on.       |
|  -o  |     False    |        True        |        True       | Large output files                                                                                |
|  -O  |     True     |        False       |        True       | Small output files                                                                                |
|  -m  |     True     |        True        |        True       | Metrics are also output files but have a special feature that you can use with `dvc metrics show`  |
|  -M  |     True     |        False       |        True       | Metrics see above. Find more information about metrics here: https://dvc.org/doc/commands-reference/metrics-show                                                                                 |

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

