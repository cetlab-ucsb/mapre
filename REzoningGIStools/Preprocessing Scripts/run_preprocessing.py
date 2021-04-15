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
ap.add_argument("-r", "--extract_region", required=True, nargs='*',
                help="the country or region (e.g. states) to extract as condition (in quotes) \n"
                     " e.g. """"NAME" LIKE 'South Africa' OR "NAME" LIKE 'Angola'""", type=str)
ap.add_argument("-n", "--region_name", required=True, nargs='*',
                help="name of region to give output folder gdb with processed files for your region", type=str)
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
arcpy.env.workspace = workspace_in = args["input"][0] #inputs2020.gdb

parentDirectory = os.path.abspath(os.path.join(arcpy.env.workspace, os.pardir))
if arcpy.Exists(os.path.join(parentDirectory, "projected.gdb")):
    projGDB = workspace_out = os.path.join(parentDirectory, "projected.gdb")
else:
    arcpy.CreateFileGDB_management(parentDirectory, "projected.gdb")
    projGDB = workspace_out = os.path.join(parentDirectory, "projected.gdb")
print(os.path.abspath(workspace_out)) #projected.gdb


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

process = csv_file[csv_file['Process?'] == "Yes"]
process = process.reset_index()

import_functions.BatchProject1.project(process, workspace_in, workspace_out, cellSize, template=False)

###########################################################################

# Name: Country_bounds.py
# Description: Take world boundaries file and divvy it up into indiv countries that we need
import import_functions.Country_bounds_function

bounds = csv_file[csv_file['Country Bound File'] == "Yes"]
bounds = bounds.reset_index()
list_of_countries = args["region_name"]
condition = args["extract_region"][0]
print(list_of_countries)
print(condition)

#work_in = inputs2020; work_out = projected.gdb
workspace_in, workspace_out = import_functions.Country_bounds_function.create_bounds(bounds, workspace_in,
                                                                workspace_out, list_of_countries, condition)
#work_in = projected.gdb; work_out = country_bounds.gdb


###########################################################################


# Name: All_clip.py
# Description: Clip each file to each country (M x N)
# Feature classes = Clip and Rasters = Extract by Mask

import import_functions.All_clip_function

workspace_countries = workspace_out
workspace_files = projGDB

country_names, workspace_out = import_functions.All_clip_function.all_clip(process, workspace_files, workspace_countries,
                                                                           list_of_countries)
#work_out = country_name.gdb, work_out = projected.gdb



###########################################################################

# Name: Extract_Attributes.py
# Description: For some files, we only need certain categories
# this may have to be in preprocessing if a euc dist is produced
# and the condition in stage 1 applies to the euc dist, not original categories

if not csv_file['Extract Attributes'].isnull().all():
    extract = process[process['Extract Attributes'].notnull()]
    extract = extract.reset_index()

    import import_functions.Extract_Attributes_function

    import_functions.Extract_Attributes_function.extract(country_names, extract, workspace_out)

###########################################################################

# Name: Euclidean_Distance.py
# Description: Turns feature classes or rasters into euclidean distance rasters
# Euclidean Distance calculates, for each cell, the Euclidean distance to the closest source.

import import_functions.Euclidean_Distance_function

parentDirectory = os.path.abspath(os.path.join(workspace_in, os.pardir))
region_bounds = os.path.join(parentDirectory, "country_bounds.gdb", list_of_countries[0])
desc = arcpy.Describe(region_bounds)
xmin = desc.extent.XMin
xmax = desc.extent.XMax
ymin = desc.extent.YMin
ymax = desc.extent.YMax
print(region_bounds)
arcpy.env.extent = arcpy.Extent(xmin, ymin, xmax, ymax)

cellSize = int(str.split(cellSize, " ")[0])

ed = process[process['Euclidean Distance Raster'] == "Yes"]
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