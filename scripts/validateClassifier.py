import numpy as np
import pandas as pd 
from sklearn import cross_validation
from sklearn.cross_validation import KFold
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestClassifier 
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support , accuracy_score
import matplotlib.pyplot as plt
import scipy.stats

import sys
import lmdb
import h5py
caffe_root = '/work/sagarj/caffe-rc5/'  # this file should be run from {caffe_root}/examples (otherwise change this line)
sys.path.insert(0, caffe_root + 'python')
from collections import defaultdict
import caffe

model_root = "/work/sagarj/Work/BellLabs/caffe_models/caffe_model_1/"
# net_weights='caffe_beauty_augmented/caffe_model_beauty_city_smartAugment_fixed_iter_20000.caffemodel'
# net_weights='caffe_model_beauty_4_votes/caffe_model_1_iter_24732.caffemodel'
# net_weights = '../caffe_models/caffe_model_1/smartAugment/caffe_model_beauty_city_smartAugment_iter_15000.caffemodel'
net_weights='caffe_model_beauty_city_smartAugment_fixed_iter_20000.caffemodel'
net_definition='caffenet_deploy_1.prototxt'

test_lmdb_path = '../Data/validation_lmdb_beauty_augmented_smart/' # Test LMDB database path
mean_file_binaryproto = '../Data/citySmart1.binaryproto' # Mean image file

caffe.set_mode_gpu()
model_def = model_root+net_definition
model_weights = model_root + net_weights

net = caffe.Net(model_def,      # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)     # use test mode (e.g., don't perform dropout)

np.asarray(net.blobs['fc8'].data)

# Extract mean from the mean image file
mean_blobproto_new = caffe.proto.caffe_pb2.BlobProto()
f = open(mean_file_binaryproto, 'rb')
mean_blobproto_new.ParseFromString(f.read())
mean_image = caffe.io.blobproto_to_array(mean_blobproto_new)
f.close()

count = 0
correct = 0
labels = [] # (real,pred) -> int
preds = []
# labels_set = set()

lmdb_env = lmdb.open(test_lmdb_path)
lmdb_txn = lmdb_env.begin()
lmdb_cursor = lmdb_txn.cursor()

for key, value in lmdb_cursor:
    datum = caffe.proto.caffe_pb2.Datum()
    datum.ParseFromString(value)
    label = datum.label
    labels.append(label)
    image = caffe.io.datum_to_array(datum)
    image = image.astype(np.uint8)
    out = net.forward_all(data=np.asarray([image]) - mean_image).copy()

    plabel = out['prob']
    preds.append(plabel)
    count += 1
    
print preds[3]
pred_label = [np.argmax(i) for i in preds ]
print pred_label[2] , labels[2]
error_RF = mean_squared_error(labels, pred_label)

precision , recall , fscore , _ = precision_recall_fscore_support(labels, pred_label)


print ( precision , recall , fscore , _)
