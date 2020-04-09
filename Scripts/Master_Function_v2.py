# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.
# VECTORS

# packages import
import arcpy
import os
import argparse
import pandas as pd
from arcpy.sa import *
import collections


arcpy.CheckOutExtension("Spatial")

###########################################################################

# argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-r", "--region_list", required=True, nargs='*',
                help="the country or region (e.g. states) in quotes and separated by spaces", type=str)
ap.add_argument("-pf", "--process_file", required=False, nargs='+', help="csv_file of 6 columns: \n"
                                                                "1 : in_features(feature class or raster), \n"
                                                                "2 : name of output file or raster, \n"
                                                                "3 : feature_class if feature class and raster if raster \n"
                                                                "4 : input coordinate system for arcpy.SpatialReference \n"
                                                                "5 : output coordinate system for arcpy.SpatialReference \n"
                                                                "6 : If raster, resampling method (Nearest/Bilinear/Cubic/Majority",
                type=str)
ap.add_argument("-cs", "--cell_size", required=False, nargs='+',
                help="cell size in the form 'X Y' such as 500 500 in quotes ",
                type=str)


args = vars(ap.parse_args())
print(args)


###########################################################################
# functions
# for all with yes in csv structure run the passed function
def csv_loop(self, func, colname, once):
    self.func = func
    self.colname = colname
    self.once = once
    for view in csv_file[str(colname)]:
        print(view)
        if view == "Yes":
            self.func
            if self.once:
                break

###########################################################################
# SETUP

if args["process_file"] is None:
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, r"RequiredCSVs\csv_processing_file.csv")
    csv_file = pd.read_csv(path, header=0)
else:
    csv_file = pd.read_csv(args["process_file"][0], header=0)

if args["cell_size"] is None:
    cellSize = "500 500"
else:
    cellSize = args["cell_size"][0]

# Template dataset - it has GCS_WGS_1984 coordinate system
template = ""

# Geographic transformation -
transformation = ""

#####parsing the csv_file
arcpy.env.workspace = workspace_in = args["input"][0]
print(workspace_in)

parentDirectory = os.path.abspath(os.path.join(arcpy.env.workspace, os.pardir))
print(parentDirectory)
if arcpy.Exists(os.path.join(parentDirectory, "projected.gdb")):
    projGDB = workspace_out = os.path.join(parentDirectory, "projected.gdb")
else:
    arcpy.CreateFileGDB_management(parentDirectory, "projected.gdb")
    projGDB = workspace_out = os.path.join(parentDirectory, "projected.gdb")
print(os.path.abspath(workspace_out))


###########################################################################
# RUN SCRIPTS
###########################################################################
### Template raster
import import_functions.BatchProject1

template = csv_file[csv_file['Template Raster'] == "Yes"]
template = template.reset_index()
# print(template.loc[0, 'Input File Name'])
# print(template['Input File Name'][0])

if template['File Type'][0] == 'Raster':
    import_functions.BatchProject1.project(template, workspace_in, workspace_out, cellSize, template=True)
else:
    print("This file is not a raster and cannot serve as your template raster")

###########################################################################

# projectedBool = False
# print(len(set(csv_file['Input Projection'])) <= 2)
# if len(set(csv_file['Input Projection'])) <= 2:
#     if len(set(csv_file['Input Projection'])) == 2:
#         inproj = collections.Counter(csv_file['Input Projection'])
#         inproj = sorted(inproj.items(), key=lambda x: x[1], reverse=True)
#         #print(inproj.keys()[0])
#         print(inproj[0])
#         print(inproj[0][0])
#
#         arcpy.env.overwriteOutput = True
#         for i in range(len(csv_file)):
#             infile = csv_file['Input File Name'][i]
#             if csv_file['Input Projection'][i] != inproj[0][0]:
#                 # project it to inproj[0][0]
#                 if (csv_file['File Type'][i] == 'Feature Class'):
#
#                     print("Feature Class")
#                     print(infile, csv_file['Input Projection'][i], csv_file['Output Projection'][i])
#                     arcpy.Project_management(infile, infile, arcpy.SpatialReference(inproj[0][0]),
#                                              in_coor_system=arcpy.SpatialReference(csv_file['Input Projection'][i]))
#                     print(arcpy.GetMessages())
#
#                 elif (csv_file['File Type'][i] == 'Raster'):
#                     print("Raster")
#                     arcpy.ProjectRaster_management(infile, infile, arcpy.SpatialReference(inproj[0][0]),
#                                                    in_coor_system=arcpy.SpatialReference(csv_file['Input Projection'][0]),
#                                                    cell_size=cellSize)
#                     print(arcpy.GetMessages())
#             else:
#                 print("This file: " + infile + " is already projected to the majority - " + inproj[0][0])
#         projectedBool = False
#         arcpy.env.overwriteOutput = False
#     else:
#         print("All files projected to one")
#         projectedBool = True
#
# else:
#     ### Project all files
import_functions.BatchProject1.project(csv_file, workspace_in, workspace_out, cellSize, template=False)
    #projectedBool = True

###########################################################################

# Name: Country_bounds.py
# Description: Take world boundaries file and divvy it up into indiv countries that we need
import import_functions.Country_bounds_function

bounds = csv_file[csv_file['Country Bound File'] == "Yes"]
bounds = bounds.reset_index()
list_of_countries = args["region_list"]
print(list_of_countries)


workspace_in, workspace_out = import_functions.Country_bounds_function.create_bounds(bounds, workspace_in, workspace_out, list_of_countries)

###########################################################################

# if projectedBool == False:
#     ### Project all files
#     import_functions.BatchProject1.project(csv_file, workspace_in, workspace_out, cellSize, template=False)
#     projectedBool = True

###########################################################################

# Name: All_clip.py
# Description: Clip each file to each country (M x N)
# Feature classes = Clip and Rasters = Extract by Mask

import import_functions.All_clip_function


workspace_files = projGDB
workspace_countries = workspace_out

country_names, workspace_out = import_functions.All_clip_function.all_clip(workspace_files, workspace_countries,
                                                                           list_of_countries)


###########################################################################

# Name: Euclidean_Distance.py
# Description: Turns feature classes or rasters into euclidean distance rasters
# Euclidean Distance calculates, for each cell, the Euclidean distance to the closest source.

import import_functions.Euclidean_Distance_function

print(workspace_countries)

cellSize = int(str.split(cellSize, " ")[0])

ed = csv_file[csv_file['Euclidean Distance Raster'] == "Yes"]
ed = ed.reset_index()

fc_countries = []
walk = arcpy.da.Walk(workspace_countries, datatype="FeatureClass")

for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        if filename in country_names:
            fc_countries.append(os.path.join(dirpath, filename))
            # country_names.append(filename)
fc_countries.sort()

import_functions.Euclidean_Distance_function.euc_dist(ed, country_names, fc_countries[0], cellSize, workspace_out)

###########################################################################

# Name: Extract_Attributes.py
# Description: For LULC, we only need certain categories,
# so we filter that raster
# Each alt energy is different, so we need a file for solar/wind/etc

# lulc = csv_file[csv_file['LULC File'] == "Yes"]
# lulc = lulc.reset_index()
#
# if len(lulc) > 0:
#
#     # Set infile
#     inRaster = "{}_{}_Projected_Clipped".format(country_names[0], lulc['Output File Name'][0])
#
#     print(arcpy.ListRasters())
#
#     if args["threshold"] is not None:
#
#         import import_functions.Extract_Attributes_function
#         thresholds = args["threshold"]
#
#         import_functions.Extract_Attributes_function.extract(thresholds, inRaster, workspace_out)
