import arcpy
import os
import json
import sys
import inspect

arcpy.env.overwriteOutput = 1
SEG_KhungLuoi = "C:/Generalize_25_50/khung2_2.gdb/KhungLuoi/SEG_KhungLuoi"
ANO_KhungLuoi = "C:/Generalize_25_50/khung2_2.gdb/KhungLuoi/ANO_KhungLuoi_50000"
#ANO_KhungLuoi = "C:/Generalize_25_50/khung2_2.gdb/KhungLuoi/PNT_KhungLuoi"
list1 = []
list2 = []
list3 = []
check_thanh_nganh = False
check_thanh_doc = False
x_trung_binh = 0
y_trung_binh = 0
with arcpy.da.SearchCursor(SEG_KhungLuoi, ["OID@", "GlobalID", "SHAPE@"]) as sCur:
    for sRow in sCur:
        if str(sRow[1]) == "{216B299E-1AC6-4B4A-A31F-AE7F5D82B6EF}":
            list2 = []
            polyline = sRow[2]
            for feature in polyline:
                for point in feature:
                    x = point.X
                    y = point.Y
                    point_utm = arcpy.PointGeometry(arcpy.Point(point.X,point.Y),arcpy.SpatialReference(3405))   
                    pointA = point_utm.projectAs(arcpy.SpatialReference(4326))  
                    list1 = [x, y, round(pointA.centroid.X,4), round(pointA.centroid.Y,4)]
                    list2.append(list1)
            count = len(list2)
            if list2[0][3] == list2[count-1][3] and check_thanh_nganh == False: #thanh ngang
                #list3.append("NS",list2[0][0],list2[0][1],list2[0][2],list2[0][3])
                #list3.append("NS",list2[count-1][0],list2[count-1][1],list2[count-1][2],list2[count-1][3])
                check_thanh_nganh = True
                x_trung_binh = (list2[0][0] + list2[count-1][0]) / 2
                
            elif list2[0][2] == list2[count-1][2] and check_thanh_doc == False: #thanh doc
                #list3.append("EW",list2[0][0],list2[0][1],list2[0][2],list2[0][3])
                #list3.append("EW",list2[count-1][0],list2[count-1][1],list2[count-1][2],list2[count-1][3])
                check_thanh_doc = True
                y_trung_binh = (list2[0][1] + list2[count-1][1]) / 2
del sCur
x_giua = int(x_trung_binh/1000)
x_giua = x_giua * 1000 + 500
edit = arcpy.da.Editor("C:/Generalize_25_50/khung2_2.gdb")
edit.startEditing(False,False)
edit.startOperation()
'''
with arcpy.da.UpdateCursor(ANO_KhungLuoi, ["OID@" ,"SHAPE@XY", "GlobalID", "XOffset", "YOffset"]) as uCur:
    for uRow in uCur:
        if str(uRow[2]) == "{A75929C7-4EF0-4F7A-946A-82DCB34C844E}":
        #if str(uRow[2]) == "{91D9CBD7-F96A-4D8E-A0CC-0B7DA76F99BA}":
            print x_giua
            print uRow[1][0]
            #uRow[3] = 500
            #uRow[4] = 0
            uRow[1] = [x_giua,uRow[1][1]]
            uCur.updateRow(uRow)
'''
with arcpy.da.UpdateCursor(ANO_KhungLuoi, ['SHAPE@XY']) as cursor:
        for row in cursor:
            cursor.updateRow([[row[0][0] + 500, row[0][1] + 500]])
edit.stopOperation()
edit.stopEditing(True)
#print list3
                