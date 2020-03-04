# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.
# VECTORS

import arcpy
import os
import pandas as pd
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

# Set workspace environment
#workspace_in = "r" + "\"" + args["input"][0] + "\""
workspace_in = r"R:\users\anagha.uppal\MapRE\inputs2020.gdb"
print(workspace_in)

##
### Input feature classes
##input_features = ["africagrid_Transmission_Distribution",
##                  "ALL_AICD_Countries_Power_Plants",
##                      "country_boundaries", "protected_areas_points",
##                  "rails", "water_bodies"]

### Output workspace
##
workspace_out = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"
##out_workspace = workspace_out

### Output coordinate system - leave it empty
out_cs = arcpy.SpatialReference('Africa Albers Equal Area Conic')
in_cs = arcpy.SpatialReference(4326)

# Template dataset - it has GCS_WGS_1984 coordinate system
template = ""

# Geographic transformation -
transformation = ""

cellSize = "500 500"


#####parsing the csv_file
arcpy.env.workspace = workspace_in
print(arcpy.ListFeatureClasses())
for fc in arcpy.ListFeatureClasses():
    outfc = os.path.join(workspace_out, arcpy.Describe(fc).baseName + "_Projected")
    print("Feature Class")
    arcpy.Project_management(fc, outfc, out_cs, in_coor_system = in_cs)
    print(arcpy.GetMessages())

resample = ["CUBIC", "NEAREST", "CUBIC", "CUBIC", "NEAREST", "NEAREST", "BILINEAR", "CUBIC", "CUBIC", "CUBIC"]

for rs in arcpy.ListRasters():
    for i in range(len(arcpy.ListRasters())):
        print("Raster")
        outrs = os.path.join(workspace_out, arcpy.Describe(rs).baseName + "_Projected")
        print(rs, outrs, out_cs)

        # Floating point rasters cannot be projected
        if (arcpy.GetRasterProperties_management(rs, "VALUETYPE").getOutput(0) == "9"):
            print("This is a floating point raster, which cannot be projected as is")
            outInt = Int(rs)
            arcpy.env.overwriteOutput = True
            outInt.save(rs)
            arcpy.env.overwriteOutput = False
            print("Had to change floating point raster to int pixel type")

        # Rasters must have a value attribute table. If one exists, function will not make a new one
        arcpy.BuildRasterAttributeTable_management(rs, overwrite=None)

        arcpy.ProjectRaster_management(in_raster=rs, out_raster=outrs, out_coor_system=out_cs,
                                       in_coor_system = in_cs,
                                       resampling_type = resample[i], cell_size=cellSize) ## what is the resampling type
        print(arcpy.GetMessages())
        arcpy.env.snapRaster = outrs




##arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\inputs2020.gdb"
##for fc in arcpy.ListFeatureClasses():
##    fc = "rails"
##    print(fc)
##    outfc = os.path.join(r"R:\users\anagha.uppal\MapRE\outputs2020.gdb", fc + "_Projected")
##    # Set output coordinate system
##    outCS = arcpy.SpatialReference('Africa Albers Equal Area Conic')
##    inCS = arcpy.SpatialReference(4326)
##    print(fc, outfc, outCS, inCS)
##    # run project tool
##    arcpy.Project_management(fc, outfc, outCS, in_coor_system = inCS)
##
##    # check messages
##    print(arcpy.GetMessages())


##
##for fc in csv_file:
##    outfc = os.path.join(out_workspace, fc + "_Projected")
##    print(outfc)
##    arcpy.Project_management(fc, outfc, out_cs, in_coor_system = arcpy.SpatialReference(4326))
##    print(arcpy.GetMessages())

##for rs in arcpy.ListRasters():
##    outrs = os.path.join(out_workspace, rs + "_Projected.tif")
##    print(outrs)
##    arcpy.ProjectRaster_management(in_raster = rs, out_raster = outrs,
##                                   out_coor_system = out_cs, in_coor_system = arcpy.SpatialReference(4326))
##    print(arcpy.GetMessages())

##try:
##    print("tries")
##    res = arcpy.BatchProject(input_features, out_workspace, out_cs, template, transformation)
##    print("succeeds")
##    if res.maxSeverity == 0:
##        print("projection of all datasets successful")
##    else:
##        print("failed to project one or more datasets")
##except:
##    print(res.getMessages())
