# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.
# VECTORS

import arcpy
import os
import argparse
import pandas as pd
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-pf", "--project_file", required=True, nargs='+', help="csv_file of 6 columns: \n"
                "1 : in_features(feature class or raster), \n"
                "2 : name of output file or raster, \n"
                "3 : feature_class if feature class and raster if raster \n"
                "4 : input coordinate system for arcpy.SpatialReference \n"
                "5 : output coordinate system for arcpy.SpatialReference \n"
                "6 : If raster, resampling method (Nearest/Bilinear/Cubic/Majority", type=str)
ap.add_argument("-cs", "--cell_size", required=False, nargs='+',
                help="cell size in the form 'X Y' such as 500 500 in quotes ",
                type=str)
ap.add_argument("-tr", "--template_raster", required=False, nargs='+',
                help="if you want to choose a template raster to snap all rasters, provide file path here \n"
                "If you do not have one in mind, the first raster processed will be used as the template for all others",
                type=str)
ap.add_argument("-ed", "--ed_files", required=False, nargs='*',
                help="list of file names (shp or raster) (without extension) requiring euclidean distance rasters separated by spaces", type=str)
ap.add_argument("-md", "--max_dist", required=False, nargs='+', help="max distance for eucl distance (optional)", type=str)
ap.add_argument("-lf", "--lulc_file", required=False, nargs='+', help="name of land use land cover file to extract", type=str)
ap.add_argument("-s", "--solar", required=False, nargs='+',
                help="which land use categories to extract (include) for solar (numbers separated by commas) \n"
                "Reference for LULC Categories to Process LULC Data \n"
                "# Code   Class Name \n"
                "# 1  Broadleaf Evergreen Forest \n"
                "# 2  Broadleaf Deciduous Forest \n"
                "# 3  Needleleaf Evergreen Forest \n"
                "# 4  Needleleaf Deciduous Forest \n"
                "# 5  Mixed Forest \n"
                "# 6  Tree Open \n"
                "# 7  Shrub \n"
                "# 8  Herbaceous \n"
                "# 9  Herbaceous with Sparse Tree/Shrub \n"
                "# 10 Sparse vegetation \n"
                "# 11   Cropland \n"
                "# 12  Paddy field \n"
                "# 13  Cropland / Other Vegetation Mosaic \n"
                "# 14  Mangrove \n"
                "# 15  Wetland \n"
                "# 16  Bare area,consolidated(gravel,rock) \n"
                "# 17  Bare area,unconsolidated (sand) \n"
                "# 18  Urban \n"
                "# 19  Snow / Ice \n"
                "# 20  Water bodies", type=str)
ap.add_argument("-wn", "--wind_nonag", required=False, nargs='+',
                help="which land use categories to extract (include) for non-ag wind (numbers separated by commas)", type=str)
ap.add_argument("-wa", "--wind_ag", required=False, nargs='+',
                help="which land use categories to extract (include) for ag wind (numbers separated by commas)", type=str)
ap.add_argument("-cf", "--country_file", required=True, nargs='+',
                help="name of projected world country boundaries file to extract (projected.gdb\country_file_Projected)", type=str)
ap.add_argument("-c", "--country_list", required=True, nargs='*', help="list of countries in quotes and separated by spaces", type=str)

args = vars(ap.parse_args())
print(args)


###########################################################################

# Name: Batch_Project.py

#csv
csv_file = pd.read_csv(args["project_file"][0], header=True)
#print(csv_file[col][row])

### Output coordinate system - leave it empty
##out_cs = arcpy.SpatialReference('Africa Albers Equal Area Conic')

# Template dataset - it has GCS_WGS_1984 coordinate system
template = ""

# Geographic transformation - 
transformation = ""

if args["template_raster"] is not None:
    arcpy.env.snapRaster = args["template_raster"][0]
    print("Now snapping to provided template raster")

if args["cell_size"] is None:
    cellSize = "500 500"
else:
    cellSize = args["cell_size"][0]


#####parsing the csv_file
arcpy.env.workspace = workspace_in = args["input"][0]
print(workspace_in)

parentDirectory = os.path.abspath(os.path.join(arcpy.env.workspace, os.pardir))
print(parentDirectory)
if arcpy.Exists(os.path.join(parentDirectory, "projected.gdb")):
    projGDB = workspace_out = os.path.join(parentDirectory, "projected.gdb")  # Make a check for this
else:
    arcpy.CreateFileGDB_management(parentDirectory, "projected.gdb")
    projGDB = workspace_out = os.path.join(parentDirectory, "projected.gdb") #Make a check for this
print(os.path.abspath(workspace_out))

