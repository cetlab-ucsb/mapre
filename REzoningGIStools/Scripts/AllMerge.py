import arcpy
import os

arcpy.env.workspace = r"C:\Users\anagha.uppal\Documents\ArcGIS\Projects\mapre\mapre.gdb\InputShapeFiles"
path = r"C:\Users\anagha.uppal\Documents\ArcGIS\Projects\mapre\mapre.gdb\InputShapeFiles"

outcs = arcpy.SpatialReference(4326)

for root, dirs, files in os.walk(path):
    workspaces = arcpy.ListWorkspaces("*")
    for ws in workspaces:
        print(ws)
        arcpy.env.workspace = ws
        featureclasses = arcpy.ListFeatureClasses()
        #print(featureclasses)
        for fc in featureclasses:
            print(fc)
            outfc = arcpy.Describe(fc).baseName + "_Projected" + ".shp"
            print(outfc)
            arcpy.Project_management(fc, outfc, outcs)
        #print(os.path.join(root, ws))

##################################################################
for root, dirs, files in os.walk(path):
    workspaces = arcpy.ListWorkspaces("*")
    for ws in workspaces:
        arcpy.env.workspace = ws
        featureclasses = arcpy.ListFeatureClasses("*_Projected")
        print(featureclasses)
        for fc in featureclasses:
            print(fc)
