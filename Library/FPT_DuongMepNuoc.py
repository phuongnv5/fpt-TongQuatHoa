# -*- coding: utf-8 -*-
import arcpy
import arcpy.management as DM
import arcpy.analysis as AN
import os
class FPT_DuongMepNuoc:
    def __init__(self, duong_dan_nguon, duong_dan_dich, lop_thuy_he, lop_bai_boi, lop_duong_mep_nuoc, loai_ranh_gioi_nuoc_mat):
        self.duong_dan_nguon = duong_dan_nguon
        self.duong_dan_dich = duong_dan_dich
        self.lop_thuy_he = lop_thuy_he
        self.lop_bai_boi = lop_bai_boi
        self.lop_duong_mep_nuoc = lop_duong_mep_nuoc
        self.loai_ranh_gioi_nuoc_mat = loai_ranh_gioi_nuoc_mat
    
    def xu_ly_duong_mep_nuoc (self):
        arcpy.env.overwriteOutput = 1
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

        DuongMepNuoc_Path = self.duong_dan_nguon + "ThuyHe/DuongMepNuoc"
        if int(arcpy.GetCount_management(DuongMepNuoc_Path).getOutput(0)) > 0:
            arcpy.DeleteFeatures_management(DuongMepNuoc_Path)
        duongMepNuocFields = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiRanhGioiNuocMat", "nguonDuLieu", 
                            "maTrinhBay", "tenManh", "soPhienHieuManhBanDo"]
        duongMepNuocFields2 = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiRanhGioiNuocMat", "nguonDuLieu", 
                            "maTrinhBay", "tenManh", "soPhienHieuManhBanDo", "DuongMepNuoc_Rep_ID"]
        with arcpy.da.SearchCursor(_duongMepNuoc_SongSuoiA, duongMepNuocFields) as sCur:
            with arcpy.da.InsertCursor(DuongMepNuoc_Path, duongMepNuocFields2) as iCur:
                for sRow in sCur:
                    iCur.insertRow([sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], sRow[5], sRow[6], sRow[7], sRow[8], sRow[9], 1])
        arcpy.CopyFeatures_management(DuongMepNuoc_Path, self.duong_dan_dich + "ThuyHe/DuongMepNuoc")
if __name__=='__main__':
    _duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb/"
    _duongDanDich = "C:/Generalize_25_50/50K_Final.gdb/"
    _baiBoiA = "BaiBoiA"
    _songSuoiA = "SongSuoiA"
    _matNuocTinh = "MatNuocTinh"
    _kenhMuongA = "KenhMuongA"
    _duongMepNuoc = "DuongMepNuoc"
    _khoang_Cach = "1 Meters"

    arcpy.AddMessage("Bat dau xu ly Duong Mep Nuoc")
    arcpy.AddMessage("Xu ly Song Suoi")
    obj_duong_mep_nuoc = FPT_DuongMepNuoc(_duongDanNguon, _duongDanDich, _songSuoiA, _baiBoiA, _duongMepNuoc, 6)
    
    obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
    arcpy.AddMessage("Xu ly Mat nuoc tinh")
    obj_duong_mep_nuoc = FPT_DuongMepNuoc(_duongDanNguon, _duongDanDich,_matNuocTinh, _baiBoiA, _duongMepNuoc, 1)
    obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
    arcpy.AddMessage("Xu ly Kenh muong")
    obj_duong_mep_nuoc = FPT_DuongMepNuoc(_duongDanNguon, _duongDanDich,_kenhMuongA, _baiBoiA, _duongMepNuoc, 4)
    obj_duong_mep_nuoc.xu_ly_duong_mep_nuoc()
    
    obj_duong_mep_nuoc.append_DuongMepNuoc()
    
    #--------------------------COPY BAI BOI A--------------------------------------
    arcpy.CopyFeatures_management(_duongDanNguon + "ThuyHe/BaiBoiA" ,_duongDanDich + "ThuyHe/BaiBoiA")
