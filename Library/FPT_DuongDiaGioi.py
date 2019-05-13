# -*- coding: utf-8 -*-
import arcpy
import os
import json
import sys
import inspect

class FPT_DuongDiaGioi:
    def __init__(self):
        abc = 1
    def CreateDuongDiaGioi(self):
        try:
            arcpy.env.overwriteOutput = 1
            duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb"
            duongDanDich = "C:/Generalize_25_50/50K_Final.gdb"
            arcpy.env.workspace = duongDanNguon + "/BienGioiDiaGioi"
            DiaPhan_Name = "DiaPhan"
            DiaPhan_Lyr = "DiaPhan_Lyr"
            DiaPhan_Path = duongDanNguon + "/BienGioiDiaGioi/" + DiaPhan_Name
            DiaPhan_Xa_Path = DiaPhan_Path + "_Xa"
            DiaPhan_Huyen_Path = DiaPhan_Path + "_Huyen"
            DiaPhan_Tinh_Path = DiaPhan_Path + "_Tinh"
            intersect_Xa_Path = duongDanNguon + "/BienGioiDiaGioi/DuongDiaGioi_Xa"
            intersect_Huyen_Path = duongDanNguon + "/BienGioiDiaGioi/DuongDiaGioi_Huyen"
            intersect_Tinh_Path = duongDanNguon + "/BienGioiDiaGioi/DuongDiaGioi_Tinh"
            joint_Xa_Path = duongDanNguon + "/BienGioiDiaGioi/DuongDiaGioi_Xa_Join"
            joint_Huyen_Path = duongDanNguon + "/BienGioiDiaGioi/DuongDiaGioi_Huyen_Join"
            joint_Tinh_Path = duongDanNguon + "/BienGioiDiaGioi/DuongDiaGioi_Tinh_Join"
            DuongDiaGioi_Name = "DuongDiaGioi"
            DuongDiaGioi_Path = duongDanNguon + "/BienGioiDiaGioi/" + DuongDiaGioi_Name
            DuongDiaGioi_Dich_Path = duongDanDich + "/BienGioiDiaGioi/" + DuongDiaGioi_Name
            arcpy.Integrate_management([[DiaPhan_Path, 1]], "1 Meters")

            #Xa
            arcpy.MakeFeatureLayer_management(DiaPhan_Path, DiaPhan_Lyr)
            arcpy.SelectLayerByAttribute_management(DiaPhan_Lyr, "NEW_SELECTION", "doiTuong = 3")
            arcpy.CopyFeatures_management(DiaPhan_Lyr, DiaPhan_Xa_Path)
            arcpy.Intersect_analysis([[DiaPhan_Xa_Path,1]], intersect_Xa_Path, "ALL", None, "LINE")
            arcpy.DeleteIdentical_management(intersect_Xa_Path, ["Shape"], None, None)
            arcpy.AddField_management(intersect_Xa_Path, "loaiHienTrangPhapLy", "SHORT", None, None, None,"loaiHienTrangPhapLy", "NULLABLE")
            arcpy.AddField_management(intersect_Xa_Path, "donViHanhChinhLienKeTrai", "TEXT", None, None, None,"donViHanhChinhLienKeTrai", "NULLABLE")
            arcpy.AddField_management(intersect_Xa_Path, "donViHanhChinhLienKePhai", "TEXT", None, None, None,"donViHanhChinhLienKePhai", "NULLABLE")
            arcpy.AddField_management(intersect_Xa_Path, "chieuDai", "DOUBLE", None, None, None,"chieuDai", "NULLABLE")
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(DiaPhan_Xa_Path)
            for field in fieldMappings.fields:
                if field.name not in ["doiTuong", "danhTuChung", "diaDanh"]:
                    fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
            arcpy.SpatialJoin_analysis(target_features = intersect_Xa_Path, join_features = DiaPhan_Xa_Path, out_feature_class = joint_Xa_Path, 
                                    join_operation = "JOIN_ONE_TO_MANY", join_type = "KEEP_ALL", field_mapping = fieldMappings, match_option = "WITHIN")
            with arcpy.da.UpdateCursor(intersect_Xa_Path, ["OID@" ,"FID_DiaPhan_Xa", "loaiHienTrangPhapLy", "donViHanhChinhLienKeTrai", "donViHanhChinhLienKePhai", "chieuDai", "Shape_Length", "doiTuong"]) as uCur:
                for uRow in uCur:
                    with arcpy.da.SearchCursor(joint_Xa_Path, ["TARGET_FID", "JOIN_FID", "doiTuong", "danhTuChung", "diaDanh"]) as sCur:
                        for sRow in sCur:
                            if uRow[0] == sRow[0] and sRow[2] == 3:
                                if uRow[1] == sRow[1]:
                                    uRow[2] = 1
                                    uRow[5] = uRow[6]
                                    uRow[3] = sRow[3] + " " + sRow[4]
                                    uRow[7] = sRow[2]
                                    uCur.updateRow(uRow)
                                else:
                                    uRow[2] = 1
                                    uRow[5] = uRow[6]
                                    uRow[4] = sRow[3] + " " + sRow[4]
                                    uRow[7] = sRow[2]
                                    uCur.updateRow(uRow)
            #Huyen
            arcpy.SelectLayerByAttribute_management(DiaPhan_Lyr, "NEW_SELECTION", "doiTuong = 2")
            arcpy.CopyFeatures_management(DiaPhan_Lyr, DiaPhan_Huyen_Path)
            arcpy.Intersect_analysis([[DiaPhan_Huyen_Path,1]], intersect_Huyen_Path, "ALL", None, "LINE")
            arcpy.DeleteIdentical_management(intersect_Huyen_Path, ["Shape"], None, None)
            arcpy.AddField_management(intersect_Huyen_Path, "loaiHienTrangPhapLy", "SHORT", None, None, None,"loaiHienTrangPhapLy", "NULLABLE")
            arcpy.AddField_management(intersect_Huyen_Path, "donViHanhChinhLienKeTrai", "TEXT", None, None, None,"donViHanhChinhLienKeTrai", "NULLABLE")
            arcpy.AddField_management(intersect_Huyen_Path, "donViHanhChinhLienKePhai", "TEXT", None, None, None,"donViHanhChinhLienKePhai", "NULLABLE")
            arcpy.AddField_management(intersect_Huyen_Path, "chieuDai", "DOUBLE", None, None, None,"chieuDai", "NULLABLE")
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(DiaPhan_Huyen_Path)
            for field in fieldMappings.fields:
                if field.name not in ["doiTuong", "danhTuChung", "diaDanh"]:
                    fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
            arcpy.SpatialJoin_analysis(target_features = intersect_Huyen_Path, join_features = DiaPhan_Huyen_Path, out_feature_class = joint_Huyen_Path, 
                                    join_operation = "JOIN_ONE_TO_MANY", join_type = "KEEP_ALL", field_mapping = fieldMappings, match_option = "WITHIN")
            with arcpy.da.UpdateCursor(intersect_Huyen_Path, ["OID@" ,"FID_DiaPhan_Huyen", "loaiHienTrangPhapLy", "donViHanhChinhLienKeTrai", "donViHanhChinhLienKePhai", "chieuDai", "Shape_Length", "doiTuong"]) as uCur:
                for uRow in uCur:
                    with arcpy.da.SearchCursor(joint_Huyen_Path, ["TARGET_FID", "JOIN_FID", "doiTuong", "danhTuChung", "diaDanh"]) as sCur:
                        for sRow in sCur:
                            if uRow[0] == sRow[0] and sRow[2] == 2:
                                if uRow[1] == sRow[1]:
                                    uRow[2] = 1
                                    uRow[5] = uRow[6]
                                    uRow[3] = sRow[3] + " " + sRow[4]
                                    uRow[7] = sRow[2]
                                    uCur.updateRow(uRow)
                                else:
                                    uRow[2] = 1
                                    uRow[5] = uRow[6]
                                    uRow[4] = sRow[3] + " " + sRow[4]
                                    uRow[7] = sRow[2]
                                    uCur.updateRow(uRow)
            #Tinh
            arcpy.SelectLayerByAttribute_management(DiaPhan_Lyr, "NEW_SELECTION", "doiTuong = 1")
            arcpy.CopyFeatures_management(DiaPhan_Lyr, DiaPhan_Tinh_Path)
            arcpy.Intersect_analysis([[DiaPhan_Tinh_Path,1]], intersect_Tinh_Path, "ALL", None, "LINE")
            arcpy.DeleteIdentical_management(intersect_Tinh_Path, ["Shape"], None, None)
            arcpy.AddField_management(intersect_Tinh_Path, "loaiHienTrangPhapLy", "SHORT", None, None, None,"loaiHienTrangPhapLy", "NULLABLE")
            arcpy.AddField_management(intersect_Tinh_Path, "donViHanhChinhLienKeTrai", "TEXT", None, None, None,"donViHanhChinhLienKeTrai", "NULLABLE")
            arcpy.AddField_management(intersect_Tinh_Path, "donViHanhChinhLienKePhai", "TEXT", None, None, None,"donViHanhChinhLienKePhai", "NULLABLE")
            arcpy.AddField_management(intersect_Tinh_Path, "chieuDai", "DOUBLE", None, None, None,"chieuDai", "NULLABLE")
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(DiaPhan_Tinh_Path)
            for field in fieldMappings.fields:
                if field.name not in ["doiTuong", "danhTuChung", "diaDanh"]:
                    fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
            arcpy.SpatialJoin_analysis(target_features = intersect_Tinh_Path, join_features = DiaPhan_Tinh_Path, out_feature_class = joint_Tinh_Path, 
                                    join_operation = "JOIN_ONE_TO_MANY", join_type = "KEEP_ALL", field_mapping = fieldMappings, match_option = "WITHIN")
            with arcpy.da.UpdateCursor(intersect_Tinh_Path, ["OID@" ,"FID_DiaPhan_Tinh", "loaiHienTrangPhapLy", "donViHanhChinhLienKeTrai", "donViHanhChinhLienKePhai", "chieuDai", "Shape_Length", "doiTuong"]) as uCur:
                for uRow in uCur:
                    with arcpy.da.SearchCursor(joint_Tinh_Path, ["TARGET_FID", "JOIN_FID", "doiTuong", "danhTuChung", "diaDanh"]) as sCur:
                        for sRow in sCur:
                            if uRow[0] == sRow[0] and sRow[2] == 1:
                                if uRow[1] == sRow[1]:
                                    uRow[2] = 1
                                    uRow[5] = uRow[6]
                                    uRow[3] = sRow[3] + " " + sRow[4]
                                    uRow[7] = sRow[2]
                                    uCur.updateRow(uRow)
                                else:
                                    uRow[2] = 1
                                    uRow[5] = uRow[6]
                                    uRow[4] = sRow[3] + " " + sRow[4]
                                    uRow[7] = sRow[2]
                                    uCur.updateRow(uRow)
            #Xoa Xa bi trung
            arcpy.MakeFeatureLayer_management(intersect_Xa_Path, "DuongDiaGioi_Xa_Lyr") 
            arcpy.MakeFeatureLayer_management(intersect_Huyen_Path, "DuongDiaGioi_Huyen_Lyr")
            arcpy.SelectLayerByLocation_management(in_layer = "DuongDiaGioi_Xa_Lyr", overlap_type = "WITHIN", select_features = "DuongDiaGioi_Huyen_Lyr",
                                                    selection_type = "NEW_SELECTION")
            if int(arcpy.GetCount_management("DuongDiaGioi_Xa_Lyr").getOutput(0)) > 0:
                    arcpy.DeleteFeatures_management("DuongDiaGioi_Xa_Lyr")

            #Xoa Huyen bi trung
            arcpy.MakeFeatureLayer_management(intersect_Tinh_Path, "DuongDiaGioi_Tinh_Lyr") 
            arcpy.SelectLayerByLocation_management(in_layer = "DuongDiaGioi_Huyen_Lyr", overlap_type = "WITHIN", select_features = "DuongDiaGioi_Tinh_Lyr",
                                                    selection_type = "NEW_SELECTION")
            if int(arcpy.GetCount_management("DuongDiaGioi_Huyen_Lyr").getOutput(0)) > 0:
                    arcpy.DeleteFeatures_management("DuongDiaGioi_Huyen_Lyr")

            #Copy dữ liệu vào lớp DuongDiaGioi
            if int(arcpy.GetCount_management(DuongDiaGioi_Path).getOutput(0)) > 0:
                arcpy.DeleteFeatures_management(DuongDiaGioi_Path)
            duongDiaGioiFields = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiHienTrangPhapLy", "donViHanhChinhLienKeTrai", 
                                "donViHanhChinhLienKePhai", "chieuDai", "doiTuong", "maTrinhBay", "tenManh", "soPhienHieuManhBanDo"]
            duongDiaGioiFields2 = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiHienTrangPhapLy", "donViHanhChinhLienKeTrai", 
                                "donViHanhChinhLienKePhai", "chieuDai", "doiTuong", "maTrinhBay", "tenManh", "soPhienHieuManhBanDo", "DuongDiaGioi_Rep_ID", "RuleID"]
            with arcpy.da.SearchCursor(intersect_Xa_Path, duongDiaGioiFields) as sCur:
                with arcpy.da.InsertCursor(DuongDiaGioi_Path, duongDiaGioiFields2) as iCur:
                    for sRow in sCur:
                        iCur.insertRow([sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], 1, sRow[6], sRow[7], sRow[8], sRow[9], sRow[10], sRow[11], sRow[12], 5, 1])
            with arcpy.da.SearchCursor(intersect_Huyen_Path, duongDiaGioiFields) as sCur:
                with arcpy.da.InsertCursor(DuongDiaGioi_Path, duongDiaGioiFields2) as iCur:
                    for sRow in sCur:
                        iCur.insertRow([sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], 1, sRow[6], sRow[7], sRow[8], sRow[9], sRow[10], sRow[11], sRow[12], 3, 3])
            with arcpy.da.SearchCursor(intersect_Tinh_Path, duongDiaGioiFields) as sCur:
                with arcpy.da.InsertCursor(DuongDiaGioi_Path, duongDiaGioiFields2) as iCur:
                    for sRow in sCur:
                        iCur.insertRow([sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], 1, sRow[6], sRow[7], sRow[8], sRow[9], sRow[10], sRow[11], sRow[12], 1, 2])
            #arcpy.CalculateField_management(DuongDiaGioi_Path, "DuongDiaGioi_Rep_ID", 1, "PYTHON_9.3")
            arcpy.CopyFeatures_management(DuongDiaGioi_Path, DuongDiaGioi_Dich_Path)
            arcpy.AddMessage("\n# Hoan thanh!!!")
        except OSError as error:
            arcpy.AddMessage("Error" + error.message)
        except ValueError as error:
            arcpy.AddMessage("Error" + error.message)
        except arcpy.ExecuteError as error:
            arcpy.AddMessage("Error" + error.message)
        finally:
            arcpy.Delete_management("in_memory")
if __name__=='__main__':
    obj = FPT_DuongDiaGioi()
    obj.CreateDuongDiaGioi()