import numpy as np
import cv2
import os
import sys

def impaintMask(srcPath , mask , destFolder , identifier):
    if not os.path.exists(srcPath):
        print "Image not found"
        return
    name = srcPath.strip().split('/')[-1].split('.')[0]
    img = cv2.imread(srcPath.strip())
    fname = srcPath.str
    dst = cv2.inpaint(img,mask,3,cv2.INPAINT_TELEA)
    destPath = destFolder + "/" + name + '_' + str(identifier) + '.jpg' 
    cv2.imwrite(destPath,dst)
    print "Done inpainting %s for %s",%(srcPat,str(identifier))
    return
