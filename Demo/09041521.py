import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\Generalize_25_50\\50K_Process.gdb\\ThuyHe"

fcBaiBoiA = "BaiBoiA"
fcSongSuoiA = "SongSuoiA"
fcBaiBoiASongSuoiAPartitions = "BaiBoiASongSuoiAPartitions"

try:
    #arcpy.CopyFeatures_management(fcBaiBoiA, fcBaiBoiA + "_Copy")
    #arcpy.CopyFeatures_management(fcSongSuoiA, fcSongSuoiA + "_Copy")
    arcpy.CreateCartographicPartitions_cartography([fcBaiBoiA, fcSongSuoiA], fcBaiBoiASongSuoiAPartitions, "50000")
    arcpy.AddMessage("\n# Done!!!")
except:
    arcpy.AddMessage(arcpy.GetMessages())