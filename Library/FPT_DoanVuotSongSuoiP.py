# -*- coding: utf-8 -*-
import arcpy
import os
import json
import sys
import inspect

class FPT_DoanVuotSongSuoiP:
    def __init__(self):
        abc = 1
    def Snap(self):
        try:
            arcpy.env.overwriteOutput = 1
            arcpy.AddMessage("\n# Xu ly DoanVuotSongSuoiP")
            _path_Layer_DoanVuotSongSuoiP = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanVuotSongSuoiP"
            _path_Layer_DoanVuotSongSuoiP_Final = "C:/Generalize_25_50/50K_Final.gdb/GiaoThong/DoanVuotSongSuoiP"
            _path_Layer_DoanVuotSongSuoiP_Snap = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanVuotSongSuoiP_Snap"
            _path_Layer_DoanTimDuongBo = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo"
            _path_Layer_SongSuoiL = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe/SongSuoiL"
            arcpy.Intersect_analysis([_path_Layer_DoanTimDuongBo, _path_Layer_SongSuoiL], _path_Layer_DoanVuotSongSuoiP_Snap, "", "", "point")
            arcpy.Snap_edit(_path_Layer_DoanVuotSongSuoiP, [[_path_Layer_DoanVuotSongSuoiP_Snap, "EDGE", "25 Meters"]])
            arcpy.CopyFeatures_management(_path_Layer_DoanVuotSongSuoiP, _path_Layer_DoanVuotSongSuoiP_Final)
        except OSError as error:
            arcpy.AddMessage("Error" + error.message)
        except ValueError as error:
            arcpy.AddMessage("Error" + error.message)
        except arcpy.ExecuteError as error:
            arcpy.AddMessage("Error" + error.message)
        finally:
            arcpy.Delete_management("in_memory")
if __name__=='__main__':
    obj = FPT_DoanVuotSongSuoiP()
    obj.Snap()
    arcpy.AddMessage("\n# Hoan thanh!!!")