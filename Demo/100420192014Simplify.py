import arcpy
import os
import json

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\Generalize_25_50\\50K_Process.gdb\\ThuyHe"

fcBaiBoiA = "BaiBoiA"
fcSongSuoiA = "SongSuoiA"
fcMatNuocTinh = "MatNuocTinh"
fcDuongBoNuoc = "DuongBoNuoc"
fcDuongMepNuoc = "DuongMepNuoc"
fcDoanTimDuongBoClone = "DoanTimDuongBoClone"

listFeaturePolygon = [fcBaiBoiA, fcSongSuoiA, fcMatNuocTinh]
listFeatureLine = [fcDuongBoNuoc, fcDuongMepNuoc, fcDoanTimDuongBoClone]

try:
    arcpy.AddMessage("\n# 110420191216")
    
    # Create Dict #
    ## FC Polygon ##
    dictListFcPolygon = []
    for elem in listFeaturePolygon:
        temp = {
            "featureName": elem,
            "featureCopy": elem + "_Copy",
            "featureLayer": "in_memory\\" + elem + "_Copy_Layer",
            "featureToLine": elem + "_Copy_FeatureToLine",
            "featureToLineLayer": "in_memory\\" + elem + "_Copy_FeatureToLine_Layer",
            "FID_XXX": "FID_" + elem + "_Copy"
        }
        dictListFcPolygon.append(temp)
    ## FC Line ##
    dictListFcLine = []
    for elem in listFeatureLine:
        temp = {
            "featureName": elem,
            "featureCopy": elem + "_Copy",
            "featureLayer": "in_memory\\" + elem + "_Copy_Layer",
            "FID_XXX": "FID_" + elem + "_Copy"
        }
        dictListFcLine.append(temp)

    # Copy And Make Feature Layer #
    ## Feature Class Polygon ##
    for elem in dictListFcPolygon:
        ### Copy Feature Class ###
        arcpy.CopyFeatures_management(elem["featureName"], elem["featureCopy"])
        ### Make Feature Layer ###
        arcpy.MakeFeatureLayer_management(elem["featureCopy"], elem["featureLayer"])
    ## Feature Class Line ##
    for elem in dictListFcLine:
        ### Copy Feature Class ###
        arcpy.CopyFeatures_management(elem["featureName"], elem["featureCopy"])
        ### Make Feature Layer ###
        arcpy.MakeFeatureLayer_management(elem["featureCopy"], elem["featureLayer"])
    
    # Add And Update Field OID_Clone #
    ## Add Field ##
    ### Feature Class Line ###
    for elem in dictListFcLine:
        arcpy.AddField_management(elem["featureLayer"], elem["FID_XXX"], "LONG")
    ## Update Field ##
    ### Feature Class Line ###
    for elem in dictListFcLine:
        with arcpy.da.UpdateCursor(elem["featureLayer"], ["OID@", elem["FID_XXX"]]) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

    # Feature To Line And Make Feature Layer #
    ## Feature Class Polygon ##
    for elem in dictListFcPolygon:
        ### Feature To Line ###
        arcpy.FeatureToLine_management(elem["featureLayer"], elem["featureToLine"])
        ### Make Feature Layer ###
        arcpy.MakeFeatureLayer_management(elem["featureToLine"], elem["featureToLineLayer"])
    ## Feature Class Line ##
    """
    for elem in dictListFcLine:
        ### Feature To Line ###
        arcpy.FeatureToLine_management(elem["featureLayer"], elem["featureToLine"])
        ### Make Feature Layer ###
        arcpy.MakeFeatureLayer_management(elem["featureToLine"], elem["featureToLineLayer"])
    """
    
    # Field Mappings #
    fieldMappings = arcpy.FieldMappings()
    enableFields = []
    ## Feature Class Polygon ##
    for elem in dictListFcPolygon:
        fieldMappings.addTable(elem["featureToLineLayer"])
        enableFields.append(elem["FID_XXX"])
    ## Feature Class Line ##
    for elem in dictListFcLine:
        fieldMappings.addTable(elem["featureLayer"])
        enableFields.append(elem["FID_XXX"])
    ## Config Field Mappings ##
    for field in fieldMappings.fields:
        if field.name not in enableFields:
            fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))

    # Merge Feature Line #
    arcpy.AddMessage("\n# Merge...")
    ## Create List Input Feature Line ##
    inputsMerge = []
    ### Feature Class Polygon ###
    for elem in dictListFcPolygon:
        inputsMerge.append(elem["featureToLineLayer"])
    ### Feature Class Line ###
    for elem in dictListFcLine:
        inputsMerge.append(elem["featureLayer"])
    ## Run Merge Tools ##
    arcpy.Merge_management (inputsMerge, "FeatureToLineMergeTools", fieldMappings)

    # Simplify #
    ## Run Tools ##
    arcpy.AddMessage("\n# SimplifyLine...")
    out_feature_class_Simplify = "FeatureToLineMergeTools_Simplify"
    arcpy.SimplifyLine_cartography (in_features = "FeatureToLineMergeTools", 
                                    out_feature_class = out_feature_class_Simplify, 
                                    algorithm = "BEND_SIMPLIFY",
                                    tolerance = "50 Meters",
                                    collapsed_point_option = "NO_KEEP",
                                    error_checking_option = "NO_CHECK")
    ## Delete Field ##
    arcpy.DeleteField_management(out_feature_class_Simplify, ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])
    
    # Maker Feature Layer #
    tempLayerSimplify = "in_memory\\TempLayer"
    arcpy.MakeFeatureLayer_management(out_feature_class_Simplify, tempLayerSimplify)

    # Update #
    ## Feature Class Polygon ##
    """
    for elem in dictListFcPolygon:
        arcpy.AddMessage("\n# Update: {0}".format(elem["featureCopy"]))
        with arcpy.da.UpdateCursor(elem["featureLayer"], ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                ### Select By Attribute ###
                fieldName = elem["FID_XXX"]
                strQuery = fieldName + " = " + str(row[0])
                arcpy.SelectLayerByAttribute_management(tempLayerSimplify, "NEW_SELECTION", strQuery)
                ### Feature To Line ###
                tempFeatureToLine = "in_memory\\tempFeatureToLine"
                arcpy.FeatureToLine_management(tempLayerSimplify, tempFeatureToLine)
                ### Feature To Pologon ###
                tempFeatureToPolygon = "in_memory\\tempFeatureToPolygon"
                arcpy.FeatureToPolygon_management(tempFeatureToLine, tempFeatureToPolygon)
                ### Maker Feature Layer ###
                tempFeatureToPolygonLayer = "in_memory\\tempFeatureToPolygonLayer"
                arcpy.MakeFeatureLayer_management(tempFeatureToPolygon, tempFeatureToPolygonLayer)
                ### Check Count Polygon ###
                count = int(arcpy.GetCount_management(tempFeatureToPolygonLayer).getOutput(0))
                if count == 1:
                    #### Update ####
                    with arcpy.da.SearchCursor(tempFeatureToPolygonLayer, ["SHAPE@"]) as cursorSub:
                        for rowSub in cursorSub:
                            row[1] = rowSub[0]
                            cursor.updateRow(row)
                elif count > 1:
                    #### Chon Polygon thoa man ####
                    OIDPolygon = None
                    with arcpy.da.SearchCursor(tempFeatureToPolygonLayer, ["OID@"]) as cursorSub:
                        for rowSub in cursorSub:
                            ##### Select #####
                            strQuery = "OBJECTID = " + str(rowSub[0])
                            arcpy.SelectLayerByAttribute_management(tempFeatureToPolygonLayer, "NEW_SELECTION", strQuery)
                            ##### Feature To Line #####
                            tempFeatureToLineSub = "in_memory\\tempFeatureToLineSub"
                            arcpy.FeatureToLine_management(tempFeatureToPolygonLayer, tempFeatureToLineSub)
                            ##### Erase ####
                            tempFeatureToLineSubErase = "in_memory\\tempFeatureToLineSubErase"
                            arcpy.Erase_analysis(tempFeatureToLine, tempFeatureToLineSub, tempFeatureToLineSubErase)
                            countSub = int(arcpy.GetCount_management(tempFeatureToLineSubErase).getOutput(0))
                            if countSub == 0 or countSub == 1:
                                OIDPolygon = str(rowSub[0])
                                break
                    if OIDPolygon != None:
                        strQuery = "OBJECTID = " + OIDPolygon
                        arcpy.SelectLayerByAttribute_management(tempFeatureToPolygonLayer, "NEW_SELECTION", strQuery)
                        with arcpy.da.SearchCursor(tempFeatureToPolygonLayer, ["SHAPE@"]) as cursorSub:
                            for rowSub in cursorSub:
                                row[1] = rowSub[0]
                                cursor.updateRow(row)
    """
    ## Feature Class Line ##
    for elem in dictListFcLine:
        if elem["featureName"] != "DoanTimDuongBoClone":
            continue
        arcpy.AddMessage("\n# Update: {0}".format(elem["featureCopy"]))
        fieldName = elem["FID_XXX"]
        strQuery = fieldName + " IS NOT NULL"
        arcpy.SelectLayerByAttribute_management(tempLayerSimplify, "NEW_SELECTION", strQuery)
        arcpy.CopyFeatures_management(tempLayerSimplify, "in_memory\\TableTemp")
        with arcpy.da.UpdateCursor(elem["featureLayer"], ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                with arcpy.da.UpdateCursor("in_memory\\TableTemp", ["OID@", "SHAPE@", fieldName]) as cursorSub:
                    for rowSub in cursorSub:
                        if rowSub[2] == row[0]:
                            row[1] = rowSub[1]
                            cursorSub.deleteRow()
                            cursor.updateRow(row)
                            break
    
    # Done
    arcpy.AddMessage("\n# Done!!!")
except:
    arcpy.AddMessage(arcpy.GetMessages())
finally:
    arcpy.Delete_management("in_memory")