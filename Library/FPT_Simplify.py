# -*- coding: utf-8 -*-
import arcpy
import os
import json
import sys
import inspect

class FPT_Simplify:
    def __init__(self, snap_distance):
        self.snap_distance = snap_distance
        
    def simplify(self):
        try:
            # Init WorkSpase #
            arcpy.env.overwriteOutput = 1
            duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb"
            duongDanDich = "C:/Generalize_25_50/50K_Final.gdb"
            urlFile = '/ConfigSimplify.json'
            _algorithm = "BEND_SIMPLIFY"
            _tolerance = "50 Meters"
            _error_option = "NO_CHECK"
            _collapsed_point_option = "NO_KEEP"
            #Doc file config
            s1 = inspect.getfile(inspect.currentframe())
            s2 = os.path.dirname(s1)
            urlFile = s2 + urlFile
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
                    elif objConfig["LayerType"] == "Polyline" and objConfig["RunStatus"] == "True" and objConfig["LayerName"] <> "DuongBinhDo":
                        arcpy.AddMessage("\n# Buffer lop: \"{0}\"".format(objConfig["LayerName"]))
                        layerPath = duongDanNguon + "/" +  objConfig["DatasetName"] + "/" + objConfig["LayerName"]
                        arcpy.Buffer_analysis(in_features = layerPath, out_feature_class = layerPath + "_Buffer", 
                            buffer_distance_or_field = "0.1 Meters", line_side = "RIGHT")
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
                #outPathMerge = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang/outPathMergeTemp"
                arcpy.Merge_management (inputsMerge, outPathMerge, fieldMappings)
                ## Simplify Polygon ##
                arcpy.AddMessage("\n# Simplify Polygon...")
                outPathSimplify = "in_memory\\outPathSimplifyTemp"
                #outPathSimplify = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang/outPathSimplifyTemp"
                arcpy.SimplifyPolygon_cartography(in_features = outPathMerge,
                                                out_feature_class = outPathSimplify,
                                                algorithm = _algorithm,
                                                tolerance = _tolerance,
                                                minimum_area = "0 SquareMeters",
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
                    if element["LayerName"] == "DuongBinhDo":
                        arcpy.AddField_management(layerPath, "OLD_OBJECTID", "LONG", None, None, None,"OLD_OBJECTID", "NULLABLE")
                        arcpy.CalculateField_management(layerPath, "OLD_OBJECTID", "!OBJECTID!", "PYTHON_9.3")
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
                ## Simplify Polyline ##
                arcpy.AddMessage("\n# Simplify Polyline...")
                outPathSimplify = "in_memory\\outPathSimplifyTemp"
                '''
                arcpy.MakeFeatureLayer_management(duongDanNguon + "/ThuyHe/SongSuoiA", "ThuyHe_SongSuoiA_Lyr")
                arcpy.MakeFeatureLayer_management(duongDanNguon + "/ThuyHe/MatNuocTinh", "ThuyHe_MatNuocTinh_Lyr")
                arcpy.MakeFeatureLayer_management(duongDanNguon + "/ThuyHe/KenhMuongA", "ThuyHe_KenhMuongA_Lyr")
                in_barriers_Line = ["ThuyHe_SongSuoiA_Lyr", "ThuyHe_MatNuocTinh_Lyr", "ThuyHe_KenhMuongA_Lyr"]
                '''
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
                        if (lineLayerName <> "DuongBinhDo"):
                            arcpy.AddMessage("\n\t# Snap: {0}".format(lineLayerName))
                            layerBufferPath = duongDanNguon + "/" +  elementPolygon["DatasetName"] + "/" + elementPolygon["LayerName"]
                            layerLinePath = duongDanNguon + "/" +  elementPolygon["DatasetName"] + "/" + lineLayerName
                            arcpy.Snap_edit(layerLinePath, [[layerBufferPath, "EDGE", self.snap_distance]])
                
                ############################################## Copy to final #############################
                for element in listPolygon:
                    if element["LayerType"] == "Polygon":
                        layerPath = duongDanNguon + "/" +  element["DatasetName"] + "/" + element["LayerName"]
                        layerFinalPath = duongDanDich + "/" +  element["DatasetName"] + "/" + element["LayerName"]
                        arcpy.DeleteField_management(layerPath, [element["FID_XXX"]])
                        arcpy.CopyFeatures_management(layerPath, layerFinalPath)
                '''
                for objConfig in listLayerConfig:
                    if objConfig["LayerType"] == "Polyline" and objConfig["RunStatus"] == "True":
                        layerPath = duongDanNguon + "/" +  objConfig["DatasetName"] + "/" + objConfig["LayerName"]
                        layerFinalPath = duongDanDich + "/" +  objConfig["DatasetName"] + "/" + objConfig["LayerName"]
                        arcpy.CopyFeatures_management(layerPath, layerFinalPath)
                '''
                for element in listPolyLine:
                    if element["LayerType"] == "Polyline":
                        layerPath = duongDanNguon + "/" +  element["DatasetName"] + "/" + element["LayerName"]
                        layerFinalPath = duongDanDich + "/" +  element["DatasetName"] + "/" + element["LayerName"]
                        arcpy.DeleteField_management(layerPath, [element["FID_XXX"]])  
                        arcpy.CopyFeatures_management(layerPath, layerFinalPath)         
                
                #arcpy.AddMessage("\n# Hoan thanh!!!")
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

if __name__=='__main__':
    obj = FPT_Simplify("25 Meters")
    obj.simplify()
