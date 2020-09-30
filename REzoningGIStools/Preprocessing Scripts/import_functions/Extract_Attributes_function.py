# Name: Extract_Attributes.py
# Description: For LULC, we only need certain categories,
# so we filter that raster
# Each alt energy is different, so we need a file for solar/wind/etc

import arcpy
import os
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

def extract(country_names, extract, workspace_out):
    for i in range(len(extract)):
        inFile = "{}_{}_Projected_Clipped".format(country_names[0], extract['Output File Name'][i])
        print(inFile)

        outfc = os.path.join(workspace_out, "{}_extract".format(inFile))
        if arcpy.Exists(outfc):
            print("An extract file with this name already exists; skipping extracting this row")
            continue
        if extract['File Type'][i] == "Raster":
            threshold_exclusion = """{}""".format(extract['Extract Attributes'][i])
            print(threshold_exclusion)

            # solar_exclusion = """ "Value" In (1,2,3,4,5,6,11,12,13,14,15,18,19,20) """
            # #wind_nonag_exclusion = """ "VALUE" In (1,2,3,4,5,11,12,13,14,15,18,19,20) """
            # #wind_ag_exclusion = """ "VALUE" In (1,2,3,4,5,12,14,15,18,19,20) """

            # Execute ExtractByAttributes
            threshold_extract = ExtractByAttributes(inFile, threshold_exclusion)
            # Save the output
            threshold_extract.save(os.path.join(workspace_out, "{}_extract".format(inFile)))

        elif extract['File Type'][i] == "Feature Class":
            threshold_exclusion = """{}""".format(extract['Extract Attributes'][i])
            print(threshold_exclusion)
            # Make Feature Layer
            if arcpy.Exists("in_memory/inFile_lyr"):
                arcpy.Delete_management("in_memory/inFile_lyr")
            arcpy.MakeFeatureLayer_management(inFile, "in_memory/inFile_lyr")

            # Execute ExtractByAttributes
            threshold_extract = arcpy.SelectLayerByAttribute_management("in_memory/inFile_lyr", "NEW_SELECTION",
                                                    threshold_exclusion)
            # Save the output
            arcpy.CopyFeatures_management(threshold_extract, os.path.join(workspace_out, "{}_extract".format(inFile)))
            arcpy.SelectLayerByAttribute_management("in_memory/inFile_lyr", "CLEAR_SELECTION")


        print(arcpy.GetMessages())