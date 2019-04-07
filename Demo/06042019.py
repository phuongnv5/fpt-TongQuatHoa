import arcpy
import os
import json
import time

arcpy.env.overwriteOutput = True
in_workspace = "C:\\Generalize_25_50\\50K_Process.gdb"
out_workspace = "C:\\Generalize_25_50\\50K_Final.gdb"
urlFile = "C:\\Config\\ConfigTools.json"

try:
    arcpy.AddMessage("\n# Reading...")
    f = open(urlFile)
    dataJSON = json.load(f)
    f.close()
    arcpy.AddMessage("\n# Scanning...")
    fcs = []
    for ele in arcpy.Describe(in_workspace).children:
        for eleSub in arcpy.Describe(ele.catalogPath).children:
            if eleSub.featureType == "Simple" and (eleSub.shapeType == "Polyline" or eleSub.shapeType == "Polygon"):
                temp = {
                    "featureDataSet": ele.baseName,
                    "baseName": eleSub.baseName,
                    "shapeType": eleSub.shapeType,
                    "catalogPath": eleSub.catalogPath
                }
                fcs.append(temp)
    arcpy.SetProgressor("Step", "Simplify, Smooth...", 0, len(fcs), 1)
    i = 0
    for ele in fcs:
        arcpy.SetProgressorLabel("Simplify, Smooth: {0}\\{1}...".format(ele["featureDataSet"], ele["baseName"]))
        arcpy.AddMessage("# Simplify, Smooth: {0}\\{1}...".format(ele["featureDataSet"], ele["baseName"]))
        for eleSub in dataJSON:
            if eleSub["featureDataSet"] == ele["featureDataSet"] and eleSub["baseName"] == ele["baseName"]:
                arcpy.AddMessage("\t# Using Tool: {0}".format(eleSub["usingTool"]))
                arcpy.AddMessage("\t# Simplify: {0}".format(eleSub["usingParameter"][0]))
                arcpy.AddMessage("\t# Smooth: {0}".format(eleSub["usingParameter"][1]))
        arcpy.SetProgressorPosition(i)
        i += 1
        time.sleep(2)
    
except:
    arcpy.AddError(arcpy.GetMessages())