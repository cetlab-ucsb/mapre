# Name: Euclidean Distance.py
# Description: Produce euc dis rasters

import arcpy
import os
import argparse
from arcpy.sa import *

def euc_dist(ed, country_names, maxDistance, cellSize, workspace_out):

    if len(ed) > 0:
        arcpy.env.workspace = workspace_out

        for i in range(len(ed)):
            # Set local variables

            item = "{}_{}_Projected_Clipped".format(country_names[0], ed['Output File Name'][i])
            outfc = os.path.join(workspace_out, item + "_EucDist")
            if arcpy.Exists(outfc):
                print("An output file with this name already exists; skipping this row")
                continue

            # Execute EucDistance
            outEucDistance = EucDistance(in_source_data=item, maximum_distance=maxDistance, cell_size=cellSize)

            # Save the output
            outEucDistance.save(outfc)