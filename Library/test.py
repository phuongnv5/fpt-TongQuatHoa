import arcpy
import os
import json
import sys
import inspect

arcpy.env.overwriteOutput = 1
duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb"
arcpy.AddMessage("\n\t# Snap other: {0}".format("PhuBeMat"))
arcpy.Integrate_management([[duongDanNguon + "/PhuBeMat/PhuBeMat", 1]], "2 Meters")
arcpy.Densify_edit(duongDanNguon + "/PhuBeMat/PhuBeMat", "DISTANCE","2 Meters",None ,None)
arcpy.Snap_edit(duongDanNguon + "/PhuBeMat/PhuBeMat", 
    [[duongDanNguon + "/ThuyHe/SongSuoiL_KenhMuongL_SnapPBM", "EDGE", "35 Meters"]])
arcpy.Integrate_management([[duongDanNguon + "/ThuyHe/SongSuoiL_KenhMuongL_SnapPBM", 1],[duongDanNguon + "/PhuBeMat/PhuBeMat", 2]], "2 Meters")
arcpy.Erase_analysis(in_features = duongDanNguon + "/PhuBeMat/PhuBeMat_LocMatNuoc", 
    erase_features = duongDanNguon + "/PhuBeMat/PhuBeMat", out_feature_class = duongDanNguon + "/PhuBeMat/PhuBeMat_Lo")
arcpy.CalculateField_management(duongDanNguon + "/PhuBeMat/PhuBeMat_Lo", "maNhanDang", '"temp123"', "PYTHON_9.3")
arcpy.Append_management([duongDanNguon + "/PhuBeMat/PhuBeMat_Lo"], duongDanNguon + "/PhuBeMat/PhuBeMat", "NO_TEST",None,None)
arcpy.MultipartToSinglepart_management(duongDanNguon + "/PhuBeMat/PhuBeMat", duongDanNguon + "/PhuBeMat/PhuBeMat2")
arcpy.MakeFeatureLayer_management(duongDanNguon + "/PhuBeMat/PhuBeMat2", "PhuBeMat_Temp_Lyr")
arcpy.SelectLayerByAttribute_management("PhuBeMat_Temp_Lyr", "NEW_SELECTION", "maNhanDang = 'temp123'")
arcpy.Eliminate_management(in_features = "PhuBeMat_Temp_Lyr", out_feature_class = duongDanNguon + "/PhuBeMat/PhuBeMat3", selection = "LENGTH")
arcpy.Densify_edit(duongDanNguon + "/ThuyHe/SongSuoiL", "DISTANCE","2 Meters",None ,None)
arcpy.Snap_edit(duongDanNguon + "/ThuyHe/SongSuoiL", 
    [[duongDanNguon + "/ThuyHe/SongSuoiL_KenhMuongL_SnapPBM", "EDGE", "2 Meters"]])
arcpy.CopyFeatures_management(duongDanNguon + "/PhuBeMat/PhuBeMat3", duongDanNguon + "/PhuBeMat/PhuBeMat")
     