print(arcpy.ListFeatureClasses())
for i in range(len(csv_file)):
    infile = csv_file[0][i]
    print(infile)
    outfile = csv_file[1][i]
    print(outfile)
    outfc = os.path.join(workspace_out, outfile + "_Projected")

    if arcpy.Exists(outfc):
        print("An output file with this name already exists; skipping this row")
        if (i == 0):
            if args["template_raster"] is None:
                arcpy.env.snapRaster = outfc
                print("Now snapping to first raster")
        continue
    # if (infile == "gm_lc_v3_2_2"):
    #     continue

    if(csv_file[2][i] == 'Feature Class'):

        print("Feature Class")
        print(infile, outfc, arcpy.SpatialReference(csv_file[4][i]), arcpy.SpatialReference(csv_file[3][i]))
        arcpy.Project_management(infile, outfc, arcpy.SpatialReference(csv_file[4][i]),
                                 in_coor_system = arcpy.SpatialReference(csv_file[3][i]))
        print(arcpy.GetMessages())

    elif(csv_file[2][i] == 'Raster'):
        print("Raster")
        arcpy.ProjectRaster_management(infile, outfc, arcpy.SpatialReference(csv_file[4][i]),
                                       in_coor_system = arcpy.SpatialReference(csv_file[3][i]),
                                       resampling_type = csv_file[5][i], cell_size=cellSize)
        print(arcpy.GetMessages())
        if (i == 0):
            if args["template_raster"] is None:
                arcpy.env.snapRaster = outfc
                print("Now snapping to first raster")


###########################################################################

# Name: Euclidean_Distance.py
# Description: Turns feature classes or rasters into euclidean distance rasters
# Euclidean Distance calculates, for each cell, the Euclidean distance to the closest source.

arcpy.env.workspace = workspace_out

if args["ed_files"] is not None:


    if args["max_dist"] is None:
        maxDistance = 4000
    else:
        maxDistance = args["max_dist"][0]

    cellSize = int(str.split(cellSize, " ")[0])

    list_of_inputs = args["ed_files"]

    for item in list_of_inputs:
        print(item)
        # Set local variables
        outfc = os.path.join(workspace_out, item + "_EucDist")
        if arcpy.Exists(outfc):
            print("An output file with this name already exists; skipping this row")
            continue

        # Execute EucDistance
        outEucDistance = EucDistance(in_source_data = item, maximum_distance = maxDistance, cell_size = cellSize)


        # Save the output 
        outEucDistance.save(outfc)



###########################################################################

# Name: Extract_Attributes.py
# Description: For LULC, we only need certain categories,
# so we filter that raster
# Each alt energy is different, so we need a file for solar/wind/etc

if args["lulc_file"] is not None:

    # Set infile
    inRaster = args["lulc_file"][0]
    
    print(arcpy.ListRasters())

    if args["solar"] is not None:
        if arcpy.Exists("lulc_for_solar"):
            print("A lulc for solar file with this name already exists; skipping this row")
        else:
            solar_exclusion = """ "VALUE" IN ({}) """.format(args["solar"][0])
            print(solar_exclusion)

            #solar_exclusion = """ "Value" In (1,2,3,4,5,6,11,12,13,14,15,18,19,20) """
            # #wind_nonag_exclusion = """ "VALUE" In (1,2,3,4,5,11,12,13,14,15,18,19,20) """
            # #wind_ag_exclusion = """ "VALUE" In (1,2,3,4,5,12,14,15,18,19,20) """

            # Execute ExtractByAttributes
            solar_extract = ExtractByAttributes(inRaster, solar_exclusion)

            # Save the output
            solar_extract.save(os.path.join(workspace_out, "lulc_for_solar"))

            print(arcpy.GetMessages())

    if args["wind_nonag"] is not None:
        if arcpy.Exists("lulc_for_wind_nonag"):
            print("A lulc for wind nonag file with this name already exists; skipping this row")
        else:
            wind_nonag_exclusion = """ "VALUE" IN ({}) """.format(args["wind_nonag"][0])
            print(wind_nonag_exclusion)
            wind_nonag_extract = ExtractByAttributes(inRaster, wind_nonag_exclusion) # Execute ExtractByAttributes
            wind_nonag_extract.save(os.path.join(workspace_out, "lulc_for_wind_nonag")) # Save the output

    if args["wind_ag"] is not None:
        if arcpy.Exists("lulc_for_wind_ag"):
            print("A lulc for wind ag file with this name already exists; skipping this row")
        else:
            wind_ag_exclusion = """ "VALUE" IN ({}) """.format(args["wind_ag"][0])
            print(wind_ag_exclusion)
            wind_ag_extract = ExtractByAttributes(inRaster, wind_ag_exclusion) # Execute ExtractByAttributes
            wind_ag_extract.save(os.path.join(workspace_out, "lulc_for_wind_ag")) # Save the output

