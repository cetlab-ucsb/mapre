# Name: Extract_Attributes.py
# Description: For LULC, we only need certain categories,
# so we filter that raster
# Each alt energy is different, so we need a file for solar/wind/etc

import arcpy
import os
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

def extract(thresholds, inRaster, workspace_out):
    for i in range(len(thresholds)):
        threshold_exclusion = """ "VALUE" IN ({}) """.format(thresholds[i])
        print(threshold_exclusion)

        # solar_exclusion = """ "Value" In (1,2,3,4,5,6,11,12,13,14,15,18,19,20) """
        # #wind_nonag_exclusion = """ "VALUE" In (1,2,3,4,5,11,12,13,14,15,18,19,20) """
        # #wind_ag_exclusion = """ "VALUE" In (1,2,3,4,5,12,14,15,18,19,20) """

        # Execute ExtractByAttributes
        threshold_extract = ExtractByAttributes(inRaster, threshold_exclusion)

        # Save the output
        threshold_extract.save(os.path.join(workspace_out, "lulc_threshold_{}".format(i)))

        print(arcpy.GetMessages())