import arcpy
import arcpy.management as DM
import arcpy.analysis as AN
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [DuongBoNuoc_MepNuoc]

class DuongBoNuoc:
    def __init__(self, duong_dan_nguon, lop_thuy_he, lop_bai_boi, khoang_Cach, loai_ranh_gioi_nuoc_mat):
        self.duong_dan_nguon = duong_dan_nguon
        self.lop_thuy_he = lop_thuy_he
        self.lop_bai_boi = lop_bai_boi
        self.khoang_Cach = khoang_Cach
        self.loai_ranh_gioi_nuoc_mat = loai_ranh_gioi_nuoc_mat
        
    def xu_ly_duong_bo_nuoc (self):
        arcpy.env.overwriteOutput = 1
        # Khai bao bien
        lop_thuy_he = self.duong_dan_nguon + "ThuyHe/" + self.lop_thuy_he
        lop_bai_boi = self.duong_dan_nguon + "ThuyHe/" + self.lop_bai_boi
        lop_thuy_he_Copy = lop_thuy_he + "_Copy"
        lop_thuy_he_Copy_Agg = lop_thuy_he + "_Copy_Agg"
        lop_thuy_he_Copy_Agg_Tbl = self.duong_dan_nguon + self.lop_thuy_he.replace("/","_") + "_Copy_Agg_Tbl"
        
        lop_thuy_he_DuongBoNuoc = lop_thuy_he + "_DuongBoNuoc"
        #
        #snap
        #arcpy.Densify_edit(lop_thuy_he_Copy, "DISTANCE","0.1 Meters",None ,None)
        #arcpy.Densify_edit(lop_thuy_he_Copy, "OFFSET",None, "0.1 Meters",None)
        arcpy.Snap_edit(lop_bai_boi, [[lop_thuy_he, "EDGE", self.khoang_Cach]])
        #Integrate
        '''
        arcpy.Integrate_management([[lop_thuy_he, 1], [lop_bai_boi, 2]], "0.5 Meters")
        
        arcpy.Snap_edit(lop_bai_boi, 
            [[lop_thuy_he, "VERTEX", "5 Meters"], 
                [lop_thuy_he, "EDGE", "5 Meters"],[lop_thuy_he, "END", "5 Meters"]])
        '''
        #Append
        arcpy.CopyFeatures_management(lop_thuy_he, lop_thuy_he_Copy)
        arcpy.AddField_management(lop_thuy_he_Copy, "CODE", "LONG", None, None, None,"CODE", "NULLABLE")
        arcpy.CalculateField_management(lop_thuy_he_Copy, "CODE", "!OBJECTID!", "PYTHON_9.3")
        arcpy.Append_management([lop_bai_boi], lop_thuy_he_Copy, "NO_TEST",None,None)
        #AggregatePolygons
        arcpy.AggregatePolygons_cartography(lop_thuy_he_Copy, lop_thuy_he_Copy_Agg, 
            "0.001 Meters", "0 SquareMeters", "0 SquareMeters", "NON_ORTHOGONAL", "", lop_thuy_he_Copy_Agg_Tbl)
        
        DM.JoinField(lop_thuy_he_Copy_Agg_Tbl, "INPUT_FID", lop_thuy_he_Copy, "OBJECTID", None)
        #danh dau sông có diện tích lớn nhất trong group
        rows2 = arcpy.SearchCursor(lop_thuy_he_Copy_Agg_Tbl,
                        sort_fields="OUTPUT_FID A")
        _outPut_id = 0
        _area_max = 0
        my_dict = {}
        for row2 in rows2:
            if row2.getValue("CODE") is not None:
                if _outPut_id == row2.getValue("OUTPUT_FID"):
                    if _area_max < row2.getValue("Shape_Area"):
                        _area_max = row2.getValue("Shape_Area")
                        my_dict[row2.getValue("OUTPUT_FID")] = _area_max
                else:
                    _area_max = row2.getValue("Shape_Area")
                    my_dict[row2.getValue("OUTPUT_FID")] = _area_max
                _outPut_id = row2.getValue("OUTPUT_FID")
        #Update lại bảng join
        rows_update = arcpy.UpdateCursor(lop_thuy_he_Copy_Agg_Tbl)
        for row_update in rows_update:
            if row_update.getValue("CODE") is None:
                rows_update.deleteRow(row_update)
            else:
                if row_update.getValue("Shape_Area") != my_dict[row_update.getValue("OUTPUT_FID")]:
                    rows_update.deleteRow(row_update)
        del row_update
        del rows_update
        DM.JoinField(lop_thuy_he_Copy_Agg, "OBJECTID", lop_thuy_he_Copy_Agg_Tbl, "OUTPUT_FID", None)
        #Xóa bãi bồi trong Aggregate
        rows_update = arcpy.UpdateCursor(lop_thuy_he_Copy_Agg)
        for row_update in rows_update:
            if row_update.getValue("CODE") is None:
                rows_update.deleteRow(row_update)
        del row_update
        del rows_update
        #FeatureToLine
        arcpy.FeatureToLine_management([lop_thuy_he_Copy_Agg], lop_thuy_he_DuongBoNuoc, None, "ATTRIBUTES")
        #Chỉnh sửa lại field
        arcpy.DeleteField_management(lop_thuy_he_DuongBoNuoc, ["FID_SongSuoiA_Copy2_Agg","OUTPUT_FID","INPUT_FID","loaiTrangThaiNuocMat",
            "ten","doRong","SongSuoiA_Rep_ID","SongSuoiA_Rep_OVERRIDE","RuleID","Override","Shape_Length_1","Shape_Area_1","CODE",
            "loaiTrangThaiDuongBoNuoc","loaiRanhGioiNuocMat"])
        arcpy.AddField_management(lop_thuy_he_DuongBoNuoc, "loaiTrangThaiDuongBoNuoc", "SHORT", None, None, None,
                        "Loai trang thai duong bo nuoc", "NULLABLE",None,"LoaiTrangThaiDuongBoNuoc")
        arcpy.AddField_management(lop_thuy_he_DuongBoNuoc, "loaiRanhGioiNuocMat", "LONG", None, None, None,
                        "Loai ranh gioi nuoc mat", "NULLABLE",None, "LoaiRanhGioiNuocMat")
        arcpy.CalculateField_management(lop_thuy_he_DuongBoNuoc, "loaiTrangThaiDuongBoNuoc", 1,"PYTHON_9.3")
        arcpy.CalculateField_management(lop_thuy_he_DuongBoNuoc, "loaiRanhGioiNuocMat", self.loai_ranh_gioi_nuoc_mat,"PYTHON_9.3")
        arcpy.AssignDefaultToField_management(lop_thuy_he_DuongBoNuoc, "maDoiTuong", "LG01", None)
        arcpy.CalculateField_management(lop_thuy_he_DuongBoNuoc, "maDoiTuong", "'LG01'","PYTHON_9.3")

    def append_DuongBoNuoc (self):
        _matNuocTinh_SongSuoiA = self.duong_dan_nguon + "ThuyHe/SongSuoiA_DuongBoNuoc"
        _matNuocTinh_DuongBoNuoc = self.duong_dan_nguon + "ThuyHe/MatNuocTinh_DuongBoNuoc"
        _kenhMuongA_DuongBoNuoc = self.duong_dan_nguon + "ThuyHe/KenhMuongA_DuongBoNuoc"
        _input_Datasets = [_matNuocTinh_DuongBoNuoc,_kenhMuongA_DuongBoNuoc]
        arcpy.Append_management(_input_Datasets, _matNuocTinh_SongSuoiA, "NO_TEST",None,None)

