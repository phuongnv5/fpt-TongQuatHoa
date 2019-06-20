# -*- coding: utf-8 -*-
import arcpy
import arcpy.management as DM
import arcpy.analysis as AN
import os
import sys
class FPT_DuongBoNuoc:
    def __init__(self, duong_dan_nguon, duong_dan_dich, khoang_Cach):
        self.duong_dan_nguon = duong_dan_nguon
        self.duong_dan_dich = duong_dan_dich
        self.khoang_Cach = khoang_Cach
        
    def xu_ly_duong_bo_nuoc (self):
        arcpy.env.overwriteOutput = 1
        # Khai bao bien
        SongSuoiA = self.duong_dan_nguon + "ThuyHe/SongSuoiA"
        MatNuocTinh = self.duong_dan_nguon + "ThuyHe/MatNuocTinh"
        KenhMuongA = self.duong_dan_nguon + "ThuyHe/KenhMuongA"
        lop_bai_boi = self.duong_dan_nguon + "ThuyHe/BaiBoiA"
        SongSuoiA_Copy = SongSuoiA + "_Copy"
        MatNuocTinh_Copy = MatNuocTinh + "_Copy"
        KenhMuongA_Copy = KenhMuongA + "_Copy"
        lop_thuy_he_Copy_Agg = SongSuoiA_Copy + "_Agg"
        lop_thuy_he_Copy_Agg_Tbl = self.duong_dan_nguon + "SongSuoiA_Copy_Agg_Tbl"
        
        lop_thuy_he_DuongBoNuoc = SongSuoiA_Copy + "_DuongBoNuoc"

        arcpy.Snap_edit(lop_bai_boi, [[KenhMuongA, "EDGE", self.khoang_Cach], [MatNuocTinh, "EDGE", self.khoang_Cach], [SongSuoiA, "EDGE", self.khoang_Cach]])
        #Append
        arcpy.CopyFeatures_management(SongSuoiA, SongSuoiA_Copy)
        arcpy.AddField_management(SongSuoiA_Copy, "LOAI_RANH_GIOI", "LONG", None, None, None,"LOAI_RANH_GIOI", "NULLABLE")
        arcpy.CalculateField_management(SongSuoiA_Copy, "LOAI_RANH_GIOI", 6, "PYTHON_9.3")
        arcpy.CopyFeatures_management(MatNuocTinh, MatNuocTinh_Copy)
        arcpy.AddField_management(MatNuocTinh_Copy, "LOAI_RANH_GIOI", "LONG", None, None, None,"LOAI_RANH_GIOI", "NULLABLE")
        arcpy.CalculateField_management(MatNuocTinh_Copy, "LOAI_RANH_GIOI", 1, "PYTHON_9.3")
        arcpy.CopyFeatures_management(KenhMuongA, KenhMuongA_Copy)
        arcpy.AddField_management(KenhMuongA_Copy, "LOAI_RANH_GIOI", "LONG", None, None, None,"LOAI_RANH_GIOI", "NULLABLE")
        arcpy.CalculateField_management(KenhMuongA_Copy, "LOAI_RANH_GIOI", 4, "PYTHON_9.3")
        arcpy.Append_management([lop_bai_boi, MatNuocTinh_Copy, KenhMuongA_Copy], SongSuoiA_Copy, "NO_TEST",None,None)
        #AggregatePolygons
        arcpy.AggregatePolygons_cartography(SongSuoiA_Copy, lop_thuy_he_Copy_Agg, 
            "0.001 Meters", "0 SquareMeters", "0 SquareMeters", "NON_ORTHOGONAL", "", lop_thuy_he_Copy_Agg_Tbl)
        
        DM.JoinField(lop_thuy_he_Copy_Agg_Tbl, "INPUT_FID", SongSuoiA_Copy, "OBJECTID", None)
        #danh dau sông có diện tích lớn nhất trong group
        rows2 = arcpy.SearchCursor(lop_thuy_he_Copy_Agg_Tbl,
                        sort_fields="OUTPUT_FID A")
        _outPut_id = 0
        _area_max = 0
        my_dict = {}
        for row2 in rows2:
            if row2.getValue("LOAI_RANH_GIOI") is not None:
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
            if row_update.getValue("LOAI_RANH_GIOI") is None:
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
            if row_update.getValue("LOAI_RANH_GIOI") is None:
                rows_update.deleteRow(row_update)
        del row_update
        del rows_update
        #FeatureToLine
        arcpy.FeatureToLine_management([lop_thuy_he_Copy_Agg], lop_thuy_he_DuongBoNuoc, None, "ATTRIBUTES")
        #Chỉnh sửa lại field
        arcpy.DeleteField_management(lop_thuy_he_DuongBoNuoc, ["FID_SongSuoiA_Copy2_Agg","OUTPUT_FID","INPUT_FID","loaiTrangThaiNuocMat",
            "ten","doRong","SongSuoiA_Rep_ID","SongSuoiA_Rep_OVERRIDE","RuleID","Override","Shape_Length_1","Shape_Area_1",
            "loaiTrangThaiDuongBoNuoc","loaiRanhGioiNuocMat"])
        arcpy.AddField_management(lop_thuy_he_DuongBoNuoc, "loaiTrangThaiDuongBoNuoc", "SHORT", None, None, None,
                        "Loai trang thai duong bo nuoc", "NULLABLE",None,"LoaiTrangThaiDuongBoNuoc")
        arcpy.AddField_management(lop_thuy_he_DuongBoNuoc, "loaiRanhGioiNuocMat", "LONG", None, None, None,
                        "Loai ranh gioi nuoc mat", "NULLABLE",None, "LoaiRanhGioiNuocMat")
        arcpy.CalculateField_management(lop_thuy_he_DuongBoNuoc, "loaiTrangThaiDuongBoNuoc", 1,"PYTHON_9.3")
        arcpy.CalculateField_management(lop_thuy_he_DuongBoNuoc, "loaiRanhGioiNuocMat", "!LOAI_RANH_GIOI!","PYTHON_9.3")
        arcpy.AssignDefaultToField_management(lop_thuy_he_DuongBoNuoc, "maDoiTuong", "LG01", None)
        arcpy.CalculateField_management(lop_thuy_he_DuongBoNuoc, "maDoiTuong", "'LG01'","PYTHON_9.3")
        arcpy.DeleteField_management(lop_thuy_he_DuongBoNuoc, ["LOAI_RANH_GIOI"])


        DuongBoNuoc_Path = self.duong_dan_nguon + "ThuyHe/DuongBoNuoc"
        if int(arcpy.GetCount_management(DuongBoNuoc_Path).getOutput(0)) > 0:
            arcpy.DeleteFeatures_management(DuongBoNuoc_Path)
        
        duongBoNuocFields = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiTrangThaiDuongBoNuoc", "loaiRanhGioiNuocMat", 
                            "nguonDuLieu", "maTrinhBay", "tenManh", "soPhienHieuManhBanDo"]
        duongBoNuocFields2 = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiTrangThaiDuongBoNuoc", "loaiRanhGioiNuocMat", 
                            "nguonDuLieu", "maTrinhBay", "tenManh", "soPhienHieuManhBanDo", "DuongBoNuoc_Rep_ID"]
        with arcpy.da.SearchCursor(lop_thuy_he_DuongBoNuoc, duongBoNuocFields) as sCur:
            with arcpy.da.InsertCursor(DuongBoNuoc_Path, duongBoNuocFields2) as iCur:
                for sRow in sCur:
                    iCur.insertRow([sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], sRow[5], sRow[6], sRow[7], sRow[8], sRow[9], sRow[10], 1])
        arcpy.CopyFeatures_management(DuongBoNuoc_Path, self.duong_dan_dich + "ThuyHe/DuongBoNuoc")

    '''
    def append_DuongBoNuoc (self):
        _matNuocTinh_SongSuoiA = self.duong_dan_nguon + "ThuyHe/SongSuoiA_DuongBoNuoc"
        _matNuocTinh_DuongBoNuoc = self.duong_dan_nguon + "ThuyHe/MatNuocTinh_DuongBoNuoc"
        _kenhMuongA_DuongBoNuoc = self.duong_dan_nguon + "ThuyHe/KenhMuongA_DuongBoNuoc"
        _input_Datasets = [_matNuocTinh_DuongBoNuoc,_kenhMuongA_DuongBoNuoc]
        arcpy.Append_management(_input_Datasets, _matNuocTinh_SongSuoiA, "NO_TEST",None,None)

        DuongBoNuoc_Path = self.duong_dan_nguon + "ThuyHe/DuongBoNuoc"
        if int(arcpy.GetCount_management(DuongBoNuoc_Path).getOutput(0)) > 0:
            arcpy.DeleteFeatures_management(DuongBoNuoc_Path)
        
        duongBoNuocFields = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiTrangThaiDuongBoNuoc", "loaiRanhGioiNuocMat", 
                            "nguonDuLieu", "maTrinhBay", "tenManh", "soPhienHieuManhBanDo"]
        duongBoNuocFields2 = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiTrangThaiDuongBoNuoc", "loaiRanhGioiNuocMat", 
                            "nguonDuLieu", "maTrinhBay", "tenManh", "soPhienHieuManhBanDo", "DuongBoNuoc_Rep_ID"]
        with arcpy.da.SearchCursor(_matNuocTinh_SongSuoiA, duongBoNuocFields) as sCur:
            with arcpy.da.InsertCursor(DuongBoNuoc_Path, duongBoNuocFields2) as iCur:
                for sRow in sCur:
                    iCur.insertRow([sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], sRow[5], sRow[6], sRow[7], sRow[8], sRow[9], sRow[10], 1])
        arcpy.CopyFeatures_management(DuongBoNuoc_Path, self.duong_dan_dich + "ThuyHe/DuongBoNuoc")
    '''
if __name__=='__main__':
    _duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb/"
    _duongDanDich = "C:/Generalize_25_50/50K_Final.gdb/"
    _khoang_Cach = "1 Meters"#sys.argv[1:]#"1 Meters"
    arcpy.AddMessage("Bat dau xu ly Duong Bo Nuoc")
    obj_duong_bo_nuoc = FPT_DuongBoNuoc(_duongDanNguon, _duongDanDich,_khoang_Cach)
    obj_duong_bo_nuoc.xu_ly_duong_bo_nuoc()
