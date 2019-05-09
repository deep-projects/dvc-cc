import numpy as np
import os

print(' !!! RUN AN EXPERIMENT with the name !!!')


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
np.save('train_model.npy', [num_of_samples, factor, expected_value])


# calculate the summaries
l1_loss = np.abs(batch - expected_value).sum()

# save the summary
l1_loss_dict = {'L1_Train' : l1_loss}
data = json.dumps(l1_loss_dict, cls=json_encoder.MyEncoder)
f = open('train_metric.json', "w")
f.write(data)
f.close()

