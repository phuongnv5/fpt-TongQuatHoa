import arcpy


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
        self.label = "Tool"
        self.description = "abc1"
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
        arcpy.env.overwriteOutput = 1
        _path_Layer_NhaP = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang/NhaP"
        _path_Layer_NhaP_Copy = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang/NhaP_Copy"
        _path_Layer_DoanTimDuongBo = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo"
        _path_Layer_DoanTimDuongBo_Buffer = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Buffer"


        arcpy.CopyFeatures_management(_path_Layer_NhaP, _path_Layer_NhaP_Copy)
        arcpy.Buffer_analysis(roads, roadsBuffer, distanceField, sideType, endType, dissolveType, dissolveField)

        return
