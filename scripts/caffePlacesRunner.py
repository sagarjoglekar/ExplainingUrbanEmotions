from __future__ import print_function
import caffe
import sys
import os

import random
import numpy as np

import cv2


# If you get "No module named _caffe", either you have not built pycaffe or you have the wrong path.

model_root = "/datasets_1/sagarj/BellLabs/caffe_models/places/"

imagenet_mean = model_root + 'places205CNN_mean.binaryproto'

logfile = "../Data/PlacesFeatExtractStreetview.txt"


#Size of images
IMAGE_WIDTH = 227
IMAGE_HEIGHT = 227

def transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT):

    #Histogram Equalization
    img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
    img[:, :, 1] = cv2.equalizeHist(img[:, :, 1])
    img[:, :, 2] = cv2.equalizeHist(img[:, :, 2])

    #Image Resizing
    img = cv2.resize(img, (img_width, img_height), interpolation = cv2.INTER_CUBIC)

    return img


def predictImages(imgList , classprobs, model_def , model_weights):
    
    net = caffe.Net(model_def,      # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)     # use test mode (e.g., don't perform dropout)

    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape}) 
    transformer.set_transpose('data', (2,0,1))
    transformer.set_channel_swap('data', (2,1,0))
    transformer.set_raw_scale('data', 255.0)

    net.blobs['data'].reshape(1,3,IMAGE_WIDTH,IMAGE_WIDTH)


    
    for line in imgList:
    
        path = line.split(',')[0].strip()
        #true_label = line.split(',')[1]
        #path = line.strip()
        im = caffe.io.load_image(path)
        net.blobs['data'].data[...] = transformer.preprocess('data', im)
        net.forward()
        #out1 = net.blobs['prob'].data
        out2 = net.blobs['fc7'].data
        #print(out2.shape)
        #out = np.concatenate((out1,out2.reshape(1,-1)),axis =1)
        out = out2
        print(out.shape)
        with open(classprobs,'a') as f_handle:
            np.savetxt(f_handle, out , delimiter=',')
        log = line   
        print(log)    

        with open(logfile, 'a+') as f:
            print(log , file = f)
    



if __name__ == "__main__":

    imageListFile = sys.argv[1]
    classProb = sys.argv[2]
    
    if os.path.isfile(imageListFile):
        print("Reading image list .... ")
    else:
        print("no such file")
        exit(-1)
    
    imageList = []
    
    with open(imageListFile) as g:
        imageList = g.readlines()
    
    caffe.set_mode_gpu()    
    model_def = model_root + 'places205CNN_deploy_upgraded.prototxt'#'test.prototxt'
    model_weights = model_root +'places205CNN_iter_300000_upgraded.caffemodel'#'caffe_sentibank_train_iter_250000'
    
    predictImages(imageList , classProb, model_def, model_weights)
    
    
