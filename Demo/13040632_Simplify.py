import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\Users\\vuong\\Documents\\ArcGIS\\Default.gdb"

fcPointRemove = "PointRemove"
fcLineRemove = "LineRemove"

try:
    fcPointRemoveLayer = "in_memory\\fcPointRemoveLayer"
    fcLineRemoveLayer = "in_memory\\fcLineRemoveLayer"
    arcpy.MakeFeatureLayer_management(fcPointRemove, fcPointRemoveLayer)
    arcpy.MakeFeatureLayer_management(fcLineRemove, fcLineRemoveLayer)
    with arcpy.da.SearchCursor(fcPointRemoveLayer, ["OID@", "SHAPE@"]) as cursor:
        for row in cursor:
            
            
    print ("\n# Done!!!")
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())
