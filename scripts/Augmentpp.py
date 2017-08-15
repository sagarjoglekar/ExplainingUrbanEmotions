import pandas as pd
import requests as rq
import os
from time import sleep
import math



baseURL = "https://maps.googleapis.com/maps/api/streetview?"
size = "size=640x480&"
location = "location="
keyfrag = "&key="
imgDir = "/datasets/sagarj/streetView/Translational_city_test/"
logFile = "dlLog.log"
saveFile = "../streetview/TranslateTest.csv"

# headingPitchCandidates = ["&fov=90&heading=0&pitch=-20&","&fov=90&heading=0&pitch=20&",
#                           "&fov=90&heading=-30&pitch=0&","&fov=90&heading=-30&pitch=-20&","&fov=90&heading=-30&pitch=20&",
#                           "&fov=90&heading=-60&pitch=0&","&fov=90&heading=-60&pitch=-20&","&fov=90&heading=-60&pitch=20&",
#                           "&fov=90&heading=30&pitch=0&","&fov=90&heading=30&pitch=-20&","&fov=90&heading=30&pitch=20&",
#                           "&fov=90&heading=60&pitch=0&","&fov=90&heading=60&pitch=-20&","&fov=90&heading=60&pitch=20&",]


# headingCandidates = ["&fov=90&heading=15&pitch=0&" , "&fov=90&heading=-15&pitch=0&"
#                      "&fov=90&heading=-30&pitch=0&", "&fov=90&heading=30&pitch=0&",  
#                      "&fov=90&heading=-60&pitch=0&", "&fov=90&heading=60&pitch=0&",
#                      "&fov=90&heading=90&pitch=0&", "&fov=90&heading=-90&pitch=0&",
#                      "&fov=90&heading=120&pitch=0&", "&fov=90&heading=-120&pitch=0&",]

#headingCandidates = ["&fov=90&heading=0&pitch=0&" , "&fov=90&heading=-15&pitch=0&", "&fov=90&heading=15&pitch=0&" ]

headingCandidates = ["&fov=90&heading=0&pitch=0&"]
offsetMeters = [0 , 20 , 40 , 60 ]
#offsetMeters = [0]

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
    candidates = [ (latO1 , lonO1), (latO2 , lonO2) ]
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
    df = pd.read_csv("../streetview/easternCities.csv")
    #df = dfO[10:20]
    if os.path.exists(saveFile):
        saveDf = pd.read_csv(saveFile)
    else:
        saveDf = pd.DataFrame({'key':0 , 'disp':0 , 'path':[""]})
    
    history_files = getDownloadedList()
    keys = ['api.key' , 'api2.key', 'api3.key']
    key = getKey(keys[1])
    print "using key " + key
    crawled = 0
    sl = 1
    idCrawled = 0
    for index , row in df.iterrows():
        ID = row['left_id']
        if crawled > 24500:
            print "Nearing rate limit, change key"
            saveDf.to_csv(saveFile)
            exit(0)
        if ID not in history_files:
            lat = row['left_lat'] 
            lon = row['left_long']
            augmentDir = imgDir + "/" + ID 
            if not os.path.exists(augmentDir):
                os.makedirs(augmentDir)
            offsetCandidates = []
            
            for d in offsetMeters:
                offsetCandidates = offsetCandidates + getOffsetLatLong(lat,lon,d)
            candidates = headingCandidates
            
            for j in range(len(offsetCandidates)):
                displacement = j/2
                imagePaths = []
                for i in range(len(candidates)): 
                    #displacement = i/2
                    imgName = augmentDir + "/" + ID + "_" + str(j) + "_"  + str(i) + '_' + str(displacement) + ".jpg"
                    imagePaths.append(imgName)
                    #imgLoc = str(lat) + ',' + str(lon)
                    imgLoc = str(offsetCandidates[j][0]) + ',' + str(offsetCandidates[j][1])
                    url = baseURL + size + location + imgLoc + candidates[i] + keyfrag + key
                    print url

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
                d = {'key':ID , 'disp':displacement , 'path':imagePaths}
                df = pd.DataFrame(data=d)
                saveDf = saveDf.append(df)
            idCrawled+=1
            if idCrawled >= 3000:
                print "Done crawling test set"
                saveDf.to_csv(saveFile)
                exit(0)

        else:
            print "ID already cralwed!! " 
        
    
    print "Done crawling IDs" 
        
        
        
        
    
