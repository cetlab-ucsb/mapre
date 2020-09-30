# Name: Euclidean Distance.py
# Description: Produce euc dis rasters

import arcpy
import os
import argparse
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")


#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-if", "--input_files", required=True, nargs='*',
                help="list of files requiring euclidean distance rasters separated by spaces", type=str)
ap.add_argument("-o", "--output", required=True, nargs='+', help="output directory", type=str)
ap.add_argument("-tr", "--template_raster", required=True, nargs='+', help="template raster to snap to grid", type=str)
ap.add_argument("-md", "--max_dist", required=False, nargs='+', help="max distance (optional)", type=str)
ap.add_argument("-cs", "--cell_size", required=False, nargs='+', help="cell size", type=str)


args = vars(ap.parse_args())

arcpy.env.snapRaster = args["template_raster"][0]


if args["max_dist"] is None:
    maxDistance = 4000
else:
    maxDistance = args["max_dist"][0]

if args["cell_size"] is None:
    cellSize = 500
else:
    cellSize = args["cell_size"][0]


arcpy.env.workspace = args["input"][0]
list_of_inputs = args["input_files"]
print(list_of_inputs[0])

for item in list_of_inputs:
    print(item)
    # Set local variables
    outfc = os.path.join(args["output"][0], item + "_EucDist")

    # Execute EucDistance
    outEucDistance = EucDistance(in_source_data = item, maximum_distance = maxDistance, cell_size = cellSize)


    # Save the output 
    outEucDistance.save(outfc)
