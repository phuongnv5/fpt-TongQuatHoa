import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\Generalize_25_50\\50K_Process.gdb\\ThuyHe"

fcBaiBoiA = "BaiBoiA"
fcSongSuoiA = "SongSuoiA"

try:
    arcpy.CopyFeatures_management(fcBaiBoiA, fcBaiBoiA + "_Copy")
    arcpy.CopyFeatures_management(fcSongSuoiA, fcSongSuoiA + "_Copy")
    arcpy.Intersect_analysis ([fcBaiBoiA + "_Copy", fcSongSuoiA + "_Copy"], "in_memory\\fcBaiBoiA_Intersect_fcSongSuoiA", "ONLY_FID", "#", "LINE")
    arcpy.Densify_edit("in_memory\\fcBaiBoiA_Intersect_fcSongSuoiA", "DISTANCE", "1 Meters")
    arcpy.FeatureVerticesToPoints_management ("in_memory\\fcBaiBoiA_Intersect_fcSongSuoiA", "in_memory\\fcBaiBoiA_Intersect_fcSongSuoiA_Point", "#")
    arcpy.Integrate_management ([[fcBaiBoiA + "_Copy", 1], ["in_memory\\fcBaiBoiA_Intersect_fcSongSuoiA_Point", 2]], "#")
    arcpy.Integrate_management ([[fcSongSuoiA + "_Copy", 1], ["in_memory\\fcBaiBoiA_Intersect_fcSongSuoiA_Point", 2]], "#")
    arcpy.SimplifyPolygon_cartography(fcBaiBoiA + "_Copy",
                                    fcBaiBoiA + "_Copy_Simplify",
                                    algorithm = "BEND_SIMPLIFY",
                                    tolerance = "50 Meters",
                                    collapsed_point_option = "NO_KEEP")
    arcpy.SimplifyPolygon_cartography(fcSongSuoiA + "_Copy",
                                    fcSongSuoiA + "_Copy_Simplify",
                                    algorithm = "BEND_SIMPLIFY",
                                    tolerance = "50 Meters",
                                    collapsed_point_option = "NO_KEEP")
except:
    arcpy.AddError(arcpy.GetMessages())
finally:
    arcpy.Delete_management("in_memory")