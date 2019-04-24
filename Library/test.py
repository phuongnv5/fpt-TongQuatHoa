import arcpy
import os
import json
import sys
import inspect

arcpy.env.overwriteOutput = 1
urlFile = '../Config/ConfigSimplify.json'
s1 = inspect.getfile(inspect.currentframe())
s2 = os.path.dirname(s1)
s3 = os.path.dirname(s2)
print(s1)
print(s2)
print(s3)
if os.path.exists(urlFile):
    print("ok")
    fileConfig = open(urlFile)
else:
    print("not exit")
#print(sys.path.append('../DIR2'))