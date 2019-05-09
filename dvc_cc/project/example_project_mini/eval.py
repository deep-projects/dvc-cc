import numpy as np
import os
import json
import helper as json_encoder

print(' !!! RUN AN eval.py !!!')


# load your test data
data = np.load('mydata.npy')[-500:]

# build your model and load the weights
[_, factor, expected_value] = np.load('train_model.npy')

# predict the data
batch = data
batch = batch * 1./factor + batch * factor

# calculate the summaries
l1_loss = np.abs(batch - expected_value).sum()

# save the summary
l1_loss_dict = {'L1_Test' : l1_loss}
data = json.dumps(l1_loss_dict, cls=json_encoder.MyEncoder)
f = open('test_metric.json', "w")
f.write(data)
f.close()

