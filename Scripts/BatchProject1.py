# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.
# VECTORS

import arcpy
import os
import argparse
import pandas as pd


#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-o", "--output", required=True, nargs='+', help="output directory", type=str)
ap.add_argument("-fp", "--file_path", required=True, nargs='+', help="csv_file of 5 columns: \n"
                "1 : in_features(feature class or raster), \n"
                "2 : feature_class if feature class and raster if raster \n"
                "3 : input coordinate system for arcpy.SpatialReference \n"
                "4 : output coordinate system for arcpy.SpatialReference \n"
                "5 : If raster, resampling method (Nearest/Bilinear/Cubic/Majority", type=str)

args = vars(ap.parse_args())

# Set workspace environment
#workspace_in = "r" + "\"" + args["input"][0] + "\""
workspace_in = args["input"][0]
print(workspace_in)

##
### Input feature classes
##input_features = ["africagrid_Transmission_Distribution",
##                  "ALL_AICD_Countries_Power_Plants",
##                      "country_boundaries", "protected_areas_points",
##                  "rails", "water_bodies"]

### Output workspace
##
##workspace_out = "r" + "\"" + args["output"][0] + "\""
##out_workspace = workspace_out

#csv
csv_file = pd.read_csv(args["file_path"][0], header=None)
#print(csv_file[col][row])

### Output coordinate system - leave it empty
##out_cs = arcpy.SpatialReference('Africa Albers Equal Area Conic')

# Template dataset - it has GCS_WGS_1984 coordinate system
template = ""

# Geographic transformation - 
transformation = ""


#####parsing the csv_file
arcpy.env.workspace = workspace_in
print(arcpy.ListFeatureClasses())
for i in range(len(csv_file)):
    infile = csv_file[0][i]
    if(csv_file[1][i] == 'Feature Class'):
        outfc = os.path.join(args["output"][0], infile + "_Projected")
        print("Feature Class")
        print(infile, outfc, arcpy.SpatialReference(csv_file[3][i]), arcpy.SpatialReference(csv_file[2][i]))
        arcpy.Project_management(infile, outfc, arcpy.SpatialReference(csv_file[3][i]), in_coor_system = arcpy.SpatialReference(csv_file[2][i]))
        print(arcpy.GetMessages())

    elif(csv_file[1][i] == 'Raster'):
        print("Raster")
        outfc = os.path.join(args["output"][0], infile + "_Projected.tif")
        arcpy.ProjectRaster_management(infile, outfc, arcpy.SpatialReference(csv_file[3][i]),
                                       in_coor_system = arcpy.SpatialReference(csv_file[2][i]), resampling_type = csv_file[4][i])
        print(arcpy.GetMessages())




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
