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
        self.tools = [SimplifySmooth]


class SimplifySmooth(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "0.SimplifySmooth"
        self.description = "SimplifySmooth"
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
        """The source code of the tool."""
        # Bo tham so nhap vao:
        #   Su dung bo tham so nay neu featureClass khong duoc cau hinh tham so trong file JSON (urlFile)
        parametersDefault = [
            {
                "nameTool": "Simplify",
                "algorithm": parameters[0].valueAsText,
                "tolerance": parameters[1].valueAsText
            },
            {
                "nameTool": "Smooth",
                "algorithm": parameters[2].valueAsText,
                "tolerance": parameters[3].valueAsText
            }
        ]
        #arcpy.AddMessage(parametersDefault)
        try:
            # Doc du lieu JSON tu file: urlFile
            arcpy.AddMessage("\n# Reading: \"{0}\"".format(urlFile))
            dataJSON = None
            if os.path.exists(urlFile):
                f = open(urlFile)
                try:
                    dataJSON = json.load(f)
                except:
                    arcpy.AddWarning("\t# Data Error?")
                f.close()
            else:
                arcpy.AddWarning("\t# Not Found: \"{0}\"".format(urlFile))
            # Lay tat ca featureClass trong duong dan in_workspake thoa man la: Simple = [Polyline, Polygon]
            arcpy.AddMessage("\n# Scanning...\n")
            fcs = []
            for ele in arcpy.Describe(in_workspace).children:
                for eleSub in arcpy.Describe(ele.catalogPath).children:
                    if eleSub.featureType == "Simple" and (eleSub.shapeType == "Polyline" or eleSub.shapeType == "Polygon"):
                        temp = {
                            "featureDataSet": ele.baseName,
                            "baseName": eleSub.baseName,
                            "shapeType": eleSub.shapeType,
                            "catalogPath": eleSub.catalogPath
                        }
                        fcs.append(temp)
            # Chay tool Simplify, Smooth
            for ele in fcs:
                if ele["baseName"] != "BaiBoiA":
                    continue
                arcpy.AddMessage("# Simplify, Smooth: {0}\\{1} ...".format(ele["featureDataSet"], ele["baseName"]))
                # Ban dau bo tham so = parametersDefault
                ele["usingParameter"] = parametersDefault
                # Tim kiem trong dataJSON xem featureClass co duoc cau hinh tham so hay khong:
                #   Neu co thi su dung tham so duoc cau hinh trong fileJSON
                #   Neu khong thi su dung bo tham so default (nhap khi chay tool)
                if dataJSON != None:
                    for eleSub in dataJSON:
                        if eleSub["featureDataSet"] == ele["featureDataSet"] and eleSub["baseName"] == ele["baseName"]:
                            ele["usingParameter"] = eleSub["usingParameter"]
                            break
                # Chay tool phu hop voi "shapeType" cua featureClass
                arcpy.CopyFeatures_management(ele["catalogPath"], featureClassTemp)
                if ele["shapeType"] == "Polyline":
                    arcpy.AddMessage("\t# SimplifyLine: {0}, {1}".format(ele["usingParameter"][0]["algorithm"], ele["usingParameter"][0]["tolerance"]))
                    CA.SimplifyLine(featureClassTemp,
                                    featureClassSimplifyTemp,
                                    ele["usingParameter"][0]["algorithm"], 
                                    ele["usingParameter"][0]["tolerance"])
                    arcpy.DeleteField_management(featureClassSimplifyTemp, ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])
                    arcpy.AddMessage("\t# SmoothLine: {0}, {1}".format(ele["usingParameter"][1]["algorithm"], ele["usingParameter"][1]["tolerance"]))
                    CA.SmoothLine(featureClassSimplifyTemp,
                                    os.path.join(os.path.join(out_workspace, ele["featureDataSet"]), ele["baseName"]),
                                    ele["usingParameter"][1]["algorithm"],
                                    ele["usingParameter"][1]["tolerance"],
                                    "NO_CHECK")
                elif ele["shapeType"] == "Polygon":
                    arcpy.AddMessage("\t# SimplifyPolygon: {0}, {1}".format(ele["usingParameter"][0]["algorithm"], ele["usingParameter"][0]["tolerance"]))
                    CA.SimplifyPolygon(featureClassTemp,
                                    featureClassSimplifyTemp,
                                    ele["usingParameter"][0]["algorithm"], 
                                    ele["usingParameter"][0]["tolerance"])
                    arcpy.DeleteField_management(featureClassSimplifyTemp, ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])
                    arcpy.AddMessage("\t# SmoothPolygon: {0}, {1}".format(ele["usingParameter"][1]["algorithm"], ele["usingParameter"][1]["tolerance"]))
                    CA.SmoothPolygon(featureClassSimplifyTemp,
                                    os.path.join(os.path.join(out_workspace, ele["featureDataSet"]), ele["baseName"]),
                                    ele["usingParameter"][1]["algorithm"],
                                    ele["usingParameter"][1]["tolerance"])
            arcpy.AddMessage("\n# Done!!!")
        except:
            arcpy.AddError(arcpy.GetMessages())
        finally:
            arcpy.Delete_management(featureClassTemp)
            arcpy.Delete_management(featureClassSimplifyTemp)
            arcpy.Delete_management(featureClassSimplifyTemp_Pnt)
        return
