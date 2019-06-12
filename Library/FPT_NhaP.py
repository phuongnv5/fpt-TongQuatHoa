# -*- coding: utf-8 -*-
import arcpy
import os
import json
import sys
import inspect

class FPT_NhaP:
    def __init__(self):
        abc = 1
    def Dich_Nha(self):
        try:
            arcpy.env.overwriteOutput = 1
            arcpy.AddMessage("#Xu ly lop NhaP")
            _path_Layer_NhaP = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang/NhaP"
            _path_Layer_NhaP_Final = "C:/Generalize_25_50/50K_Final.gdb/DanCuCoSoHaTang/NhaP"
            _path_Layer_DoanTimDuongBo = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo"
            _path_Layer_DoanTimDuongBo_Copy = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Copy"
            _path_Layer_DoanTimDuongBo_Buffer = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Buffer"
            _path_Layer_DoanTimDuongBo_Buffer_2 = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Buffer_2"
            _path_TableAgg_DoanTimDuongBo = "C:/Generalize_25_50/50K_Process.gdb/DoanTimDuongBo_Buffer_2_Tbl"
            _path_Layer_DoanTimDuongBo_Buffer_ToLine = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Buffer_ToLine"
            arcpy.CopyFeatures_management(_path_Layer_DoanTimDuongBo, _path_Layer_DoanTimDuongBo_Copy)
            arcpy.AddField_management(_path_Layer_DoanTimDuongBo_Copy, "Distance", "TEXT", None, None, None,
                            "Khoang cach buffer", "NULLABLE")
            rows_update = arcpy.UpdateCursor(_path_Layer_DoanTimDuongBo_Copy)
            for row in rows_update:
                if row.getValue("DoanTimDuongBo_Rep_ID") == 1:
                    row.setValue("Distance", "32.5 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 2:
                    row.setValue("Distance", "62.5 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 3:
                    row.setValue("Distance", "57.5 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 4:
                    row.setValue("Distance", "52.5 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 5:
                    row.setValue("Distance", "50 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 6:
                    row.setValue("Distance", "50 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 7:
                    row.setValue("Distance", "36.25 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 8:
                    row.setValue("Distance", "33.75 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 9:
                    row.setValue("Distance", "47.5 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 10:
                    row.setValue("Distance", "50 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 11:
                    row.setValue("Distance", "45 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 12:
                    row.setValue("Distance", "75 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 13:
                    row.setValue("Distance", "43.75 Meters")
                elif row.getValue("DoanTimDuongBo_Rep_ID") == 14:
                    row.setValue("Distance", "43.75 Meters")   
                rows_update.updateRow(row)
            del row
            del rows_update
            arcpy.Buffer_analysis(in_features = _path_Layer_DoanTimDuongBo_Copy, out_feature_class = _path_Layer_DoanTimDuongBo_Buffer, 
                buffer_distance_or_field = "Distance", line_side = "FULL", line_end_type = "ROUND", dissolve_option = "LIST", dissolve_field = "Distance")
            arcpy.AggregatePolygons_cartography(in_features = _path_Layer_DoanTimDuongBo_Buffer, out_feature_class = _path_Layer_DoanTimDuongBo_Buffer_2,
                aggregation_distance = "0.001 Meters", minimum_area =  "0 SquareMeters", minimum_hole_size = "0 SquareMeters", 
                orthogonality_option = "NON_ORTHOGONAL", out_table = _path_TableAgg_DoanTimDuongBo)
            arcpy.FeatureToLine_management([_path_Layer_DoanTimDuongBo_Buffer_2], _path_Layer_DoanTimDuongBo_Buffer_ToLine, None, "ATTRIBUTES")
            #Select by location
            arcpy.env.workspace = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang"
            arcpy.MakeFeatureLayer_management(_path_Layer_NhaP, "NhaP_lyr")
            arcpy.SelectLayerByLocation_management (in_layer = "NhaP_lyr", overlap_type = "WITHIN", select_features = _path_Layer_DoanTimDuongBo_Buffer_2)
            arcpy.Snap_edit("NhaP_lyr", [[_path_Layer_DoanTimDuongBo_Buffer_ToLine, "EDGE", "75 Meters"]])
            arcpy.CopyFeatures_management(_path_Layer_NhaP, _path_Layer_NhaP_Final)
            
            
        except OSError as error:
            arcpy.AddMessage("Error" + error.message)
        except ValueError as error:
            arcpy.AddMessage("Error" + error.message)
        except arcpy.ExecuteError as error:
            arcpy.AddMessage("Error" + error.message)
        finally:
            arcpy.Delete_management("in_memory")
if __name__=='__main__':
    obj = FPT_NhaP()
    obj.Dich_Nha()