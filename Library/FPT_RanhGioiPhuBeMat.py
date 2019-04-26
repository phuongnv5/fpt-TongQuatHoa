# -*- coding: utf-8 -*-
import arcpy
import os
import json
import sys
import inspect

class FPT_RanhGioiPhuBeMat:
    def __init__(self):
        abc = 1
    def CreateRanhGioiPhuBeMat(self):
        try:
            arcpy.env.overwriteOutput = 1
            duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb"
            duongDanDich = "C:/Generalize_25_50/50K_Final.gdb"
            arcpy.env.workspace = duongDanNguon + "/PhuBeMat"

            PhuBeMat_Name = "PhuBeMat"

            PhuBeMat_Path = duongDanNguon + "/PhuBeMat/" + PhuBeMat_Name
            
            intersect_Path = duongDanNguon + "/PhuBeMat/RanhGioiPhuBeMat_Intersect"
            RanhGioiPhuBeMat_Name = "RanhGioiPhuBeMat"
            RanhGioiPhuBeMat_Path = duongDanNguon + "/PhuBeMat/" + RanhGioiPhuBeMat_Name
            RanhGioiPhuBeMat_Dich_Path = duongDanDich + "/PhuBeMat/" + RanhGioiPhuBeMat_Name
            arcpy.Integrate_management([[PhuBeMat_Path, 1]], "1 Meters")

            
            arcpy.Intersect_analysis([[PhuBeMat_Path,1]], intersect_Path, "ALL", None, "LINE")
            arcpy.DeleteIdentical_management(intersect_Path, ["Shape"], None, None)
            arcpy.AddField_management(intersect_Path, "loaiRanhGioiPhuBeMat", "SHORT", None, None, None,"loaiRanhGioiPhuBeMat", "NULLABLE")
            
            #Copy dữ liệu vào lớp RanhGioiPhuBeMat
            if int(arcpy.GetCount_management(RanhGioiPhuBeMat_Path).getOutput(0)) > 0:
                arcpy.DeleteFeatures_management(RanhGioiPhuBeMat_Path)
            ranhGioiPhuBeMatFields = ["SHAPE@", "maNhanDang", "ngayThuNhan", "ngayCapNhat", "maDoiTuong", "loaiRanhGioiPhuBeMat", "nguonDuLieu", 
                                "maTrinhBay", "tenManh", "soPhienHieuManhBanDo"]
            with arcpy.da.SearchCursor(intersect_Path, ranhGioiPhuBeMatFields) as sCur:
                with arcpy.da.InsertCursor(RanhGioiPhuBeMat_Path, ranhGioiPhuBeMatFields) as iCur:
                    for sRow in sCur:
                        iCur.insertRow([sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], 1, sRow[6], sRow[7], sRow[8], sRow[9]])
            arcpy.CopyFeatures_management(RanhGioiPhuBeMat_Path, RanhGioiPhuBeMat_Dich_Path)
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
    abc = 1