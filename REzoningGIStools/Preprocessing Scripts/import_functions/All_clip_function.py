# Name: All_clip.py
# Description: Clip each file to each country (M x N)
#Feature classes = Clip and Rasters = Extract by Mask

import arcpy
import os

## arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"

def all_clip(dataframe, workspace_files, workspace_countries, list_of_countries):

    fc_vectors = []
    vector_names = []
    fc_rasters = []
    raster_names = []
    fc_countries = []
    global country_names
    country_names = list_of_countries
    country_names.sort()

    for j in range(len(country_names)):
        if " " in country_names[j]:
            country_names[j] = country_names[j].replace(" ", "_")
    ##
    ##if arcpy.Exists('R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\ALL_AICD_Countries_Power_Plants_Projected'):
    ##    arcpy.Rename_management('R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\ALL_AICD_Countries_Power_Plants_Projected', 'R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\Power_Plants_Projected')

    # Get all feature classes to clip
    dirpath = os.path.abspath(workspace_files)
    for index, each in dataframe.iterrows():
        filename = each['Output File Name']+"_Projected"
        filetype = each["File Type"]
        if filetype =="Feature Class":
            fc_vectors.append(os.path.join(dirpath, filename))
            vector_names.append(filename)
        if filetype == "Raster":
            fc_rasters.append(os.path.join(dirpath, filename))
            raster_names.append(filename)
    # for dirpath, dirnames, filenames in walk:
    #     for filename in filenames:
    #         fc_vectors.append(os.path.join(dirpath, filename))
    #         vector_names.append(filename)
    #
    # # Get all rasters to clip
    # walk = arcpy.da.Walk(workspace_files, datatype=["RasterCatalog", "RasterDataset"])
    #
    # for dirpath, dirnames, filenames in walk:
    #     for filename in filenames:
    #         fc_rasters.append(os.path.join(dirpath, filename))
    #         raster_names.append(filename)

    # Get all countries to clip to
    walk = arcpy.da.Walk(workspace_countries, datatype="FeatureClass")

    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            if filename in country_names:
                fc_countries.append(os.path.join(dirpath, filename))
                # country_names.append(filename)
    fc_countries.sort()
    parentDirectory = os.path.abspath(os.path.join(workspace_countries, os.pardir))
    print(parentDirectory)

    for j in range(len(country_names)):
        print(country_names[j])

        if arcpy.Exists(os.path.join(parentDirectory, country_names[j] + ".gdb")):
            arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")
        else:
            arcpy.CreateFileGDB_management(parentDirectory, country_names[j] + ".gdb")
            arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")

        print(workspace_out)
        for i in range(len(fc_vectors)):
            print(vector_names[i])
            outfc = "{}_{}_Clipped".format(country_names[j], vector_names[i])
            if arcpy.Exists(outfc):
                print("An output file with this name ({}) already exists; skipping clipping this row".format(outfc))
                continue
            arcpy.Clip_analysis(fc_vectors[i], fc_countries[j], outfc)
            print(arcpy.GetMessages())

    for j in range(len(country_names)):
        print(country_names[j])
        if arcpy.Exists(os.path.join(parentDirectory, country_names[j] + ".gdb")):
            arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")
        else:
            arcpy.CreateFileGDB_management(parentDirectory, country_names[j] + ".gdb")
            arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")
        print(workspace_out)
        for i in range(len(fc_rasters)):
            print(raster_names[i])
            outfc = "{}_{}_Clipped".format(country_names[j], raster_names[i])
            if arcpy.Exists(outfc):
                print("An output file with this name already exists; skipping clipping this row")
                continue
            arcpy.Clip_management(in_raster=fc_rasters[i], rectangle="",
                                  clipping_geometry="ClippingGeometry",
                                  in_template_dataset=fc_countries[j],
                                  out_raster=outfc)
            print(arcpy.GetMessages())
    return country_names, workspace_out