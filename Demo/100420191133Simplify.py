import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\Generalize_25_50\\50K_Process.gdb\\ThuyHe"

fcBaiBoiA = "BaiBoiA"
fcSongSuoiA = "SongSuoiA"
fcDuongBoNuoc = "DuongBoNuoc"

listFeatureClass = [fcBaiBoiA, fcSongSuoiA, fcDuongBoNuoc]
listFeatureArea = [fcBaiBoiA, fcSongSuoiA]

try:
    # Copy FeatureClass:
    listFeatureClassCopy = []
    for elem in listFeatureClass:
        arcpy.CopyFeatures_management(elem, elem + "_Copy")
        listFeatureClassCopy.append(elem + "_Copy")
    # Create Dict
    listFcAndFl = []
    for elem in listFeatureClassCopy:
        temp = {
            "featureClass": elem,
            "featureLayer": "in_memory\\" + elem + "_Layer"
        }
        listFcAndFl.append(temp)
    # MakeLayer
    for elem in listFcAndFl:
        arcpy.MakeFeatureLayer_management(elem["featureClass"], elem["featureLayer"])
    # # AddField OID_Clone and NameFeatureLayer
    # for elem in listFcAndFl:
    #     arcpy.AddField_management(elem["featureLayer"], "OID_Clone", "LONG")
    #     arcpy.AddField_management(elem["featureLayer"], "NameFeatureLayer", "TEXT")
    # # Update Field
    # for elem in listFcAndFl:
    #     with arcpy.da.UpdateCursor(elem["featureLayer"], ["OID@", "OID_Clone", "NameFeatureLayer"]) as cursor:
    #         for row in cursor:
    #             row[1] = row[0]
    #             row[2] = elem["featureLayer"]
    #             cursor.updateRow(row)
    # Feature To Line
    arcpy.AddMessage("\n# Feature To Line...")
    for elem in listFcAndFl:
        arcpy.FeatureToLine_management(elem["featureLayer"], elem["featureClass"] + "_FeatureToLine")
    # FieldMappings
    fields = []
    for elem in listFcAndFl:
        fields.append("FID_" + elem["featureClass"])
    arcpy.AddMessage(fields)
    fieldMappings = arcpy.FieldMappings()
    for elem in listFcAndFl:
        fieldMappings.addTable(elem["featureClass"] + "_FeatureToLine")
    for field in fieldMappings.fields:
        if field.name not in fields:
            fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
    # Merge
    arcpy.AddMessage("\n# Merge...")
    inputsMerge = []
    for elem in listFcAndFl:
        inputsMerge.append(elem["featureClass"] + "_FeatureToLine")
    arcpy.Merge_management (inputsMerge, "FeatureToLineMergeTools", fieldMappings)
    # Simplify
    arcpy.AddMessage("\n# SimplifyLine...")
    arcpy.SimplifyLine_cartography (in_features = "FeatureToLineMergeTools", 
                                    out_feature_class = "FeatureToLineMergeTools_Simplify", 
                                    algorithm = "BEND_SIMPLIFY",
                                    tolerance = "50 Meters",
                                    collapsed_point_option = "NO_KEEP",
                                    error_checking_option = "NO_CHECK")
    arcpy.DeleteField_management("FeatureToLineMergeTools_Simplify", ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])
    # MakeLayer
    arcpy.AddMessage("\n# MakeFeatureLayer...")
    FeatureToLineMergeTools_Simplify_Layer = "in_memory\\FeatureToLineMergeTools_Simplify_Layer"
    arcpy.MakeFeatureLayer_management("FeatureToLineMergeTools_Simplify", FeatureToLineMergeTools_Simplify_Layer)
    # Snap
    for elem in listFeatureArea:
        arcpy.AddMessage("\t# Snap: {0}".format(elem + "_Copy"))
        fileName = "FID_" + elem + "_Copy"
        strQuery = fileName + " IS NOT NULL"
        arcpy.SelectLayerByAttribute_management(FeatureToLineMergeTools_Simplify_Layer, "NEW_SELECTION", strQuery)
        with arcpy.da.SearchCursor(FeatureToLineMergeTools_Simplify_Layer, ["OID@", fileName]) as cursor:
            for row in cursor:
                strQuery = "OBJECTID = " + str(row[0])
                arcpy.SelectLayerByAttribute_management(FeatureToLineMergeTools_Simplify_Layer, "NEW_SELECTION", strQuery)
                strQuery = "OBJECTID = " + str(row[1])
                arcpy.SelectLayerByAttribute_management("in_memory\\" + elem + "_Copy_Layer", "NEW_SELECTION", strQuery)
                arcpy.Densify_edit("in_memory\\" + elem + "_Copy_Layer", "OFFSET", "#", "0.1 Meters") 
                arcpy.Snap_edit("in_memory\\" + elem + "_Copy_Layer", 
                                [[FeatureToLineMergeTools_Simplify_Layer, "EDGE", "25 Meters"]])

    # Done
    arcpy.AddMessage("\n# Done!!!")
    # #####
    # # Feature Area To Line
    # fields = []
    # in_features_FeatureToLine = []
    # for elem in listFeatureClass:
    #     in_features_FeatureToLine.append("in_memory\\" + elem + "_Copy_Layer")
    #     fields.append("FID_" + elem + "_Copy")
    # out_features_FeatureToLine = "FeatureToLine"
    # arcpy.FeatureToLine_management(in_features_FeatureToLine, out_features_FeatureToLine)
    # # Field Mappings
    # fieldMappings = arcpy.FieldMappings()
    # fieldMappings.addTable(out_features_FeatureToLine)
    # fieldsDelete = []
    # for field in fieldMappings.fields:
    #     if field.name in fields:
    #         fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
    # for field in fieldMappings.fields:
    #     if field.name != "Shape_Length":
    #         fieldsDelete.append(field.name)
    # # Delete Field
    # arcpy.DeleteField_management(out_features_FeatureToLine, fieldsDelete)
    # # Simplify
    # FeatureToLine_Simplify = "FeatureToLine_Simplify"
    # arcpy.SimplifyLine_cartography (in_features = out_features_FeatureToLine, 
    #                                 out_feature_class = FeatureToLine_Simplify, 
    #                                 algorithm = "BEND_SIMPLIFY",
    #                                 tolerance = "50 Meters",
    #                                 collapsed_point_option = "NO_KEEP",
    #                                 error_checking_option = "NO_CHECK")
    # arcpy.DeleteField_management(FeatureToLine_Simplify, ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])
    # # MakeLayer
    # FeatureToLine_Simplify_Layer = "in_memory\\FeatureToLine_Simplify_Layer"
    # arcpy.MakeFeatureLayer_management(FeatureToLine_Simplify, FeatureToLine_Simplify_Layer)
    # # Done
    # arcpy.AddMessage("\n# Done!!!")
except:
    arcpy.AddMessage(arcpy.GetMessages())