import arcpy
import os
import json

try:
    # Init WorkSpase #
    arcpy.env.overwriteOutput = 1
    duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb"
    duongDanDich = "C:/Generalize_25_50/50K_Final.gdb"
    urlFile = "/Config/ConfigSimplify.json"
    #Doc file config

    arcpy.AddMessage("\n# Doc file cau hinh: \"{0}\"".format(urlFile))
    if os.path.exists(urlFile):
        fileConfig = open(urlFile)
        listLayerConfig = json.load(fileConfig)
        fileConfig.close()
        #Simplify Polygon
        listPolygon = []
        for objConfig in listLayerConfig:
            if objConfig["LayerType"] == "Polygon":
                featureName = objConfig["LayerPath"][objConfig["LayerPath"].find("\\") + 1, len(objConfig["LayerPath"])]
                temp = {
                    "featureName": featureName,
                    "featureLayer": "in_memory\\" + featureName + "_Layer",
                    "featureCopy": "in_memory\\" + featureName + "_Copy",
                    "featureCopyLayer": "in_memory\\" + featureName + "_Copy_Layer",
                    "FID_XXX": "FID_" + featureName
                }
                listPolygon.append(temp)
        for element in listPolygon:
            arcpy.AddMessage("\n# Xu ly lop: {0}".format(element["featureName"]))
            layerPath = duongDanNguon + "/" +  os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
            arcpy.MakeFeatureLayer_management(inPath, elemSub["featureLayer"])




    else:
        arcpy.AddMessage("\t# Khong tim thay file cau hinh: \"{0}\"".format(urlFile))
        


    # Create Dict Polygon #
    listDictPolygon = []
    for elem in arcpy.Describe(duongDanNguon).children:
        temp = {
            "featureDataset": elem.baseName,
            "listFeature": []
        }
        for elemSub in arcpy.Describe(elem.catalogPath).children:
            if elemSub.featureType == "Simple" and elemSub.shapeType == "Polygon":
                tempSub = {
                    "featureName": elemSub.baseName,
                    "featureLayer": "in_memory\\" + elemSub.baseName + "_Layer",
                    "featureCopy": "in_memory\\" + elemSub.baseName + "_Copy",
                    "featureCopyLayer": "in_memory\\" + elemSub.baseName + "_Copy_Layer",
                    "FID_XXX": "FID_" + elemSub.baseName
                }
                temp["listFeature"].append(tempSub)
        listDictPolygon.append(temp)
    
    # ... #
    for elem in listDictPolygon:
        if len(elem["listFeature"]) == 0:
            continue
        arcpy.AddMessage("\n# Xu ly: {0}".format(elem["featureDataset"]))
        ## Make Feature Layer ##
        for elemSub in elem["listFeature"]:
            ### MakeLayerFeature ###
            inPath = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
            arcpy.MakeFeatureLayer_management(inPath, elemSub["featureLayer"])
        ## Add Field For Feature Class ##
        for elemSub in elem["listFeature"]:
            arcpy.AddField_management(elemSub["featureLayer"], elemSub["FID_XXX"], "LONG")
        ## Update Field FID_XXX ##
        for elemSub in elem["listFeature"]:
            with arcpy.da.UpdateCursor(elemSub["featureLayer"], ["OID@", elemSub["FID_XXX"]]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
        ## Copy Feature Class And Make Feature Layer ##
        for elemSub in elem["listFeature"]:
            ### CopyFeatureClass ###
            inPath = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
            arcpy.CopyFeatures_management(inPath, elemSub["featureCopy"])
            ### MakeLayerFeature ###
            arcpy.MakeFeatureLayer_management(elemSub["featureCopy"], elemSub["featureCopyLayer"])
        ## Field Mappings ##
        fieldMappings = arcpy.FieldMappings()
        enableFields = []
        for elemSub in elem["listFeature"]:
            enableFields.append(elemSub["FID_XXX"])
        for elemSub in elem["listFeature"]:
            fieldMappings.addTable(elemSub["featureCopyLayer"])
        for field in fieldMappings.fields:
            if field.name not in enableFields:
                fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
        ## Merge ##
        arcpy.AddMessage("\n\t# Merge Polygon...")
        inputsMerge = []
        for elemSub in elem["listFeature"]:
            inputsMerge.append(elemSub["featureCopyLayer"])
        #outPathMerge = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elem["featureDataset"] + "PolygonMerger")
        outPathMerge = "in_memory\\outPathMergeTemp"
        arcpy.Merge_management (inputsMerge, outPathMerge, fieldMappings)
        ## Simplify Polygon ##
        arcpy.AddMessage("\n\t# Simplify Polygon...")
        outPathSimplify = "in_memory\\outPathSimplifyTemp"
        arcpy.SimplifyPolygon_cartography(in_features = outPathMerge,
                                        out_feature_class = outPathSimplify,
                                        algorithm = "BEND_SIMPLIFY",
                                        tolerance = "50 Meters",
                                        error_option = "NO_CHECK",
                                        collapsed_point_option = "NO_KEEP")
        ## MakeLayerFeature ##
        outPathSimplifyLayer = "in_memory\\outPathSimplifyTempLayer"
        arcpy.MakeFeatureLayer_management(outPathSimplify, outPathSimplifyLayer)
        ## Update Shape Feature Class ##
        arcpy.AddMessage("\n\t# Update Shape Feature Class:")
        for elemSub in elem["listFeature"]:
            arcpy.AddMessage("\t\t# Update {0}...".format(elemSub["featureName"]))
            ### MakeLayerFeature ###
            inPath = os.path.join(os.path.join(duongDanDich, elem["featureDataset"]), elemSub["featureName"])
            arcpy.MakeFeatureLayer_management(inPath, elemSub["featureLayer"])
            ### Select ###
            strQuery = elemSub["FID_XXX"] + " IS NOT NULL"
            arcpy.SelectLayerByAttribute_management(outPathSimplifyLayer, "NEW_SELECTION", strQuery)
            ### Copy To Table Temp ###
            outTableTemp = "in_memory\\outTableTemp"
            arcpy.CopyFeatures_management(outPathSimplifyLayer, outTableTemp)
            ### ... ###
            with arcpy.da.UpdateCursor(elemSub["featureLayer"], ["OID@", "SHAPE@"]) as cursor:
                for row in cursor:
                    found = False
                    with arcpy.da.UpdateCursor(outTableTemp, [elemSub["FID_XXX"], "SHAPE@"]) as cursorSub:
                        for rowSub in cursorSub:
                            if row[0] == rowSub[0]:
                                found = True
                                row[1] = rowSub[1]
                                cursor.updateRow(row)
                                cursorSub.deleteRow()
                                break
                    if found == False:
                        cursor.deleteRow()

    # Done #
    arcpy.AddMessage("\n# Done!!!")
except:
    arcpy.AddMessage(arcpy.GetMessages())
finally:
    arcpy.Delete_management("in_memory")
return