import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\Generalize_25_50\\50K_Process.gdb\\ThuyHe"

fcBaiBoiA = "BaiBoiA"
fcSongSuoiA = "SongSuoiA"
fcMatNuocTinh = "MatNuocTinh"
listFeatureClass = [fcBaiBoiA, fcSongSuoiA, fcMatNuocTinh]

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
    # AddField OID_Clone and NameFeatureLayer
    for elem in listFcAndFl:
        arcpy.AddField_management(elem["featureLayer"], "OID_Clone", "LONG")
        arcpy.AddField_management(elem["featureLayer"], "NameFeatureLayer", "TEXT")
    # Update Field
    for elem in listFcAndFl:
        with arcpy.da.UpdateCursor(elem["featureLayer"], ["OID@", "OID_Clone", "NameFeatureLayer"]) as cursor:
            for row in cursor:
                row[1] = row[0]
                row[2] = elem["featureLayer"]
                cursor.updateRow(row)
    # FieldMappings
    fieldMappings = arcpy.FieldMappings()
    for elem in listFcAndFl:
        fieldMappings.addTable(elem["featureLayer"])
    for field in fieldMappings.fields:
        if field.name not in ["OID_Clone", "NameFeatureLayer"]:
            fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
    # Merge
    arcpy.AddMessage("\n# Merge...")
    inputsMerge = []
    for elem in listFcAndFl:
        inputsMerge.append(elem["featureLayer"])
    arcpy.Merge_management (inputsMerge, "MergeTools", fieldMappings)
    # Simplify
    arcpy.AddMessage("\n# Simplify...")
    arcpy.CopyFeatures_management("MergeTools", "MergeTools_Copy")
    arcpy.SimplifyPolygon_cartography(in_features = "MergeTools_Copy",
                                    out_feature_class = "MergeTools_Copy" + "_Simplify",
                                    algorithm = "BEND_SIMPLIFY",
                                    tolerance = "50 Meters",
                                    collapsed_point_option = "NO_KEEP")
    arcpy.DeleteField_management("MergeTools_Copy" + "_Simplify", ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])            
    # Make Feature Layer
    arcpy.MakeFeatureLayer_management("MergeTools_Copy" + "_Simplify", "in_memory\\" + "MergeTools_Copy" + "_Simplify" + "_Layer")
    # Update Shape
    arcpy.AddMessage("\n# Update...")
    #arcpy.SelectLayerByAttribute_management("in_memory\\" + "MergeTools_Copy" + "_Simplify" + "_Layer", "NEW_SELECTION", "OBJECTID <> -1")
    for elem in listFcAndFl:
        arcpy.AddMessage("\n\t# Update: {0}".format(elem["featureClass"]))
        with arcpy.da.UpdateCursor(elem["featureLayer"], ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                strQuery = "OID_Clone = " + str(row[0]) + " AND NameFeatureLayer = " + "'" + elem["featureLayer"] + "'"
                arcpy.SelectLayerByAttribute_management("in_memory\\" + "MergeTools_Copy" + "_Simplify" + "_Layer", "NEW_SELECTION", strQuery)
                with arcpy.da.SearchCursor("in_memory\\" + "MergeTools_Copy" + "_Simplify" + "_Layer", ["SHAPE@"]) as cursorSub:
                    for rowSub in cursorSub:
                        row[1] = rowSub[0]
                        cursor.updateRow(row)
    # DeleteField
    for elem in listFcAndFl:
        arcpy.DeleteField_management(elem["featureLayer"], ["OID_Clone", "NameFeatureLayer"])
except:
    arcpy.AddMessage(arcpy.GetMessages())
finally:
    arcpy.Delete_management("in_memory")
