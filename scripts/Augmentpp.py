import pandas as pd
import requests as rq
import os
from time import sleep
import math



baseURL = "https://maps.googleapis.com/maps/api/streetview?"
size = "size=640x480&"
location = "location="
keyfrag = "&key="
imgDir = "../streetview/AugImages/"
logFile = "dlLog.log"

# headingPitchCandidates = ["&fov=90&heading=0&pitch=-20&","&fov=90&heading=0&pitch=20&",
#                           "&fov=90&heading=-30&pitch=0&","&fov=90&heading=-30&pitch=-20&","&fov=90&heading=-30&pitch=20&",
#                           "&fov=90&heading=-60&pitch=0&","&fov=90&heading=-60&pitch=-20&","&fov=90&heading=-60&pitch=20&",
#                           "&fov=90&heading=30&pitch=0&","&fov=90&heading=30&pitch=-20&","&fov=90&heading=30&pitch=20&",
#                           "&fov=90&heading=60&pitch=0&","&fov=90&heading=60&pitch=-20&","&fov=90&heading=60&pitch=20&",]


headingCandidates = ["&fov=90&heading=-30&pitch=0&", "&fov=90&heading=-60&pitch=0&",
                     "&fov=90&heading=30&pitch=0&",  "&fov=90&heading=60&pitch=0&",
                     "&fov=90&heading=15&pitch=0&" , "&fov=90&heading=-15&pitch=0&"  ]

def getOffsetLatLong(lat,lon,meters):
    #offsets in meters
    dn = meters
    de = meters
    #radius of earth in meters
    R=6378137.0
    #Coordinate offsets in radians
    dLat = dn/R
    dLon = de/(R*math.cos(math.pi*lat/180))
    #OffsetPosition, decimal degrees
    latO1 = lat + dLat * (180.0/math.pi)
    latO2 = lat - dLat * (180.0/math.pi)
    lonO1 = lon + dLon * (180.0/math.pi) 
    lonO2 = lon - dLon * (180.0/math.pi) 
    candidates = [(latO1 , lonO1),(lat,lonO1), (latO1, lon) , (latO2 , lonO2) ,(lat,lonO2), (latO2, lon)]
    print str(lat) + str(lon)
    print candidates
    return candidates
 
    

def getDownloadedList():
    idList = [ name for name in os.listdir(imgDir) if os.path.isdir(os.path.join(imgDir, name)) ]
    return idList

def getKey(path):
    with open(path , 'rb') as f:
        key = f.readline()
    return key

if __name__ == "__main__":
    df = pd.read_csv("../streetview/4votes.csv")
    #df = dfO[10:20]
    
    history_files = getDownloadedList()
    keys = ['api.key' , 'api2.key']
    key = getKey(keys[0])
    print "using key " + key
    crawled = 0
    sl = 0.5
    for index , row in df.iterrows():
        ID = row['left_id']
        if crawled > 24500:
            print "Nearing rate limit, change key"
            exit(0)
        if ID not in history_files:
            lat = row['left_lat'] 
            lon = row['left_long']
            augmentDir = imgDir + "/" + ID 
            if not os.path.exists(augmentDir):
                os.makedirs(augmentDir)
            #candidates = getOffsetLatLong(lat,lon,5)
            candidates = headingCandidates
            for i in range(len(candidates)):
                imgName = augmentDir + "/" + ID + str(i) + ".jpg"
                imgLoc = str(lat) + ',' + str(lon)
                url = baseURL + size + location + imgLoc + candidates[i] + keyfrag + key

                r = rq.get(url)
                if r.status_code == 200:
                    with open(imgName, 'wb') as f:
                        f.write(r.content)
                    print " Downloaded," + ID
                    history_files.append(ID)
                    sleep(sl)
                    crawled+=1
                else:
                    with open(logFile, 'a') as f:
                        line = "failed," + ID + ',' + str(r.status_code) + "\n"
                        f.write(line)
                    print "Failed ," + ID
        else:
            print "ID already cralwed!! " 
    
    print "Done crawling IDs" 
        
        
        
        
    