class DuongMepNuoc:
    def __init__(self, duong_dan_nguon, lop_thuy_he, lop_bai_boi, lop_duong_mep_nuoc, loai_ranh_gioi_nuoc_mat):
        self.duong_dan_nguon = duong_dan_nguon
        self.lop_thuy_he = lop_thuy_he
        self.lop_bai_boi = lop_bai_boi
        self.lop_duong_mep_nuoc = lop_duong_mep_nuoc
        self.loai_ranh_gioi_nuoc_mat = loai_ranh_gioi_nuoc_mat
    
    def xu_ly_duong_mep_nuoc (self):
        inFeatures = [[self.duong_dan_nguon + "ThuyHe/" + self.lop_thuy_he,1], [self.duong_dan_nguon + "ThuyHe/" + self.lop_bai_boi,2]]
        intersectOutput = self.duong_dan_nguon + "ThuyHe/" + self.lop_duong_mep_nuoc + "_" + self.lop_thuy_he
        arcpy.Intersect_analysis(inFeatures, intersectOutput, "NO_FID", None, "LINE")
        arcpy.DeleteField_management(intersectOutput, ["loaiTrangThaiNuocMat","ten","doRong","maNhanDang_1",
        "ngayThuNhan_1","ngayCapNhat_1","maDoiTuong_1","ten_1","loaiBaiBoi","loaiTrangThaiXuatLo","nguonDuLieu_1","maTrinhBay_1","tenManh_1",
        "soPhienHieuManhBanDo_1"])
        arcpy.AddField_management(intersectOutput, "loaiRanhGioiNuocMat", "LONG", None, None, None,
                        "Loai ranh gioi nuoc mat", "NULLABLE",None, "LoaiRanhGioiNuocMat")
        arcpy.CalculateField_management(intersectOutput, "loaiRanhGioiNuocMat", self.loai_ranh_gioi_nuoc_mat,"PYTHON_9.3")
        arcpy.AssignDefaultToField_management(intersectOutput, "maDoiTuong", "LG02", None)
        arcpy.CalculateField_management(intersectOutput, "maDoiTuong", "'LG02'","PYTHON_9.3")

    def append_DuongMepNuoc (self):
        _duongMepNuoc_SongSuoiA = self.duong_dan_nguon + "ThuyHe/" + self.lop_duong_mep_nuoc + "_" + "SongSuoiA"
        _duongMepNuoc_MatNuocTinh = self.duong_dan_nguon + "ThuyHe/" + self.lop_duong_mep_nuoc + "_" + "MatNuocTinh"
        _duongMepNuoc_KenhMuongA = self.duong_dan_nguon + "ThuyHe/" + self.lop_duong_mep_nuoc + "_" + "KenhMuongA"
        _input_Datasets = [_duongMepNuoc_MatNuocTinh,_duongMepNuoc_KenhMuongA]
        arcpy.Append_management(_input_Datasets, _duongMepNuoc_SongSuoiA, "NO_TEST",None,None)

