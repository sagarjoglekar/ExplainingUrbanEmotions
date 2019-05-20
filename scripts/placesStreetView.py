# from __future__ import print_function
import caffe
import sys
import os
import pandas as pd
import random
import numpy as np
import csv
import cv2


# If you get "No module named _caffe", either you have not built pycaffe or you have the wrong path.

model_root = "/datasets_1/sagarj/BellLabs/caffe_models/places/"

imagenet_mean = model_root + 'places205CNN_mean.binaryproto'

logfile = "../Data/StreetViewPlaces.txt"


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


def predictImages(imgDict, model_def , model_weights):
    
    net = caffe.Net(model_def,      # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)     # use test mode (e.g., don't perform dropout)

    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape}) 
    transformer.set_transpose('data', (2,0,1))
    transformer.set_channel_swap('data', (2,1,0))
    transformer.set_raw_scale('data', 255.0)

    net.blobs['data'].reshape(1,3,IMAGE_WIDTH,IMAGE_WIDTH)
    finalDict = imgDict.copy()


    
    for k in imgDict:
    
        path = imgDict[k]['path']
        #true_label = line.split(',')[1]
        #path = line.strip()
        im = caffe.io.load_image(path)
        net.blobs['data'].data[...] = transformer.preprocess('data', im)
        net.forward()
        out1 = np.squeeze(net.blobs['prob'].data)
        # out2 = net.blobs['fc7'].data
        #print(out2.shape)
        #out = np.concatenate((out1,out2.reshape(1,-1)),axis =1)
        out = out1.argsort()[-5:][::-1]
        # out = np.argmax(out1)
        # print(out.shape)
        print "Processing image" + k
        print out
        finalDict[k]['places'] = out
    return finalDict



if __name__ == "__main__":
    
    ImageDir = "/datasets/sagarj/streetView/LondonImages/GreaterLondon_NoRot/"
    LondonPoints = pd.read_csv("/datasets/sagarj/streetView/LondonImages/greater_london_points.csv",header=None)
    
    classProb = sys.argv[1]
    
    imageDict = {}
    for index , row in LondonPoints.iterrows():
        ID = str(int(row[0])) + '_' + str(int(row[1]))
        if os.path.exists(ImageDir+ID):
            files = os.listdir(ImageDir+ID)
            for f in files:
                comps = f.split('.')
                imageDict[comps[0]] = {}
                imageDict[comps[0]]['path'] =  ImageDir+ID+"/"+f
                imageDict[comps[0]]['rot'] = comps[0].split('_')[-1]
    
    caffe.set_mode_gpu()    
    model_def = model_root + 'places205CNN_deploy_upgraded.prototxt'#'test.prototxt'
    model_weights = model_root +'places205CNN_iter_300000_upgraded.caffemodel'#'caffe_sentibank_train_iter_250000'
    
    finalDict = predictImages(imageDict , model_def, model_weights)
    

    with open(classProb, 'wb') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter='|')
        csvWriter.writerow(['WayID','PointID','Rotation','Top5PlaceIndex'])
        for k in finalDict:
            ids = k.split("_")
            row = [ids[0], ids[1], ids[2] , finalDict[k]['places']]
            csvWriter.writerow(row)
    print "Done wrinting CSV"
        
