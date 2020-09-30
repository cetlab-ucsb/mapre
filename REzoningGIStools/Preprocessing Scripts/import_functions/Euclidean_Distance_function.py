# Name: Euclidean Distance.py
# Description: Produce euc dis rasters

import arcpy
import os
import argparse
from arcpy.sa import *

def euc_dist(ed, country_names, region_bounds, cellSize, workspace_out):

    if len(ed) > 0:
        arcpy.env.workspace = workspace_out
        arcpy.env.mask = region_bounds

        for i in range(len(ed)):
            # Set local variables

            item = "{}_{}_Projected_Clipped_extract".format(country_names[0], ed['Output File Name'][i])
            if not arcpy.Exists(item):
                item = "{}_{}_Projected_Clipped".format(country_names[0], ed['Output File Name'][i])
            print(item)
            outfc = os.path.join(workspace_out, item + "_EucDist")
            if arcpy.Exists(outfc):
                print("An output file with this name already exists; skipping this row")
                continue

            # Execute EucDistance
            outEucDistance = EucDistance(in_source_data=item, cell_size=cellSize)
            print(arcpy.GetMessages())

            # Save the output
            outEucDistance.save(outfc)