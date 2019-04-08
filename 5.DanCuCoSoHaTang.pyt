import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [NhaP]


class NhaP(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2.Dich nha"
        self.description = "Dich Nha khong trung len Duong"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.env.overwriteOutput = 1
        _path_Layer_NhaP = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang/NhaP"
        _path_Layer_NhaP_Copy = "C:/Generalize_25_50/50K_Process.gdb/DanCuCoSoHaTang/NhaP_Copy"
        _path_Layer_DoanTimDuongBo = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo"
        _path_Layer_DoanTimDuongBo_Copy = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Copy"
        _path_Layer_DoanTimDuongBo_Buffer = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Buffer"
        _path_Layer_DoanTimDuongBo_Buffer_2 = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Buffer_2"
        _path_TableAgg_DoanTimDuongBo = "C:/Generalize_25_50/50K_Process.gdb/DoanTimDuongBo_Buffer_2_Tbl"
        _path_Layer_DoanTimDuongBo_Buffer_ToLine = "C:/Generalize_25_50/50K_Process.gdb/GiaoThong/DoanTimDuongBo_Buffer_ToLine"
        arcpy.CopyFeatures_management(_path_Layer_NhaP, _path_Layer_NhaP_Copy)
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
        arcpy.MakeFeatureLayer_management(_path_Layer_NhaP_Copy, "NhaP_Copy_lyr")
        arcpy.SelectLayerByLocation_management (in_layer = "NhaP_Copy_lyr", overlap_type = "WITHIN", select_features = _path_Layer_DoanTimDuongBo_Buffer_2)
        arcpy.Snap_edit("NhaP_Copy_lyr", [[_path_Layer_DoanTimDuongBo_Buffer_ToLine, "EDGE", "75 Meters"]])
        return
