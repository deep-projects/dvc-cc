import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int,default=None)
parser.add_argument('--num_of_hidden_layers', type=int,default=1)
parser.add_argument('--num_of_kernels', type=int,default=64)
parser.add_argument('--dropout_rate', type=float,default=0.2)
parser.add_argument('--learning_rate', type=float,default=0.001)
parser.add_argument('--activation_function', type=str,default='relu')
parser.add_argument('--batch_size', type=int,default=1000)
parser.add_argument('--epochs', type=int,default=2)
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
  # Write TensorBoard logs to `./tensorboard` directory
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
model.fit(x_train, y_train, epochs=args.epochs, batch_size=args.batch_size, validation_split=0.1,
          callbacks=callbacks, verbose=2)
################
### TEST MODEL
################
model.evaluate(x_test, y_test, verbose=2)

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
