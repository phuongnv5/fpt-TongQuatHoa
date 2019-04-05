import arcpy
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [DuongDiaGioi,DuongBienGioi]

#---------------------------Đường địa giới------------------------------------#
class DuongDiaGioi(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1.DuongDiaGioi"
        self.description = "Tiep bien lai duong dia gioi"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Khoang cach Snap",
            name="iput0",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param0.value = "20 Meters"
        params = [param0]
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
            arcpy.env.overwriteOutput = 1
            _duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb/"
            _duongDanDich = "C:/Generalize_25_50/50K_Final.gdb/"
            _DuongDiaGioi = "DuongDiaGioi"
            _KenhMuongL = "KenhMuongL"
            _SongSuoiL = "SongSuoiL"
            _khoang_Cach = parameters[0].valueAsText
            arcpy.Densify_edit(_duongDanNguon + "BienGioiDiaGioi/" + _DuongDiaGioi, "OFFSET",None, "0.1 Meters",None)
            arcpy.Snap_edit(_duongDanNguon + "BienGioiDiaGioi/" + _DuongDiaGioi, [[_duongDanNguon + "ThuyHe/" + _KenhMuongL, "VERTEX", _khoang_Cach], 
                [_duongDanNguon + "ThuyHe/" + _KenhMuongL, "EDGE", _khoang_Cach]])

            arcpy.Snap_edit(_duongDanNguon + "BienGioiDiaGioi/" + _DuongDiaGioi, [[_duongDanNguon + "ThuyHe/" + _SongSuoiL, "VERTEX", _khoang_Cach], 
                [_duongDanNguon + "ThuyHe/" + _SongSuoiL, "EDGE", _khoang_Cach]])
            
            arcpy.CopyFeatures_management(_duongDanNguon + "BienGioiDiaGioi/" + _DuongDiaGioi, _duongDanDich + "BienGioiDiaGioi/" + _DuongDiaGioi)
            arcpy.AddMessage("Hoan thanh !!!")
        except:
            arcpy.AddError("Error")
            arcpy.AddMessage(arcpy.GetMessages())
        return

#---------------------------Đường biên giới------------------------------------#
class DuongBienGioi(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.DuongBienGioi"
        self.description = "Tiep bien lai duong bien gioi"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Khoang cach Snap",
            name="iput0",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param0.value = "20 Meters"
        params = [param0]
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
            arcpy.env.overwriteOutput = 1
            _duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb/"
            _duongDanDich = "C:/Generalize_25_50/50K_Final.gdb/"
            _DuongBienGioi = "DuongBienGioi"
            _KenhMuongL = "KenhMuongL"
            _SongSuoiL = "SongSuoiL"
            _khoang_Cach = parameters[0].valueAsText
            arcpy.Densify_edit(_duongDanNguon + "BienGioiDiaGioi/" + _DuongBienGioi, "OFFSET",None, "0.1 Meters",None)
            arcpy.Snap_edit(_duongDanNguon + "BienGioiDiaGioi/" + _DuongBienGioi, [[_duongDanNguon + "ThuyHe/" + _KenhMuongL, "VERTEX", _khoang_Cach], 
                [_duongDanNguon + "ThuyHe/" + _KenhMuongL, "EDGE", _khoang_Cach]])

            arcpy.Snap_edit(_duongDanNguon + "BienGioiDiaGioi/" + _DuongBienGioi, [[_duongDanNguon + "ThuyHe/" + _SongSuoiL, "VERTEX", _khoang_Cach], 
                [_duongDanNguon + "ThuyHe/" + _SongSuoiL, "EDGE", _khoang_Cach]])
            
            arcpy.CopyFeatures_management(_duongDanNguon + "BienGioiDiaGioi/" + _DuongBienGioi, _duongDanDich + "BienGioiDiaGioi/" + _DuongBienGioi)
            arcpy.AddMessage("Hoan thanh !!!")
        except:
            arcpy.AddError("Error")
            arcpy.AddMessage(arcpy.GetMessages())
        return
