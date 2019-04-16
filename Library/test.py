import arcpy
import os
import json

arcpy.env.overwriteOutput = 1
arcpy.env.workspace = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe"
_MatNuocTinh = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe/MatNuocTinh"
_MatNuocTinh_Copy = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe/MatNuocTinh_Copy"
_MatNuocTinh_Line = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe/MatNuocTinh_Line"
_DoanTimDuongBo = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo"
_DoanTimDuongBo_Copy = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Copy"
_DoanTimDuongBo_Copy2 = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Copy2"
_Line_Buffer = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe/Line_Buffer"
_Polygon_Merge = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe/Polygon_Merge"
_Polygon_Simplify = "C:/Generalize_25_50/50K_Process.gdb/ThuyHe/Polygon_Simplify"

arcpy.CopyFeatures_management(_MatNuocTinh, _MatNuocTinh_Copy)
arcpy.CopyFeatures_management(_DoanTimDuongBo, _DoanTimDuongBo_Copy)
arcpy.CopyFeatures_management(_DoanTimDuongBo, _DoanTimDuongBo_Copy2)
arcpy.Densify_edit(_DoanTimDuongBo_Copy, "OFFSET",None, "0.1 Meters",None)
#arcpy.FeatureToLine_management([_MatNuocTinh_Copy], _MatNuocTinh_Line, None, None)
#arcpy.Append_management([_DoanTimDuongBo_Copy], _MatNuocTinh_Line, "NO_TEST",None,None)
arcpy.Buffer_analysis(_DoanTimDuongBo_Copy, _Line_Buffer, "0.01 Meters")
arcpy.Merge_management([_MatNuocTinh_Copy, _Line_Buffer], _Polygon_Merge)
arcpy.SimplifyPolygon_cartography(in_features = _Polygon_Merge,
                                                out_feature_class = _Polygon_Simplify,
                                                algorithm = "BEND_SIMPLIFY",
                                                tolerance = "50 Meters",
                                                error_option = "NO_CHECK",
                                                collapsed_point_option = "NO_KEEP")

arcpy.Snap_edit(_DoanTimDuongBo_Copy, [[_Polygon_Simplify, "EDGE", "5 Meters"]])
arcpy.AddMessage("\n# Done...")