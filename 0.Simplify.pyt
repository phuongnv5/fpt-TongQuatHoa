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
        self.tools = [SimplifyPolygon, ChangeLineFollowPolygon, CreateFileConfig]

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

class ChangeLineFollowPolygon(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.ChangeLineFollowPolygon"
        self.description = "Change Line Follow Polygon"
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
            simplifyPologon = {
                "algorithm": "BEND_SIMPLIFY",
                "tolerance": "50 Meters",
                "error_option": "NO_CHECK",
                "collapsed_point_option": "NO_KEEP"
            }
            # Load Data Config #
            ## Location Current File ##
            fileUrl = os.path.dirname(os.path.realpath(__file__))
            fileName = "ConfigSimplifySmooth.json"
            ## Load Data JSON ##
            dataJSON = None
            with open(os.path.join(fileUrl, fileName)) as jsonFile:  
                dataJSON = json.load(jsonFile)
            #arcpy.AddMessage(json.dumps(dataJSON, indent = 4))
            ## Load Data Config Tools ##
            dataConfigTools = dataJSON[0]
            #arcpy.AddMessage(json.dumps(dataConfigTools, indent = 4))

            # Init WorkSpase #
            arcpy.env.overwriteOutput = True
            duongDanNguon = "C:\\Generalize_25_50\\50K_Process.gdb"
            duongDanDich = "C:\\Generalize_25_50\\50K_Final.gdb"
            defaultGDB = "C:\\Users\\vuong\\Documents\\ArcGIS\\Default.gdb"

            # Run #
            for elem in dataConfigTools["configTools"]:
                arcpy.AddMessage("\n# Xu ly: {}\\{} ...".format(elem["featureDataset"], elem["featureName"]))
                ## Merge Polygon (in = All Polygon in listPolygon, out = "in_memory\\OutMergePolygonTemp") ##
                in_merge = []
                out_merge = "in_memory\\OutMergePolygonTemp"
                fieldMappings = arcpy.FieldMappings()
                ### Init in_merge ###
                for elemSub in elem["listPolygon"]:
                    urlFeatureDataSet = os.path.join(duongDanNguon, elemSub["featureDataset"])
                    for elemSubSub in elemSub["listSimplifyPolygon"]:
                        urlFeatureClass = os.path.join(urlFeatureDataSet, elemSubSub)
                        in_merge.append(urlFeatureClass)
                        fieldMappings.addTable(urlFeatureClass)
                for field in fieldMappings.fields:
                    if field.name != "":
                        fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
                ### Run Tool Merge ##
                arcpy.AddMessage("\n\t# Merge Polygon: in_merge = {} ...".format(in_merge))
                arcpy.Merge_management(in_merge, out_merge, fieldMappings)

                ## Simplify Polygon (in = "in_memory\\OutMergePolygonTemp", out = "in_memory\\OutSimplifyTemp") ##
                arcpy.AddMessage("\n\t# Simplify Polygon: in_features = {} ...".format(out_merge))
                out_simplify = "in_memory\\OutSimplifyTemp"
                arcpy.SimplifyPolygon_cartography(in_features = out_merge,
                                                out_feature_class = out_simplify,
                                                algorithm = simplifyPologon["algorithm"],
                                                tolerance = simplifyPologon["tolerance"],
                                                error_option = simplifyPologon["error_option"],
                                                collapsed_point_option = simplifyPologon["collapsed_point_option"])
                
                ## Feature To Line (in = "in_memory\\OutSimplifyTemp", out = "in_memory\\OutFeatureToLineTemp") ##
                arcpy.AddMessage("\n\t# Feature To Line: in_features = {} ...".format(out_simplify))
                out_featuretoline = "in_memory\\OutFeatureToLineTemp"
                arcpy.FeatureToLine_management(in_features = out_simplify,
                                            out_feature_class = out_featuretoline)

                ## Feature Vertices To Point (in = featureName, out = "in_memory\\OutFeatureVerticesToPointTemp") ##
                arcpy.AddMessage("\n\t# Feature Vertices To Point: in_features = {}\\{} ...".format(elem["featureDataset"], elem["featureName"]))
                in_featureverticestopoint = os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elem["featureName"])
                out_featureverticestopoint = "in_memory\\OutFeatureVerticesToPointTemp"
                arcpy.FeatureVerticesToPoints_management(in_features = in_featureverticestopoint,
                                                        out_feature_class = out_featureverticestopoint,
                                                        point_location = "ALL")
                ## Make Feature Layer ##
                arcpy.AddMessage("\n\t# Make Feature Layer: {}, {} ...".format(out_featuretoline, out_featureverticestopoint))
                layerLine = "in_memory\\LayerLine"
                arcpy.MakeFeatureLayer_management(out_featuretoline, layerLine)
                layerPoint = "in_memory\\LayerPoint"
                arcpy.MakeFeatureLayer_management(out_featureverticestopoint, layerPoint)

                ## Select Layer By Location () ##
                arcpy.AddMessage("\n\t# Select Layer By Location: {}, {} ...".format(layerPoint, layerLine))
                arcpy.SelectLayerByLocation_management(in_layer = layerPoint, 
                                                        overlap_type = "INTERSECT", 
                                                        select_features = layerLine,
                                                        search_distance = "#",
                                                        selection_type = "NEW_SELECTION",
                                                        invert_spatial_relationship = "INVERT")
                ## Copy Features Class ##
                arcpy.AddMessage("\n\t# Copy Features Class: {}".format(layerPoint))
                #out_featurePointCopy = "in_memory\\FeaturePointCopy"
                out_featurePointCopy = os.path.join(defaultGDB, "DemoPoint")
                arcpy.CopyFeatures_management(in_features = layerPoint, out_feature_class = out_featurePointCopy)
                
                """
                out_featurePointCopyLayer = "in_memory\\FeaturePointCopyLayer"
                arcpy.MakeFeatureLayer_management(out_featurePointCopy, out_featurePointCopyLayer)
                ## Remove Point ##
                ### Maker Feature Layer Line ###
                arcpy.AddMessage("\n\t# Make Feature Layer: {}, {} ...".format(elem["featureDataset"], elem["featureName"]))
                layerLineRemove = "in_memory\\LayerLineRemove"
                arcpy.MakeFeatureLayer_management(os.path.join(os.path.join(duongDanNguon, elem["featureDataset"]), elem["featureName"]), layerLineRemove)
                arcpy.AddMessage("\n\t# Remove Point ...")
                with arcpy.da.UpdateCursor(layerLineRemove, ["OID@", "SHAPE@"]) as cursor:
                    for row in cursor:
                        #arcpy.AddMessage("\n\t\t# Line OID@: {}".format(str(row[0])))
                        strQuery = "OBJECTID = " + str(row[0])
                        #arcpy.AddMessage("\n\t\t# strQuery: {}".format(strQuery))
                        arcpy.SelectLayerByAttribute_management(layerLineRemove, "NEW_SELECTION", strQuery)
                        arcpy.SelectLayerByLocation_management(in_layer = out_featurePointCopyLayer, 
                                                        overlap_type = "WITHIN", 
                                                        select_features = layerLineRemove,
                                                        search_distance = "#",
                                                        selection_type = "NEW_SELECTION",
                                                        invert_spatial_relationship = "NOT_INVERT")
                        #count = int(arcpy.GetCount_management(out_featurePointCopyLayer).getOutput(0))
                        #arcpy.AddMessage("\n\t\t# Count Point: {}".format(count))
                """

            # Done #
            arcpy.AddMessage("\n# Done!!!")
        except OSError as error:
            arcpy.AddMessage(error.message)
        except ValueError as error:
            arcpy.AddMessage(error.message)
        except arcpy.ExecuteError as error:
            arcpy.AddMessage(error.message)
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

