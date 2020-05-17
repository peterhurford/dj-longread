import joblib

import numpy as np


print('Load GloVe...')
embeddings_dict = {}
with open('data/glove.6B.300d.txt', 'r') as f:
    for line in f:
        values = line.split()
        word = values[0]
        vector = np.asarray(values[1:], 'float32')
        embeddings_dict[word] = vector

print('Saving GloVe...')
joblib.dump(embeddings_dict, 'data/glove.pkl')

print('Done!')
