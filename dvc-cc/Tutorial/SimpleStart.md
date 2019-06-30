# DVC-CC: A simple tutorial

## Init DVC-CC
First you need to create a new git repository and init DVC-CC with:
```
dvc-cc init
```

## Create the pipeline

In the second step you need some code for testing. source/train.py could look like this:
```
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int,default=None)
parser.add_argument('--num_of_hidden_layers', type=int,default=1)
parser.add_argument('--num_of_kernels', type=int,default=64)
parser.add_argument('--dropout_rate', type=float,default=0.2)
parser.add_argument('--learning_rate', type=float,default=0.1)
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

################
### LOAD DATASET
################
if args.dataset == 'fashion_mnist':
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
elif args.dataset == 'mnist':
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
elif args.dataset == 'cifar10':
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
elif args.dataset == 'cifar100':
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar100.load_data()
else:
    raise ValueError('Did not find a dataset with this Name.')

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
  tf.keras.callbacks.EarlyStopping(patience=10, monitor='val_loss'),
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
Now we commit and push our source to git.
```
git add -A
git commit -m 'Create the Pipeline'
git push
```
If we do not have any hyper parameter we can work easily with DVC and define the dependencies and output files of our
script. DVC will handle everything else.
```
dvc run --no-exec -d source/train.py -o tensorboard -o model.h5 -m summary.yml -f train.dvc "python source/train.py --seed 100 --num_of_hidden_layers 3 --num_of_kernels 128 --dropout_rate 0.1 --learning_rate 0.01 --activation_function relu --batch_size 512 --epochs 1000 --dataset mnist"
```
Everytime we changed some dependency or parameter we would need to rerun this command. If you want do some kind of
hyperoptimization this could be very frustrating. For this kind you should use `dvc-cc hyperopt new`:
```
dvc-cc hyperopt new -d source/train.py -o tensorboard -o model.h5 -m summary.yml -f train.dvc "python source/train.py --seed {{seed:in}} --num_of_hidden_layers {{nh:in}} --num_of_kernels {{nk:in}} --dropout_rate {{dr:fl}} --learning_rate {{lr:fl}} --activation_function {{af:[relu,tanh]}} --batch_size {{bs:in}} --epochs {{e:in}} --dataset {{d:[mnist,fashion_mnist,cifar10,cifar100]}}"
```
It looks similar to the `dvc run` command but instead of setting the parameter you can use variables with {{A_Variable_Name}}.
In the upper case we define the types of the variable. 

## Run the pipeline and check the results

If the pipeline is defined we can run our job with:
```
dvc-cc run -r 2 'YourExperimentName'
```
If we used dvc-cc hyperopt the run command will ask us to set the parameter or choise a hyperoptimizator.

If everything worked well, we can check the status of the job:
```
dvc-cc status -at -n 5
dvc-cc status -f -d -at
```

`dvc-cc git branch` is the same as `git branch` but will ignore all branches that was created from dvc-cc.
```
dvc-cc git branch
```
If you want to check the output of the result branches you can get all output files with:
```
dvc-cc git sync
dvc-cc output-to-tmp --allow-dir -f tensorboard -d -p 14 -r
```
