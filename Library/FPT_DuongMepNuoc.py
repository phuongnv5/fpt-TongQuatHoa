# -*- coding: utf-8 -*-
import arcpy
import arcpy.management as DM
import arcpy.analysis as AN
import os
class FPT_DuongMepNuoc:
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
if __name__=='__main__':
    abc = 1