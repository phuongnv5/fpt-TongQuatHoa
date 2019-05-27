# Xoay Representation CongThuyLoiP, CauGiaoThongP theo DoanTimDuongBo

import arcpy

class XoayCongThuyLoiPCauGiaoThongP:

    def __init__(self):
        pass

    def Excute(self):
        arcpy.env.workspace = "C:\\Generalize_25_50\\50K_Process.gdb"
        arcpy.env.overwriteOutput = True
        arcpy.env.referenceScale = "50000"
        fcCongThuyLoiP = "CongThuyLoiP"
        fcCauGiaoThongP = "CauGiaoThongP"
        fcDoanTimDuongBo = "DoanTimDuongBo"
        congThuyLoiPLayer = "CongThuyLoiPLayer"
        cauGiaoThongPLayer = "CauGiaoThongPLayer"
        doanTimDuongBoLayer = "DoanTimDuongBoLayer"
        arcpy.MakeFeatureLayer_management(in_features = fcCongThuyLoiP,
                                            out_layer = congThuyLoiPLayer)
        arcpy.MakeFeatureLayer_management(in_features = fcCauGiaoThongP,
                                            out_layer = cauGiaoThongPLayer)
        arcpy.MakeFeatureLayer_management(in_features = fcDoanTimDuongBo,
                                            out_layer = doanTimDuongBoLayer)
        arcpy.SetLayerRepresentation_cartography(in_layer = congThuyLoiPLayer,
                                                 representation = "CongThuyLoiP_Rep")
        arcpy.SetLayerRepresentation_cartography(in_layer = cauGiaoThongPLayer,
                                                 representation = "CauGiaoThongP_Rep")
        arcpy.SetLayerRepresentation_cartography(in_layer = doanTimDuongBoLayer,
                                                 representation = "DoanTimDuongBo_Rep")
        #PERPENDICULAR: aligns representation markers perpendicularly to the stroke or fill edge. This is the default.
        #PARALLEL: aligns representation markers parallel to the stroke or fill edge.
        arcpy.AlignMarkerToStrokeOrFill_cartography(in_point_features = congThuyLoiPLayer,
                                                    in_line_or_polygon_features = doanTimDuongBoLayer,
                                                    search_distance = "0 Meters",
                                                    marker_orientation = "PERPENDICULAR")
        arcpy.AlignMarkerToStrokeOrFill_cartography(in_point_features = cauGiaoThongPLayer,
                                                    in_line_or_polygon_features = doanTimDuongBoLayer,
                                                    search_distance = "0 Meters",
                                                    marker_orientation = "PERPENDICULAR")

if __name__ == '__main__':
    xoayCongThuyLoiPCauGiaoThongP = XoayCongThuyLoiPCauGiaoThongP()
    xoayCongThuyLoiPCauGiaoThongP.Excute()
