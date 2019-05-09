import sys
sys.path.insert(0,'code')
sys.path.insert(0,'code/helper')

import numpy as np
import os

from argparser import *
from _utility import get_name_of_experiment
import json
import json_encoder

args = get_args()
name_of_experiment = 'train_' + get_name_of_experiment(args)


print(' !!! RUN AN EXPERIMENT with the name: ' + name_of_experiment + ' !!!')

is_test = args.is_test_run


# load your test data
data = np.load('data/mydata.npy')[:-500]

# build your model and set the weights
num_of_samples = 10
factor = 5
expected_value = 25

# train the model
batch = np.random.choice(data, num_of_samples)
batch = batch * 1./factor + batch * factor
expected_value = batch.mean()

# save your results
if not is_test:
    np.save('result/' + name_of_experiment + '.npy', batch)

# save your results
if not is_test:
    np.save('model/' + name_of_experiment + '.npy', [num_of_samples, factor, expected_value])


# calculate the summaries
l1_loss = np.abs(batch - expected_value).sum()

# save the summary
if not is_test:
    l1_loss_dict = {'L1_Train' : l1_loss}
    data = json.dumps(l1_loss_dict, cls=json_encoder.MyEncoder)
    f = open('metrics/'+name_of_experiment+'.json', "w")
    f.write(data)
    f.close()

