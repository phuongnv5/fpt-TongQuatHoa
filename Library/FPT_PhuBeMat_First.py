# -*- coding: utf-8 -*-
import arcpy
import os
import json
import sys
import inspect

class FPT_PhuBeMat_First:
    def __init__(self):
        abc = 1
    def ProcessGioiPhuBeMat(self):
        try:
            arcpy.env.overwriteOutput = 1
            duongDanNguon = "C:/Generalize_25_50/50K_Process.gdb"
            duongDanDich = "C:/Generalize_25_50/50K_Final.gdb"
            arcpy.env.workspace = duongDanNguon + "/PhuBeMat"
            arcpy.Integrate_management([[duongDanNguon + "/PhuBeMat/PhuBeMat", 1]], "3 Meters")
            arcpy.CopyFeatures_management(duongDanNguon + "/PhuBeMat/PhuBeMat", duongDanDich + "/PhuBeMat/PhuBeMat")
        except OSError as error:
            arcpy.AddMessage("Error" + error.message)
        except ValueError as error:
            arcpy.AddMessage("Error" + error.message)
        except arcpy.ExecuteError as error:
            arcpy.AddMessage("Error" + error.message)
        finally:
            arcpy.Delete_management("in_memory")
if __name__=='__main__':
    arcpy.AddMessage("#Xu ly PhuBeMat")
    obj = FPT_PhuBeMat_First()
    obj.ProcessGioiPhuBeMat()
    arcpy.AddMessage("#Hoan thanh !!!")