###########################################################################

# Name: Country_bounds.py
# Description: Take world boundaries file and divvy it up into indiv countries that we need


country_file = args["country_file"][0]
parentDirectory = os.path.abspath(os.path.join(country_file, os.pardir))
print(parentDirectory)
basename = os.path.basename(parentDirectory).split('.')[0]
dir = os.path.dirname(parentDirectory)
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

#infile = r"C:\Users\anagha.uppal\Downloads\TM_WORLD_BORDERS-0.3\TM_WORLD_BORDERS-0.3.shp"
#arcpy.MakeFeatureLayer_management('TM_WORLD_BORDERS-0.3.shp',"countries_lyr")
arcpy.MakeFeatureLayer_management(country_file,"countries_lyr")


list_of_countries = args["country_list"]
print(list_of_countries)
print(list_of_countries[0])

##list_of_countries = ["Angola", "Botswana", "DRC", "Lesotho", "Malawi",
##                     "Mozambique", "Namibia", "South Africa", "Swaziland",
##                     "Tanzania", "Zambia", "Zimbabwe"]


for item in list_of_countries:
    print(item)
    # if "_" in item:
    #     item.replace("_", " ")
    query = """"NAME" LIKE '%s'"""%item
    print(query)
    country = arcpy.SelectLayerByAttribute_management("countries_lyr", 'NEW_SELECTION', query)
    outfc = os.path.join(workspace_out, item)
    arcpy.CopyFeatures_management(country, outfc)
    arcpy.SelectLayerByAttribute_management("countries_lyr","CLEAR_SELECTION")
    print(arcpy.GetMessages())

                            

###########################################################################

# Name: All_clip.py
# Description: Clip each file to each country (M x N)
#Feature classes = Clip and Rasters = Extract by Mask


## arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"

  
workspace_files = projGDB
workspace_countries = workspace_out

fc_vectors = []
vector_names = []
fc_rasters = []
raster_names = []
fc_countries = []
country_names = []
##
##if arcpy.Exists('R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\ALL_AICD_Countries_Power_Plants_Projected'):
##    arcpy.Rename_management('R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\ALL_AICD_Countries_Power_Plants_Projected', 'R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\Power_Plants_Projected')

#Get all feature classes to clip
walk = arcpy.da.Walk(workspace_files, datatype="FeatureClass")  
  
for dirpath, dirnames, filenames in walk:  
   for filename in filenames:
       fc_vectors.append(os.path.join(dirpath, filename))
       vector_names.append(filename)

#Get all rasters to clip
walk = arcpy.da.Walk(workspace_files, datatype=["RasterCatalog", "RasterDataset"])

for dirpath, dirnames, filenames in walk:  
   for filename in filenames:
       fc_rasters.append(os.path.join(dirpath, filename))
       raster_names.append(filename)

#Get all countries to clip to
walk = arcpy.da.Walk(workspace_countries, datatype="FeatureClass")  
  
for dirpath, dirnames, filenames in walk:  
   for filename in filenames:
       if filename != "shp":
           fc_countries.append(os.path.join(dirpath, filename))
           country_names.append(filename)

print(vector_names, raster_names, country_names)

parentDirectory = os.path.abspath(os.path.join(workspace_countries, os.pardir))
print(parentDirectory)

for j in range(len(fc_countries)):
    print(country_names[j])
    if " " in country_names[j]:
        country_names[j].replace(" ", "_")

    if arcpy.Exists(os.path.join(parentDirectory, country_names[j]+".gdb")):
        arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")
    else:
        arcpy.CreateFileGDB_management(parentDirectory, country_names[j]+".gdb")
        arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")

    print(workspace_out)
    for i in range(len(fc_vectors)):
        print(vector_names[i])
        outfc = "{}_{}_Clipped".format(country_names[j],vector_names[i])
        arcpy.Clip_analysis(fc_vectors[i], fc_countries[j], outfc)
        print(arcpy.GetMessages())

for j in range(len(fc_countries)):
    print(country_names[j])
    if arcpy.Exists(os.path.join(parentDirectory, country_names[j] + ".gdb")):
        arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")
    else:
        arcpy.CreateFileGDB_management(parentDirectory, country_names[j] + ".gdb")
        arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, country_names[j] + ".gdb")
    print(workspace_out)
    for i in range(len(fc_rasters)):
        print(raster_names[i])
        outfc = "{}_{}_Clipped".format(country_names[j],raster_names[i])
        arcpy.Clip_management(in_raster=fc_rasters[i], rectangle="",
                            clipping_geometry="ClippingGeometry",
                            in_template_dataset=fc_countries[j],
                            out_raster=outfc)
        print(arcpy.GetMessages())



        