#============== Create File Config.json ==============#
class CreateFileConfig(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "3.Create File Config"
        self.description = "Create File Config"
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
            duongDanNguon = "C:\\Generalize_25_50\\50K_Process.gdb"
            duongDanDich = "C:\\Generalize_25_50\\50K_Final.gdb"

            # Create Dict Polygon #
            listDictPolygon = []
            for elem in arcpy.Describe(duongDanNguon).children:
                for elemSub in arcpy.Describe(elem.catalogPath).children:
                    if elemSub.featureType == "Simple" and elemSub.shapeType == "Polygon":
                        temp = {
                            "LayerType": "Polygon",
                            "ToolName": "Simplify Polygon",
                            "Algorithm": "BEND_SIMPLIFY",
                            "Tolerance": "50 Meters",
                            "Collapsed_Point_Option": "NO_KEEP",
                            "RunStatus": "True",
                            "DatasetName": elem.baseName,
                            "LayerName": elemSub.baseName
                        }
                        listDictPolygon.append(temp)
            
            # Write #
            fileFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Config")
            fileName = "ConfigSimplify.json"
            f = open(os.path.join(fileFolder, fileName), "w")
            f.write(json.dumps(obj = listDictPolygon, indent = 4))
            f.close()
            
            # Done #
            arcpy.AddMessage("\n# Done!!!")
        except:
            arcpy.AddMessage(arcpy.GetMessages())
        return