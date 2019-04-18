import arcpy
import arcpy.management as DM
import arcpy.analysis as AN
import os

#reload modules
import Library.FPT_DuongBoNuoc
reload(Library.FPT_DuongBoNuoc)
import Library.FPT_DuongMepNuoc
reload(Library.FPT_DuongMepNuoc)
import Library.FPT_Simplify
reload(Library.FPT_Simplify)


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Simplify]


#---------------------------------------------------Simplify
class Simplify(object):
    def __init__(self):
        """Simplify"""
        self.label = "1.Simplify"
        self.description = "Simpify tất ca cac lop"
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
            arcpy.env.overwriteOutput = 1
            #obj = FPT_Simplify("25 Meters")
            #obj.simplify()
        except:
            arcpy.AddError("Error")
            arcpy.AddMessage(arcpy.GetMessages())
        return
'''
#---------------------------------------------------Đường bờ nước - Mép nước
class DuongBoNuoc_MepNuoc(object):
    def __init__(self):
        """Tạo Đường Bờ Nước và Mép Nước"""
        self.label = "2.Tao DuongBoNuoc & MepNuoc"
        self.description = "Tao Duong Bo Nuoc va Duong Mep Nuoc"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Khoang cach Snap",
            name="iput0",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param0.value = "5 Meters"
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
            _baiBoiA = "BaiBoiA"
            _songSuoiA = "SongSuoiA"
            _matNuocTinh = "MatNuocTinh"
            _kenhMuongA = "KenhMuongA"
            _duongMepNuoc = "DuongMepNuoc"
            _khoang_Cach = parameters[0].valueAsText
            
            #--------------------------ĐƯỜNG BỜ NƯỚC--------------------------------------
            #--------------------------Tiền xử lý bãi bồi---------------------------------
            arcpy.AddMessage("Bat dau xu ly Duong Bo Nuoc")
            arcpy.AddMessage("Tien xu ly bai boi")
            arcpy.Densify_edit(_duongDanNguon + "ThuyHe/" + _baiBoiA, "DISTANCE","0.1 Meters",None ,None)
            #arcpy.Densify_edit(_baiBoiA_Copy, "OFFSET",None, "0.1 Meters",None)
            #--------------------------Xử lý sông suối ------------------------------
            arcpy.AddMessage("Xu ly Song Suoi")
            obj_duong_bo_nuoc = FPT_DuongBoNuoc(_duongDanNguon, _songSuoiA,_baiBoiA,_khoang_Cach, 6)
            obj_duong_bo_nuoc.xu_ly_duong_bo_nuoc()
            #--------------------------Xử lý mặt nước tĩnh ------------------------------
            arcpy.AddMessage("Xu ly Mat nuoc tinh")
            obj_duong_bo_nuoc = FPT_DuongBoNuoc(_duongDanNguon, _matNuocTinh,_baiBoiA,_khoang_Cach, 1)
            obj_duong_bo_nuoc.xu_ly_duong_bo_nuoc()
            #--------------------------Xử lý kênh mương------------------------------
            arcpy.AddMessage("Xu ly Kenh muong")
            obj_duong_bo_nuoc = FPT_DuongBoNuoc(_duongDanNguon, _kenhMuongA,_baiBoiA,_khoang_Cach, 4)
            obj_duong_bo_nuoc.xu_ly_duong_bo_nuoc()
            
            #--------------------------Append---------------------------------------
            obj_duong_bo_nuoc.append_DuongBoNuoc()
            #--------------------------Copy Duong Bo Nuoc sang dich
            arcpy.CopyFeatures_management(_duongDanNguon + "ThuyHe/SongSuoiA_DuongBoNuoc",
                _duongDanNguon + "ThuyHe/DuongBoNuoc")
            arcpy.CopyFeatures_management(_duongDanNguon + "ThuyHe/SongSuoiA_DuongBoNuoc",
                _duongDanDich + "ThuyHe/DuongBoNuoc")
            
            #--------------------------ĐƯỜNG MÉP NƯỚC--------------------------------------
            arcpy.AddMessage("Bat dau xu ly Duong Mep Nuoc")
            arcpy.AddMessage("Xu ly Song Suoi")
            obj_duong_mep_nuoc = FPT_DuongMepNuoc(_duongDanNguon, _songSuoiA, _baiBoiA, _duongMepNuoc, 6)
            obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
            arcpy.AddMessage("Xu ly Mat nuoc tinh")
            obj_duong_mep_nuoc = FPT_DuongMepNuoc(_duongDanNguon, _matNuocTinh, _baiBoiA, _duongMepNuoc, 1)
            obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
            arcpy.AddMessage("Xu ly Kenh muong")
            obj_duong_mep_nuoc = FPT_DuongMepNuoc(_duongDanNguon, _kenhMuongA, _baiBoiA, _duongMepNuoc, 4)
            obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
            obj_duong_mep_nuoc.append_DuongMepNuoc()
            arcpy.CopyFeatures_management(_duongDanNguon + "ThuyHe/DuongMepNuoc_SongSuoiA",
                _duongDanNguon + "ThuyHe/DuongMepNuoc")
            arcpy.CopyFeatures_management(_duongDanNguon + "ThuyHe/DuongMepNuoc_SongSuoiA",
                _duongDanDich + "ThuyHe/DuongMepNuoc")
            #--------------------------COPY BAI BOI A--------------------------------------
            arcpy.CopyFeatures_management(_duongDanNguon + "ThuyHe/BaiBoiA" ,_duongDanDich + "ThuyHe/BaiBoiA")
            arcpy.AddMessage("Hoan thanh !!!")
            
        except:
            arcpy.AddError("Error")
            arcpy.AddMessage(arcpy.GetMessages())
        return
'''