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

name_of_experiment = 'eval_' + get_name_of_experiment(args)


print(' !!! RUN AN EXPERIMENT with the name: ' + name_of_experiment + ' !!!')

is_test = args.is_test_run


# load your test data
data = np.load('data/mydata.npy')[-500:]

# build your model and load the weights
[_, factor, expected_value] = np.load('model/train_' + name_of_experiment[5:] + '.npy')

# predict the data
batch = data
batch = batch * 1./factor + batch * factor

# save your results
if not is_test:
    np.save('result/' + name_of_experiment + '.npy', batch)

# calculate the summaries
l1_loss = np.abs(batch - expected_value).sum()

# save the summary
if not is_test:
    l1_loss_dict = {'L1_Test' : l1_loss}
    data = json.dumps(l1_loss_dict, cls=json_encoder.MyEncoder)
    f = open('metrics/'+name_of_experiment+'.json', "w")
    f.write(data)
    f.close()

