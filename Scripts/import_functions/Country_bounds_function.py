# Name: Country_bounds.py
# Description: Take world boundaries file and divvy it up
# into indiv countries that we need

import arcpy
import os

def create_bounds(bounds, workspace_in, workspace_out, list_of_countries, condition):
    parentDirectory = os.path.abspath(os.path.join(workspace_in, os.pardir))
    print(parentDirectory)
    basename = os.path.basename(parentDirectory).split('.')[0]
    dir = os.path.dirname(parentDirectory)
    workspace_in = workspace_out
    if arcpy.Exists(os.path.join(dir, basename + ".gdb")):
        parentDirectory = os.path.abspath(os.path.join(parentDirectory, os.pardir))
        print(parentDirectory)
    if arcpy.Exists(os.path.join(parentDirectory, "country_bounds.gdb")):
        arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, "country_bounds.gdb")
    else:
        arcpy.CreateFileGDB_management(parentDirectory, "country_bounds.gdb")
        arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, "country_bounds.gdb")


    bounds_file = os.path.join(workspace_in, bounds['Output File Name'][0] + "_Projected")
    arcpy.MakeFeatureLayer_management(bounds_file, "countries_lyr")

    print(condition)
    country = arcpy.SelectLayerByAttribute_management("countries_lyr", 'NEW_SELECTION', condition)
    for cntry in list_of_countries:
        if " " in cntry:
            cntry = cntry.replace(" ", "_")
        outfc = os.path.join(workspace_out, cntry)
        print(outfc)
        if arcpy.Exists(outfc):
            print("A region bounds file with this name already exists; skipping creating this region file")
        else:
            arcpy.CopyFeatures_management(country, outfc)
            arcpy.SelectLayerByAttribute_management("countries_lyr", "CLEAR_SELECTION")
            print(arcpy.GetMessages())
    return workspace_in, workspace_out