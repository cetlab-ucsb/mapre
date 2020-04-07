# Name: Country_bounds.py
# Description: Take world boundaries file and divvy it up
# into indiv countries that we need

import arcpy
import os

def create_bounds(bounds, workspace_in, workspace_out, list_of_countries):
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

    print(os.path.abspath(workspace_out))
    print(arcpy.ListFeatureClasses())
    print(workspace_in)

    bounds_file = os.path.join(workspace_in, bounds['Output File Name'][0] + "_Projected")
    arcpy.MakeFeatureLayer_management(bounds_file, "countries_lyr")


    for item in list_of_countries:
        print(item)

        query = """"NAME" LIKE '%s'""" % item
        print(query)
        country = arcpy.SelectLayerByAttribute_management("countries_lyr", 'NEW_SELECTION', query)
        if " " in item:
            item = item.replace(" ", "_")
        outfc = os.path.join(workspace_out, item)
        if arcpy.Exists(outfc):
            print("A region bounds file with this name already exists; skipping creating this region file")
            continue
        arcpy.CopyFeatures_management(country, outfc)
        arcpy.SelectLayerByAttribute_management("countries_lyr", "CLEAR_SELECTION")
        print(arcpy.GetMessages())
    return workspace_in, workspace_out