import numpy as np
import pylab
import sys
from datetime import datetime

sys.path.append('./wrapper')
import bhtsnewrapper

print('Loading data...')
data = np.loadtxt("./data/mnist2500_X.txt")
labels = np.loadtxt("./data/mnist2500_labels.txt")
figfile = './results/bhtsne_wrapper_demo.png'

print('Processing...')
start = datetime.now()
embedding_array = bhtsnewrapper.run_bh_tsne(data, initial_dims=data.shape[1])
end = datetime.now()
elapsedTime = (end - start).total_seconds()
print('Process time ', elapsedTime, 's')


pylab.scatter(embedding_array[:, 0], embedding_array[:, 1], 20, labels)
pylab.savefig(figfile)
pylab.show()
