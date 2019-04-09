import os
import json

urlFile = "C:\\TQHBD\\ArcGIS_Tools\\fpt-TongQuatHoa\\fpt-TongQuatHoa\\ConfigSimplifySmooth.json"

def returnKey(elem):
    return int(elem["OrderNumber"])

try:
    f = open(urlFile)
    dataJSON = json.load(f)
    f.close()
    print type(dataJSON)
    for item in dataJSON:
        print item["OrderNumber"]
    dataJSON.sort(key = returnKey, reverse = False)
    for item in dataJSON:
        print item["OrderNumber"]
except:
    print "Error!"