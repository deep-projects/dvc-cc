import sys
sys.path.insert(0,'code')
sys.path.insert(0,'code/helper')

import numpy as np
import os

from argparser import *
from _utility import get_name_of_experiment

args = get_args()
name_of_experiment = 'train_' + get_name_of_experiment(args)


print(' !!! RUN AN EXPERIMENT with the name: ' + name_of_experiment + ' !!!')

is_test = args.is_test_run


# load your train data
data = np.load('data/mydata.npy')[:-500]

# build your model
num_of_samples = 2 if is_test else 10
factor = 5.0

# train your model
batch = np.random.choice(data, num_of_samples) * factor
expected_value = batch.mean()

# save your results (i.e. tensorboard file)
if not is_test:
    np.save('result/' + name_of_experiment + '.npy', batch)

# save your model (i.e. your keras cnn model)
if not is_test:
    np.save('model/' + name_of_experiment + '.npy', [num_of_samples, factor, expected_value])

# calculate the summaries
l1_loss = np.abs(batch - expected_value).sum()

# save the summary
l1_loss_dict = {'L1_Train' : l1_loss}
data = json.dumps(l1_loss_dict, cls=json_encoder.MyEncoder)
if not is_test:
    f = open('metrics/'+name_of_experiment+'.json', "w")
    f.write(data)
    f.close()

