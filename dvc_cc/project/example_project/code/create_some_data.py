import numpy as np
import os

print('!!! CREATE THE DATASET !!!')

if not os.path.exists("data"):
    os.mkdir('data')

np.save('data/mydata.npy', np.random.random((1000000)))
