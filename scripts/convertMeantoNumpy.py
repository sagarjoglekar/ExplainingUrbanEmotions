import caffe
import numpy as np
import sys
import scipy

size = (3,640,480)

if len(sys.argv) != 3:
    print "Usage: python convertMeantoNumpy.py proto.mean out.npy"
    sys.exit()

blob = caffe.proto.caffe_pb2.BlobProto()
data = open( sys.argv[1] , 'rb' ).read()
blob.ParseFromString(data)
arr = np.array( caffe.io.blobproto_to_array(blob) )
print arr.shape
interpol = np.squeeze(arr)
#interpol = scipy.misc.imresize(arr[0,:,:,:],size)
print interpol.shape
np.save( sys.argv[2] , interpol )
