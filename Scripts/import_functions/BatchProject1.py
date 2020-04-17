# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.

import arcpy
import os
import argparse
import pandas as pd
from arcpy.sa import *

def project(dataframe, workspace_in, workspace_out, cellSize, template=False):
    arcpy.env.workspace = workspace_in

    for i in range(len(dataframe)):
        infile = dataframe['Input File Name'][i]
        outfile = dataframe['Output File Name'][i]
        print("infile: ", infile, ", outfile: ", outfile)
        outfc = os.path.join(workspace_out, outfile + "_Projected")

        dsc = arcpy.Describe(infile)

        if not dataframe['Process?'][i] == "Yes":
            continue
        if dsc.spatialReference.Name == "Unknown":
            print('skipped this fc due to undefined coordinate system: ' + infile)
            continue
        if arcpy.Exists(outfc):
            print("An output file with this name already exists; skipping projecting this row")
            if template:
                arcpy.env.snapRaster = outfc
                print("Now snapping to existing raster")
            continue
        # if (infile == "gm_lc_v3_2_2"):
        #     continue

        if (dataframe['File Type'][i] == 'Feature Class'):

            print("Feature Class")
            print(infile, outfc, dataframe['Input Projection'][i], dataframe['Output Projection'][i])
            arcpy.Project_management(infile, outfc, arcpy.SpatialReference(dataframe['Output Projection'][i]),
                                     in_coor_system=arcpy.SpatialReference(dataframe['Input Projection'][i]))
            print(arcpy.GetMessages())

        elif (dataframe['File Type'][i] == 'Raster'):
            print("Raster")
            arcpy.ProjectRaster_management(infile, outfc, arcpy.SpatialReference(dataframe['Output Projection'][i]),
                                           in_coor_system=arcpy.SpatialReference(dataframe['Input Projection'][i]),
                                           resampling_type=dataframe['Resampling Type (for Raster)'][i], cell_size=cellSize)
            print(arcpy.GetMessages())
            if template:
                arcpy.env.snapRaster = outfc
                print("Now snapping to template raster")