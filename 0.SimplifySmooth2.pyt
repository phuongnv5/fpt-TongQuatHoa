import arcpy
import arcpy.cartography as CA
import json
import os

in_workspace = "C:\\Generalize_25_50\\50K_Process.gdb"
out_workspace = "C:\\Generalize_25_50\\50K_Final.gdb"
featureClassTemp = os.path.join(in_workspace, "featureClassTemp")
featureClassSimplifyTemp = os.path.join(in_workspace, "featureClassSimplifyTemp")
featureClassSimplifyTemp_Pnt = featureClassSimplifyTemp + "_Pnt"
urlFile = "C:\\TQHBD\\ArcGIS_Tools\\fpt-TongQuatHoa\\SimplifySmoothTool.json"

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "0.SimplifySmooth2"
        self.description = "SimplifySmooth2"
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
            arcpy.AddMessage("\n# Reading: \"{0}\"".format(urlFile))
            dataJSON = None
            if os.path.exists(urlFile):
                f = open(urlFile)
                try:
                    dataJSON = json.load(f)
                    for ele in dataJSON:
                        if ele["enable"] == False:
                            continue
                        fc = os.path.join(os.path.join(in_workspace, ele["featureDataSet"]), ele["baseName"])
                        if arcpy.Exists(fc):
                            dec = arcpy.Describe(fc)
                            if dec.featureType == "Simple":
                                if dec.shapeType == "Polyline":
                                    #arcpy.AddMessage("\t# SimplifyLine: {0}, {1}".format(ele["usingParameter"][0]["algorithm"], ele["usingParameter"][0]["tolerance"]))
                                    CA.SimplifyLine(featureClassTemp,
                                                    featureClassSimplifyTemp,
                                                    ele["usingParameter"][0]["algorithm"], 
                                                    ele["usingParameter"][0]["tolerance"])
                                    arcpy.DeleteField_management(featureClassSimplifyTemp, ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])
                                    #arcpy.AddMessage("\t# SmoothLine: {0}, {1}".format(ele["usingParameter"][1]["algorithm"], ele["usingParameter"][1]["tolerance"]))
                                    CA.SmoothLine(featureClassSimplifyTemp,
                                                    os.path.join(os.path.join(out_workspace, ele["featureDataSet"]), ele["baseName"]),
                                                    ele["usingParameter"][1]["algorithm"],
                                                    ele["usingParameter"][1]["tolerance"])
                                elif dec.shapeType == "Polygon":
                                    #arcpy.AddMessage("\t# SimplifyPolygon: {0}, {1}".format(ele["usingParameter"][0]["algorithm"], ele["usingParameter"][0]["tolerance"]))
                                    CA.SimplifyPolygon(featureClassTemp,
                                                    featureClassSimplifyTemp,
                                                    ele["usingParameter"][0]["algorithm"], 
                                                    ele["usingParameter"][0]["tolerance"])
                                    arcpy.DeleteField_management(featureClassSimplifyTemp, ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])
                                    #arcpy.AddMessage("\t# SmoothPolygon: {0}, {1}".format(ele["usingParameter"][1]["algorithm"], ele["usingParameter"][1]["tolerance"]))
                                    CA.SmoothPolygon(featureClassSimplifyTemp,
                                                    os.path.join(os.path.join(out_workspace, ele["featureDataSet"]), ele["baseName"]),
                                                    ele["usingParameter"][1]["algorithm"],
                                                    ele["usingParameter"][1]["tolerance"])
                        else:
                            arcpy.AddMessage("\t# Not Found: {0}".format(fc))
                except:
                    arcpy.AddWarning("\t# Data Error?")
                arcpy.AddMessage("\n# Done!!!")
            else:
                arcpy.AddWarning("\t# Not Found: \"{0}\"".format(urlFile))
        except:
            arcpy.AddError(arcpy.GetMessages())
        finally:
            arcpy.Delete_management(featureClassTemp)
            arcpy.Delete_management(featureClassSimplifyTemp)
            arcpy.Delete_management(featureClassSimplifyTemp_Pnt)
        return
