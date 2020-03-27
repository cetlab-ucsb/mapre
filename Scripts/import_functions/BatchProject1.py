# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.

import arcpy
import os
import argparse
import pandas as pd
from arcpy.sa import *

def project(dataframe, workspace_in, workspace_out, cellSize, template=False):
    arcpy.env.workspace = workspace_in

    print(arcpy.ListFeatureClasses())

    for i in range(len(dataframe)):
        infile = dataframe['Input File Name'][i]
        print(infile)
        outfile = dataframe['Output File Name'][i]
        print(outfile)
        outfc = os.path.join(workspace_out, outfile + "_Projected")

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
            arcpy.ProjectRaster_management(infile, outfc, arcpy.SpatialReference(dataframe['Output Projection'][0]),
                                           in_coor_system=arcpy.SpatialReference(dataframe['Input Projection'][0]),
                                           resampling_type=dataframe['Resampling Type (for Raster)'][0], cell_size=cellSize)
            print(arcpy.GetMessages())
            if template:
                arcpy.env.snapRaster = outfc
                print("Now snapping to template raster")