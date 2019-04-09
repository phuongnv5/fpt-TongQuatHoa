import arcpy
import arcpy.cartography as CA
import json
import os

arcpy.env.overwriteOutput = True
in_workspace = "C:\\Generalize_25_50\\50K_Process.gdb"
out_workspace = "C:\\Generalize_25_50\\50K_Final.gdb"
urlFile = "C:\\TQHBD\\ArcGIS_Tools\\fpt-TongQuatHoa\\fpt-TongQuatHoa\\ConfigSimplifySmooth.json"

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [SimplifySmooth]

class CreateFileConfig(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1.CreateFileConfig"
        self.description = "CreateFileConfig"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = "Simplification Algorithm",
            name = "simplification_algorithm",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param1 = arcpy.Parameter(
            displayName = "Simplification Tolerance",
            name = "simplification_tolerance",
            datatype = "GPLinearUnit",
            parameterType = "Required",
            direction = "Input"
        )
        param2 = arcpy.Parameter(
            displayName = "Smoothing Algorithm",
            name = "smoothing_algorithm",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param3 = arcpy.Parameter(
            displayName = "Smoothing Tolerance",
            name = "smoothing_tolerance",
            datatype = "GPLinearUnit",
            parameterType = "Required",
            direction = "Input"
        )
        param0.filter.type = "ValueList"
        param0.filter.list = ["POINT_REMOVE", "BEND_SIMPLIFY", "WEIGHTED_AREA"]
        param0.value = "BEND_SIMPLIFY"
        param1.value = "50 Meters"
        param2.filter.type = "ValueList"
        param2.filter.list = ["PAEK", "BEZIER_INTERPOLATION"]
        param2.value = "PAEK"
        param3.value = "50 Meters"
        params = [param0, param1, param2, param3]
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
        try:
            f = open(urlFile, "w")
            dataJSON = []
            for ele in arcpy.Describe(in_workspace).children:
                for eleSub in arcpy.Describe(ele.catalogPath).children:
                    if eleSub.featureType == "Simple":
                        if eleSub.shapeType == "Polyline":
                            x = {
                                "Layer": ele.baseName + "\\" + eleSub.baseName,
                                "RunTools": "True",
                                "ProcessType": 
                                    [
                                        {
                                            "ToolName": "Simplify Line",
                                            "Algorithm": parameters[0].valueAsText,
                                            "Tolerance": parameters[1].valueAsText,
                                            "Collapsed_Point_Option": "NO_KEEP"
                                        },
                                        {
                                            "ToolName": "Smooth Line",
                                            "Algorithm": parameters[2].valueAsText,
                                            "Tolerance": parameters[3].valueAsText,
                                            "Endpoint_Option": "FIXED_CLOSED_ENDPOINT",
                                            "Error_Option": "NO_CHECK"
                                        }
                                    ]
                            }
                            dataJSON.append(x)
                        elif eleSub.shapeType == "Polygon":
                            x = {
                                "Layer": ele.baseName + "\\" + eleSub.baseName,
                                "RunTools": "True",
                                "ProcessType": 
                                    [
                                        {
                                            "ToolName": "Simplify Polygon",
                                            "Algorithm": parameters[0].valueAsText,
                                            "Tolerance": parameters[1].valueAsText,
                                            "MinimumArea": "0 SquareMeters",
                                            "Collapsed_Point_Option": "NO_KEEP"
                                        },
                                        {
                                            "ToolName": "Smooth Polygon",
                                            "Algorithm": parameters[2].valueAsText,
                                            "Tolerance": parameters[3].valueAsText,
                                            "Endpoint_Option": "FIXED_ENDPOINT",
                                            "Error_Option": "NO_CHECK"
                                        }
                                    ]
                            }
                            dataJSON.append(x)
            f.write(json.dumps(dataJSON, indent=4))
            f.close()
        except:
            arcpy.AddError(arcpy.GetMessages())
        return

class SimplifySmooth(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.SimplifySmooth"
        self.description = "SimplifySmooth"
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
            arcpy.AddMessage("\n# Reading File Config: \"{0}\"".format(urlFile))
            dataJSON = None
            if os.path.exists(urlFile):
                f = open(urlFile)
                dataJSON = json.load(f)
                f.close()
                # Sap xep theo OrderNumber
                def returnKey(elem):
                    return int(elem["OrderNumber"])
                dataJSON.sort(key = returnKey, reverse = False)
                # Simplify, Smooth
                for elem in dataJSON:
                    arcpy.AddMessage(os.path.join(in_workspace, elem["Layer"]))
                    fc = os.path.join(in_workspace, elem["Layer"])
                    if arcpy.Exists(fc):
                        # Create in_barries:
                        in_barriers = []
                        if len(elem["BarrierLayers"]) > 0:
                            for elemSub in elem["BarrierLayers"]:
                                in_barriers.append(os.path.join(in_workspace, elemSub["Layer"]))
                        # Simplify
                        if elem["ProcessType"][0]["ToolName"] == "Simplify Polygon" and elem["ProcessType"][0]["RunStatus"] == "True":
                            arcpy.AddMessage("\t# Simplify Polygon: {0}, {1}".format(elem["ProcessType"][0]["Algorithm"], elem["ProcessType"][0]["Tolerance"]))
                            CA.SimplifyPolygon(in_features = fc,
                                                out_feature_class = fc + "_Simplify",
                                                algorithm = elem["ProcessType"][0]["Algorithm"],
                                                tolerance = elem["ProcessType"][0]["Tolerance"],
                                                collapsed_point_option = elem["ProcessType"][0]["Collapsed_Point_Option"],
                                                in_barriers = in_barriers)
                            #arcpy.CopyFeatures_management(fc + "_Simplify", fc)
                            #arcpy.Delete_management(fc + "_Simplify")
                        elif elem["ProcessType"][0]["ToolName"] == "Simplify Line" and elem["ProcessType"][0]["RunStatus"] == "True":
                            arcpy.AddMessage("\t# Simplify Line: {0}, {1}".format(elem["ProcessType"][0]["Algorithm"], elem["ProcessType"][0]["Tolerance"]))
                            CA.SimplifyLine(in_features = fc,
                                            out_feature_class = fc + "_Simplify",
                                            algorithm = elem["ProcessType"][0]["Algorithm"],
                                            tolerance = elem["ProcessType"][0]["Tolerance"],
                                            collapsed_point_option = elem["ProcessType"][0]["Collapsed_Point_Option"],
                                            in_barriers = in_barriers)
                            #arcpy.CopyFeatures_management(fc + "_Simplify", fc)
                            #arcpy.Delete_management(fc + "_Simplify")
                        elif elem["ProcessType"][0]["ToolName"] == "Simplify Building" and elem["ProcessType"][0]["RunStatus"] == "True":
                            arcpy.AddMessage("\t# Simplify Building: {0}, {1}".format(elem["ProcessType"][0]["Algorithm"], elem["ProcessType"][0]["Tolerance"]))
                            CA.SimplifyBuilding(in_features = fc,
                                                out_feature_class = fc + "_Simplify",
                                                simplification_tolerance = elem["ProcessType"][0]["Tolerance"],
                                                minimum_area = elem["ProcessType"][0]["MinimumArea"],
                                                conflict_option = elem["ProcesssType"][0]["Collapsed_Point_Option"])
                            #arcpy.CopyFeatures_management(fc + "_Simplify", fc)
                            #arcpy.Delete_management(fc + "_Simplify")
                        # Smooth
                        if elem["ProcessType"][1]["ToolName"] == "Smooth Polygon" and elem["ProcessType"][1]["RunStatus"] == "True":
                            arcpy.AddMessage("\t# Smooth Polygon: {0}, {1}".format(elem["ProcessType"][1]["Algorithm"], elem["ProcessType"][1]["Tolerance"]))
                            CA.SmoothPolygon(in_features = fc,
                                            out_feature_class = fc + "_Simplify_Smooth",
                                            algorithm = elem["ProcessType"][1]["Algorithm"],
                                            tolerance = elem["ProcessType"][1]["Tolerance"],
                                            endpoint_option = elem["ProcessType"][1]["Endpoint_Option"],
                                            error_option = elem["ProcessType"][1]["Error_Option"])
                            arcpy.CopyFeatures_management(fc + "_Simplify_Smooth", fc)
                            arcpy.Delete_management(fc + "_Simplify_Smooth")
                        elif elem["ProcessType"][1]["ToolName"] == "Smooth Line" and elem["ProcessType"][1]["RunStatus"] == "True":
                            arcpy.AddMessage("\t# Smooth Line: {0}, {1}".format(elem["ProcessType"][1]["Algorithm"], elem["ProcessType"][1]["Tolerance"]))
                            CA.SmoothLine(in_features = fc,
                                        out_feature_class = fc + "_Simplify_Smooth",
                                        algorithm = elem["ProcessType"][1]["Algorithm"],
                                        tolerance = elem["ProcessType"][1]["Tolerance"],
                                        endpoint_option = elem["ProcessType"][1]["Endpoint_Option"],
                                        error_option = elem["ProcessType"][1]["Error_Option"])
                            arcpy.CopyFeatures_management(fc + "_Simplify_Smooth", fc)
                            arcpy.Delete_management(fc + "_Simplify_Smooth")
                    else:
                        arcpy.AddMessage("\t# Not Found: {0}".format(fc))
                arcpy.AddMessage("\n# Done!!!")
            else:
                arcpy.AddMessage("\t# Not Found File Config: \"{0}\". Run Tools CreateFileConfig!".format(urlFile))
        except:
            arcpy.AddMessage(arcpy.GetMessages())
        finally:
            pass
        return

        