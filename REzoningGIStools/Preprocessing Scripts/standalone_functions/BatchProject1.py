# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.
# VECTORS

import arcpy
import os
import argparse
import pandas as pd
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")


#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-o", "--output", required=True, nargs='+', help="output directory", type=str)
ap.add_argument("-fp", "--file_path", required=True, nargs='+', help="csv_file of 6 columns: \n"
                "1 : in_features(feature class or raster), \n"
                "2 : name of output file or raster, \n"
                "3 : feature_class if feature class and raster if raster \n"
                "4 : input coordinate system for arcpy.SpatialReference \n"
                "5 : output coordinate system for arcpy.SpatialReference \n"
                "6 : If raster, resampling method (Nearest/Bilinear/Cubic/Majority", type=str)
ap.add_argument("-cs", "--cell_size", required=False, nargs='+',
                help="cell size in the form 'X Y' such as 500 500 ",
                type=str)
ap.add_argument("-tr", "--template_raster", required=False, nargs='+',
                help="if you want to choose a template raster to snap all rasters, provide file path here \n"
                "If you do not have one in mind, the first raster processed will be used as the template for all others",
                type=str)

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

if args["template_raster"] is not None:
    arcpy.env.snapRaster = args["template_raster"][0]
    print("Now snapping to provided template raster")

if args["cell_size"] is None:
    cellSize = "500 500"
else:
    cellSize = args["cell_size"][0]


#####parsing the csv_file
arcpy.env.workspace = workspace_in
print(arcpy.ListFeatureClasses())
for i in range(len(csv_file)):
    infile = csv_file[0][i]
    print(infile)
    outfile = csv_file[1][i]
    print(outfile)
    outfc = os.path.join(args["output"][0], outfile + "_Projected")

    if arcpy.Exists(outfc):
        print("An output file with this name already exists; skipping this row")
        if (i == 0):
            if args["template_raster"] is None:
                arcpy.env.snapRaster = outfc
                print("Now snapping to first raster")
        continue
    # if (infile == "gm_lc_v3_2_2"):
    #     continue

    if(csv_file[2][i] == 'Feature Class'):

        print("Feature Class")
        print(infile, outfc, arcpy.SpatialReference(csv_file[4][i]), arcpy.SpatialReference(csv_file[3][i]))
        arcpy.Project_management(infile, outfc, arcpy.SpatialReference(csv_file[4][i]),
                                 in_coor_system = arcpy.SpatialReference(csv_file[3][i]))
        print(arcpy.GetMessages())

    elif(csv_file[2][i] == 'Raster'):
        print("Raster")

        # # Floating point rasters cannot be projected
        # if (arcpy.GetRasterProperties_management(infile, "VALUETYPE").getOutput(0) == "9"):
        #     print("This is a floating point raster, which cannot be projected as is")
        #     outInt = Int(infile)
        #     arcpy.env.overwriteOutput = True
        #     outInt.save(infile)
        #     arcpy.env.overwriteOutput = False
        #     print("Had to change floating point raster to int pixel type")

        # Rasters must have a value attribute table. If one exists, function will not make a new one
        #arcpy.BuildRasterAttributeTable_management(infile,overwrite=None)

        arcpy.ProjectRaster_management(infile, outfc, arcpy.SpatialReference(csv_file[4][i]),
                                       in_coor_system = arcpy.SpatialReference(csv_file[3][i]),
                                       resampling_type = csv_file[5][i], cell_size=cellSize)
        print(arcpy.GetMessages())
        if (i == 0):
            if args["template_raster"] is None:
                arcpy.env.snapRaster = outfc
                print("Now snapping to first raster")





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
