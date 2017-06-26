import pandas as pd
import requests as rq
import os
from time import sleep



baseURL = "https://maps.googleapis.com/maps/api/streetview?"
size = "size=640x480&"
location = "location="
keyfrag = "&key="
imgDir = "../streetview/PPImages/"
logFile = "dlLog.log"


def getDownloadedList():
    files = os.listdir(imgDir)
    fileList = []
    for f in files:
        fileList.append(f.split('.')[0])
    return fileList

def getKey(path):
    with open(path , 'rb') as f:
        key = f.readline()
    return key

if __name__ == "__main__":
    df = pd.read_csv("../streetview/votes.csv")
    history_files = getDownloadedList()
    key = getKey('api2.key')
    print "using key " + key
    i = 0
    sl = 0.5
    for index , row in df.iterrows():
        ID = row['left_id']
        if ID not in history_files:
            imgLoc = str(row['left_lat']) + ',' + str(row['left_long'])
            imgName = imgDir + ID + ".jpg"
            url = baseURL + size + location + imgLoc + keyfrag + key
            r = rq.get(url)
            if r.status_code == 200:
                with open(imgName, 'wb') as f:
                    f.write(r.content)
                print " Downloaded," + ID
                history_files.append(ID)
                sleep(sl)
                i+=1
            else:
                with open(logFile, 'a') as f:
                    line = "failed," + ID + ',' + str(r.status_code) + "\n"
                    f.write(line)
                print "Failed ," + ID


        ID = row['right_id']
        if ID not in history_files:
            imgLoc = str(row['right_lat']) + ',' + str(row['right_long'])
            imgName = imgDir + ID + ".jpg"
            url = baseURL + size + location + imgLoc + keyfrag + key
            r = rq.get(url)
            if r.status_code == 200:
                with open(imgName, 'wb') as f:
                    f.write(r.content)
                print " Downloaded," + ID
                history_files.append(ID)
                sleep(sl)
                i+=1
            else:
                with open(logFile, 'a') as f:
                    line = "failed,"+ ID + ',' + str(r.status_code) + "\n"
                    f.write(line)
                print "Failed ," + ID
        
        if i > 30900:
            with open(logFile, 'a') as f:                                                                                       
                line = "Reached Daily limit" + "\n"                                                          
                f.write(line)
            exit(0)
