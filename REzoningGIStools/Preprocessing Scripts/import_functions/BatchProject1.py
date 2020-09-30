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
        print("*** infile: ", infile, ", outfile: ", outfile)
        outfc = os.path.join(workspace_out, outfile + "_Projected")

        # if not dataframe['Process?'][i] == "Yes":
        #     continue
        dsc = arcpy.Describe(infile)
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

        try:
            outProj = int(dataframe['Output Projection'][i])
        except:
            outProj = dataframe['Output Projection'][i]

        try:
            inProj = int(dataframe['Input Projection'][i])
        except:
            inProj = dataframe['Input Projection'][i]

        if (dataframe['File Type'][i] == 'Feature Class'):

            print("Feature Class")
            print(infile, outfc, inProj, outProj)
            arcpy.Project_management(infile, outfc, out_coor_system=arcpy.SpatialReference(outProj),
                                     in_coor_system=arcpy.SpatialReference(inProj))
            print(arcpy.GetMessages())

        elif (dataframe['File Type'][i] == 'Raster'):
            print("Raster")
            print(infile, outfc, inProj, outProj)
            arcpy.ProjectRaster_management(infile, outfc, out_coor_system=arcpy.SpatialReference(outProj),
                                           in_coor_system=arcpy.SpatialReference(inProj), cell_size=cellSize,
                                           resampling_type=dataframe['Resampling Type (for Raster)'][i])
            print(arcpy.GetMessages())
            if template:
                arcpy.env.snapRaster = outfc
                print("Now snapping to template raster")