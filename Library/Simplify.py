import arcpy
import os
import json

try:
    # Init WorkSpase #
    arcpy.env.overwriteOutput = 1
    duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb"
    duongDanDich = "C:/Generalize_25_50/50K_Final.gdb"
    urlFile = "Config/ConfigSimplify.json"
    _algorithm = "BEND_SIMPLIFY"
    _tolerance = "50 Meters"
    _error_option = "NO_CHECK"
    _collapsed_point_option = "NO_KEEP"
    #Doc file config

    arcpy.AddMessage("\n# Doc file cau hinh: \"{0}\"".format(urlFile))
    if os.path.exists(urlFile):
        fileConfig = open(urlFile)
        listLayerConfig = json.load(fileConfig)
        fileConfig.close()
        ############################### Simplify Polygon ########################################
        
        arcpy.AddMessage("\n# Bat dau Simplify Polygon")
        listPolygon = []
        fieldMappings = arcpy.FieldMappings()
        enableFields = []
        inputsMerge = []
        for objConfig in listLayerConfig:
            if objConfig["LayerType"] == "Polygon" and objConfig["RunStatus"] == "True":
                temp = {
                    "LayerType": objConfig["LayerType"],
                    "DatasetName": objConfig["DatasetName"],
                    "LayerName": objConfig["LayerName"],
                    "featureLayer": "in_memory\\" + objConfig["LayerName"] + "_Layer",
                    "featureCopy": "in_memory\\" + objConfig["LayerName"] + "_Copy",
                    "featureCopyLayer": "in_memory\\" + objConfig["LayerName"] + "_Copy_Layer",
                    "FID_XXX": "FID_" + objConfig["LayerName"]
                }
                listPolygon.append(temp)
            elif objConfig["LayerType"] == "Polyline" and objConfig["RunStatus"] == "True":
                arcpy.AddMessage("\n# Buffer lop: \"{0}\"".format(objConfig["LayerName"]))
                layerPath = duongDanNguon + "/" +  objConfig["DatasetName"] + "/" + objConfig["LayerName"]
                arcpy.Buffer_analysis(layerPath, layerPath + "_Buffer", "0.01 Meters")
                temp = {
                    "LayerType": objConfig["LayerType"],
                    "DatasetName": objConfig["DatasetName"],
                    "LayerName": objConfig["LayerName"] + "_Buffer",
                    "featureLayer": "in_memory\\" + objConfig["LayerName"] + "_Buffer_Layer",
                    "featureCopy": "in_memory\\" + objConfig["LayerName"] + "_Buffer_Copy",
                    "featureCopyLayer": "in_memory\\" + objConfig["LayerName"] + "_Buffer_Copy_Layer",
                    "FID_XXX": "FID_" + objConfig["LayerName"]
                }
                listPolygon.append(temp)
        
        for element in listPolygon:
            arcpy.AddMessage("\n# Xu ly lop: {0}".format(element["LayerName"]))
            layerPath = duongDanNguon + "/" +  element["DatasetName"] + "/" + element["LayerName"]
            arcpy.MakeFeatureLayer_management(layerPath, element["featureLayer"])
            arcpy.AddField_management(element["featureLayer"], element["FID_XXX"], "LONG")
            with arcpy.da.UpdateCursor(element["featureLayer"], ["OID@", element["FID_XXX"]]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
            arcpy.CopyFeatures_management(layerPath, element["featureCopy"])
            arcpy.MakeFeatureLayer_management(element["featureCopy"], element["featureCopyLayer"])
            ## Field Mappings ##
            enableFields.append(element["FID_XXX"])
            fieldMappings.addTable(element["featureCopyLayer"])
            inputsMerge.append(element["featureCopyLayer"])
        for field in fieldMappings.fields:
            if field.name not in enableFields:
                fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
        ## Merge ##
        arcpy.AddMessage("\n# Merge Polygon...")
        outPathMerge = "in_memory\\outPathMergeTemp"
        arcpy.Merge_management (inputsMerge, outPathMerge, fieldMappings)
        ## Simplify Polygon ##
        arcpy.AddMessage("\n# Simplify Polygon...")
        outPathSimplify = "in_memory\\outPathSimplifyTemp"
        arcpy.SimplifyPolygon_cartography(in_features = outPathMerge,
                                        out_feature_class = outPathSimplify,
                                        algorithm = _algorithm,
                                        tolerance = _tolerance,
                                        error_option = _error_option,
                                        collapsed_point_option = _collapsed_point_option)
        ## MakeLayerFeature ##
        outPathSimplifyLayer = "in_memory\\outPathSimplifyTempLayer"
        arcpy.MakeFeatureLayer_management(outPathSimplify, outPathSimplifyLayer)
        ## Update Shape Feature Class ##
        arcpy.AddMessage("\n# Update Shape Feature Class:")
        for element in listPolygon:
            arcpy.AddMessage("\n\t# Update {0}...".format(element["LayerName"]))
            ### MakeLayerFeature ###
            layerPath = duongDanNguon + "/" +  element["DatasetName"] + "/" + element["LayerName"]
            arcpy.MakeFeatureLayer_management(layerPath, element["featureLayer"])
            ### Select ###
            strQuery = element["FID_XXX"] + " IS NOT NULL"
            arcpy.SelectLayerByAttribute_management(outPathSimplifyLayer, "NEW_SELECTION", strQuery)
            ### Copy To Table Temp ###
            outTableTemp = "in_memory\\outTableTemp"
            arcpy.CopyFeatures_management(outPathSimplifyLayer, outTableTemp)
            ### ... ###
            with arcpy.da.UpdateCursor(element["featureLayer"], ["OID@", "SHAPE@"]) as cursor:
                for row in cursor:
                    found = False
                    with arcpy.da.UpdateCursor(outTableTemp, [element["FID_XXX"], "SHAPE@"]) as cursorSub:
                        for rowSub in cursorSub:
                            if row[0] == rowSub[0]:
                                found = True
                                row[1] = rowSub[1]
                                cursor.updateRow(row)
                                cursorSub.deleteRow()
                                break
                    if found == False:
                        cursor.deleteRow()
        arcpy.AddMessage("\n# Hoan thanh Simplify Polygon!!!")
        
        
        ############################################## Simplify Line #############################
        arcpy.AddMessage("\n# Bat dau Simplify Line")
        listPolyLine = []
        fieldMappingLine = arcpy.FieldMappings()
        enableFieldLine = []
        inputsMergeLine = []
        for objConfig in listLayerConfig:
            if objConfig["LayerType"] == "Polyline" and objConfig["RunStatus"] == "True":
                temp = {
                    "LayerType": objConfig["LayerType"],
                    "DatasetName": objConfig["DatasetName"],
                    "LayerName": objConfig["LayerName"],
                    "featureLayer": "in_memory\\" + objConfig["LayerName"] + "_Layer",
                    "featureCopy": "in_memory\\" + objConfig["LayerName"] + "_Copy",
                    "featureCopyLayer": "in_memory\\" + objConfig["LayerName"] + "_Copy_Layer",
                    "FID_XXX": "FID_" + objConfig["LayerName"]
                }
                listPolyLine.append(temp)
        
        for element in listPolyLine:
            arcpy.AddMessage("\n# Xu ly lop: {0}".format(element["LayerName"]))
            layerPath = duongDanNguon + "/" +  element["DatasetName"] + "/" + element["LayerName"]
            arcpy.MakeFeatureLayer_management(layerPath, element["featureLayer"])
            arcpy.AddField_management(element["featureLayer"], element["FID_XXX"], "LONG")
            with arcpy.da.UpdateCursor(element["featureLayer"], ["OID@", element["FID_XXX"]]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
            arcpy.CopyFeatures_management(layerPath, element["featureCopy"])
            arcpy.MakeFeatureLayer_management(element["featureCopy"], element["featureCopyLayer"])
            ## Field Mappings ##
            enableFieldLine.append(element["FID_XXX"])
            fieldMappingLine.addTable(element["featureCopyLayer"])
            inputsMergeLine.append(element["featureCopyLayer"])
        for field in fieldMappingLine.fields:
            if field.name not in enableFieldLine:
                fieldMappingLine.removeFieldMap(fieldMappingLine.findFieldMapIndex(field.name))
        ## Merge ##
        arcpy.AddMessage("\n# Merge Polyline...")
        outPathMerge = "in_memory\\outPathMergeTemp"
        arcpy.Merge_management (inputsMergeLine, outPathMerge, fieldMappingLine)
        ## Simplify Polygon ##
        arcpy.AddMessage("\n# Simplify Polyline...")
        outPathSimplify = "in_memory\\outPathSimplifyTemp"
        arcpy.SimplifyLine_cartography(in_features = outPathMerge, 
                out_feature_class = outPathSimplify, 
                algorithm = _algorithm, 
                tolerance = _tolerance,  
                collapsed_point_option = _collapsed_point_option)
        ## MakeLayerFeature ##
        outPathSimplifyLayer = "in_memory\\outPathSimplifyTempLayer"
        arcpy.MakeFeatureLayer_management(outPathSimplify, outPathSimplifyLayer)
        ## Update Shape Feature Class ##
        arcpy.AddMessage("\n# Update Shape Feature Class:")
        for element in listPolyLine:
            if element["LayerType"] == "Polyline":
                arcpy.AddMessage("\n\t# Update {0}...".format(element["LayerName"]))
                ### MakeLayerFeature ###
                layerPath = duongDanNguon + "/" +  element["DatasetName"] + "/" + element["LayerName"]
                arcpy.MakeFeatureLayer_management(layerPath, element["featureLayer"])
                ### Select ###
                strQuery = element["FID_XXX"] + " IS NOT NULL"
                arcpy.SelectLayerByAttribute_management(outPathSimplifyLayer, "NEW_SELECTION", strQuery)
                ### Copy To Table Temp ###
                outTableTemp = "in_memory\\outTableTemp"
                arcpy.CopyFeatures_management(outPathSimplifyLayer, outTableTemp)
                ### ... ###
                with arcpy.da.UpdateCursor(element["featureLayer"], ["OID@", "SHAPE@"]) as cursor:
                    for row in cursor:
                        found = False
                        with arcpy.da.UpdateCursor(outTableTemp, [element["FID_XXX"], "SHAPE@"]) as cursorSub:
                            for rowSub in cursorSub:
                                if row[0] == rowSub[0]:
                                    found = True
                                    row[1] = rowSub[1]
                                    cursor.updateRow(row)
                                    cursorSub.deleteRow()
                                    break
                        if found == False:
                            cursor.deleteRow()
        arcpy.AddMessage("\n# Hoan thanh Simplify Polyline!!!")
        
        ############################################## Snap Line to Polygon #############################
        arcpy.AddMessage("\n# Bat dau Snap")
        for elementPolygon in listPolygon:
            if elementPolygon["LayerType"] == "Polyline":
                lineLayerName = elementPolygon["LayerName"][:elementPolygon["LayerName"].find('_Buffer')]
                arcpy.AddMessage("\n\t# Snap: {0}".format(lineLayerName))
                layerBufferPath = duongDanNguon + "/" +  elementPolygon["DatasetName"] + "/" + elementPolygon["LayerName"]
                layerLinePath = duongDanNguon + "/" +  elementPolygon["DatasetName"] + "/" + lineLayerName
                arcpy.Snap_edit(layerLinePath, [[layerBufferPath, "EDGE", "25 Meters"]])
                '''
                with arcpy.da.SearchCursor(layerBufferPath, ["OID@"]) as cursor:
                    for row in cursor:
                        with arcpy.da.SearchCursor(layerLinePath, ["OID@"]) as cursorSub:
                            for rowSub in cursorSub:
                                if rowSub[0] == row[0]:
                                    strQuery = "OBJECTID = " + str(row[0])
                                    arcpy.SelectLayerByAttribute_management(layerLinePath, "NEW_SELECTION", strQuery)
                                    arcpy.SelectLayerByAttribute_management(layerBufferPath, "NEW_SELECTION", strQuery)
                                    arcpy.Snap_edit(layerLinePath, [[layerBufferPath, "EDGE", "25 Meters"]])
                '''
        arcpy.AddMessage("\n# Hoan thanh!!!")
    else:
        arcpy.AddMessage("\n# Khong tim thay file cau hinh: \"{0}\"".format(urlFile))
except OSError as error:
    arcpy.AddMessage("Error" + error.message)
except ValueError as error:
    arcpy.AddMessage("Error" + error.message)
except arcpy.ExecuteError as error:
    arcpy.AddMessage("Error" + error.message)
finally:
    arcpy.Delete_management("in_memory")