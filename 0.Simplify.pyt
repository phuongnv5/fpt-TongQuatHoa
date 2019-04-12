import arcpy
import os
import json

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [SimplifyPolygon, SimplifyLine]

class SimplifyPolygon(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1.Simplify Polygon"
        self.description = "Simplify Polygon"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            # Init WorkSpase #
            arcpy.env.overwriteOutput = True
            duongDanNguon = "C:\\Generalize_25_50\\50K_Process.gdb"
            duongDanDich = "C:\\Generalize_25_50\\50K_Final.gdb"

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

class SimplifyLine(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.Simplify Line"
        self.description = "2.Simplify Line"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            # Init WorkSpase #
            arcpy.env.overwriteOutput = True
            duongDanNguon = "C:\\Generalize_25_50\\50K_Process.gdb"
            duongDanDich = "C:\\Generalize_25_50\\50K_Final.gdb"

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
                            "featureToLine": "in_memory\\" + elem.baseName + "\\" + elemSub.baseName + "_FeatureToLine",
                            "FID_XXX": "FID_" + elemSub.baseName
                        }
                        temp["listFeature"].append(tempSub)
                listDictPolygon.append(temp)
            
            # Create Dict Polyline #
            listDictPolyline = []
            for elem in arcpy.Describe(duongDanNguon).children:
                temp = {
                    "featureDataset": elem.baseName,
                    "listFeature": []
                }
                for elemSub in arcpy.Describe(elem.catalogPath).children:
                    if elemSub.featureType == "Simple" and elemSub.shapeType == "Polyline":
                        tempSub = {
                            "featureName": elemSub.baseName,
                            "featureLayer": "in_memory\\" + elemSub.baseName + "_Layer",
                            "featureCopy": "in_memory\\" + elemSub.baseName + "_Copy",
                            "featureCopyLayer": "in_memory\\" + elemSub.baseName + "_Copy_Layer",
                            "FID_XXX": "FID_" + elemSub.baseName
                        }
                        temp["listFeature"].append(tempSub)
                listDictPolyline.append(temp)

            # Add Field, Update Field FID_XXX #
            ## Poligon ##
            for elem in listDictPolygon:
                if len(elem["listFeature"]) == 0:
                    continue
                ## Add Field ##
                for elemSub in elem["listFeature"]:
                    inPathAddField = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
                    arcpy.AddField_management(inPathAddField, elemSub["FID_XXX"], "LONG")
                ## Update Field ##
                for elemSub in elem["listFeature"]:
                    inPathAddField = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
                    with arcpy.da.UpdateCursor(inPathAddField, ["OID@", elemSub["FID_XXX"]]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)

            ## Polyline ##
            for elem in listDictPolyline:
                if len(elem["listFeature"]) == 0:
                    continue
                ## Add Field ##
                for elemSub in elem["listFeature"]:
                    inPathAddField = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
                    arcpy.AddField_management(inPathAddField, elemSub["FID_XXX"], "LONG")
                ## Update Field ##
                for elemSub in elem["listFeature"]:
                    inPathAddField = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
                    with arcpy.da.UpdateCursor(inPathAddField, ["OID@", elemSub["FID_XXX"]]) as cursor:
                        for row in cursor:
                            row[1] = row[0]
                            cursor.updateRow(row)


            # Merge Feature Line #
            arcpy.AddMessage("\n# Merge tat ca cac Polygon...")
            ## Create List Input Feature Line ##
            enableFieldsPolygon = []
            inputsMerge = []
            fieldMappings = arcpy.FieldMappings()
            for elem in listDictPolygon:
                if len(elem["listFeature"]) == 0:
                    continue
                for elemSub in elem["listFeature"]:
                    inPathFeatureToLine = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
                    fieldMappings.addTable(inPathFeatureToLine)
                    inputsMerge.append(inPathFeatureToLine)
                    enableFieldsPolygon.append(elemSub["FID_XXX"])
            for field in fieldMappings.fields:
                if field.name not in enableFieldsPolygon:
                    fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
            arcpy.Merge_management(inputsMerge, os.path.join(duongDanNguon, "MergePolygon"), fieldMappings)

            # Feature To Line #
            arcpy.AddMessage("\n# Chuyen tat ca cac Polygon da duoc Merge thanh Line...")
            arcpy.FeatureToLine_management(os.path.join(duongDanNguon, "MergePolygon"), os.path.join(duongDanNguon, "MergePolygonToLine"))
            
            # Unsplit Line #
            arcpy.AddMessage("\n# Unsplit Line...")
            arcpy.UnsplitLine_management(os.path.join(duongDanNguon, "MergePolygonToLine"),
                                        os.path.join(duongDanNguon, "MergePolygonToLineUnSplitLine"),
                                        enableFieldsPolygon)

            # Merge All Line #
            arcpy.AddMessage("\n# Merge tat ca cac PolyLine va tat ca cac Polygon (da duoc chuyen thanh Line o buoc truoc)")
            enableFieldsPolyline = []
            inputsMerge = []
            fieldMappings = arcpy.FieldMappings()
            for elem in listDictPolyline:
                if len(elem["listFeature"]) == 0:
                    continue
                for elemSub in elem["listFeature"]:
                    inPathFeatureToLine = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elemSub["featureName"])
                    fieldMappings.addTable(inPathFeatureToLine)
                    inputsMerge.append(inPathFeatureToLine)
                    enableFieldsPolyline.append(elemSub["FID_XXX"])
            inputsMerge.append(os.path.join(duongDanNguon, "MergePolygonToLine"))
            fieldMappings.addTable(os.path.join(duongDanNguon, "MergePolygonToLine"))

            enableFields = enableFieldsPolygon + enableFieldsPolyline

            for field in fieldMappings.fields:
                if field.name not in enableFields:
                    fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
            
            arcpy.Merge_management(inputsMerge, os.path.join(duongDanNguon, "MergePolygonToLine_MergerAllLine"), fieldMappings)
            
            # Simplify Line #
            arcpy.AddMessage("\n# Simplify Line")
            arcpy.SimplifyLine_cartography (in_features = os.path.join(duongDanNguon, "MergePolygonToLine_MergerAllLine"), 
                                        out_feature_class = os.path.join(duongDanNguon, "MergePolygonToLine_MergerAllLine_SimplifyLine"),
                                        algorithm = "BEND_SIMPLIFY", 
                                        tolerance = "50 Meters",
                                        collapsed_point_option = "NO_KEEP",
                                        error_checking_option = "NO_CHECK")
            
            # Done #
            arcpy.AddMessage("\n# Done!!!")

        except:
            arcpy.AddMessage(arcpy.GetMessages())
        return