#---------------------------------------------------Đường bờ nước - Mép nước
class DuongBoNuoc_MepNuoc(object):
    def __init__(self):
        """Tạo Đường Bờ Nước và Mép Nước"""
        self.label = "1.Tao DuongBoNuoc & MepNuoc"
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
            obj_duong_bo_nuoc = DuongBoNuoc(_duongDanNguon, _songSuoiA,_baiBoiA,_khoang_Cach, 6)
            obj_duong_bo_nuoc.xu_ly_duong_bo_nuoc()
            #--------------------------Xử lý mặt nước tĩnh ------------------------------
            arcpy.AddMessage("Xu ly Mat nuoc tinh")
            obj_duong_bo_nuoc = DuongBoNuoc(_duongDanNguon, _matNuocTinh,_baiBoiA,_khoang_Cach, 1)
            obj_duong_bo_nuoc.xu_ly_duong_bo_nuoc()
            #--------------------------Xử lý kênh mương------------------------------
            arcpy.AddMessage("Xu ly Kenh muong")
            obj_duong_bo_nuoc = DuongBoNuoc(_duongDanNguon, _kenhMuongA,_baiBoiA,_khoang_Cach, 4)
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
            obj_duong_mep_nuoc = DuongMepNuoc(_duongDanNguon, _songSuoiA, _baiBoiA, _duongMepNuoc, 6)
            obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
            arcpy.AddMessage("Xu ly Mat nuoc tinh")
            obj_duong_mep_nuoc = DuongMepNuoc(_duongDanNguon, _matNuocTinh, _baiBoiA, _duongMepNuoc, 1)
            obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
            arcpy.AddMessage("Xu ly Kenh muong")
            obj_duong_mep_nuoc = DuongMepNuoc(_duongDanNguon, _kenhMuongA, _baiBoiA, _duongMepNuoc, 4)
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

