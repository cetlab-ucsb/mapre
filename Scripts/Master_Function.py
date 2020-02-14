# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.
# VECTORS

import arcpy
import os
import argparse
import pandas as pd


#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-pf", "--project_file", required=True, nargs='+', help="csv_file of 5 columns: \n"
                "1 : in_features(feature class or raster), \n"
                "2 : feature_class if feature class and raster if raster \n"
                "3 : input coordinate system for arcpy.SpatialReference \n"
                "4 : output coordinate system for arcpy.SpatialReference \n"
                "5 : If raster, resampling method (Nearest/Bilinear/Cubic/Majority", type=str)
ap.add_argument("-ed", "--ed_files", required=False, nargs='*',
                help="list of file names (shp or raster) (without extension) requiring euclidean distance rasters separated by spaces", type=str)
ap.add_argument("-md", "--max_dist", required=False, nargs='+', help="max distance for eucl distance (optional)", type=str)
ap.add_argument("-lf", "--lulc_file", required=False, nargs='+', help="name of land use land cover file to extract", type=str)
ap.add_argument("-s", "--solar", required=False, nargs='+',
                help="which land use categories to extract for solar (numbers separated by commas) \n"
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
                help="which land use categories to extract for non-ag wind (numbers separated by commas)", type=str)
ap.add_argument("-wa", "--wind_ag", required=False, nargs='+',
                help="which land use categories to extract for ag wind (numbers separated by commas)", type=str)
ap.add_argument("-cf", "--country_file", required=True, nargs='+',
                help="name of world country boundaries file to extract", type=str)
ap.add_argument("-c", "--country_list", required=True, nargs='*', help="list of countries separated by spaces", type=str)

args = vars(ap.parse_args())
print(args)


###########################################################################

# Name: Batch_Project.py

#csv
csv_file = pd.read_csv(args["project_file"][0], header=None)
#print(csv_file[col][row])

### Output coordinate system - leave it empty
##out_cs = arcpy.SpatialReference('Africa Albers Equal Area Conic')

# Template dataset - it has GCS_WGS_1984 coordinate system
template = ""

# Geographic transformation - 
transformation = ""


#####parsing the csv_file
arcpy.env.workspace = workspace_in = args["input"][0]
print(workspace_in)

parentDirectory = os.path.abspath(os.path.join(arcpy.env.workspace, os.pardir))
print(parentDirectory)
arcpy.CreateFileGDB_management(parentDirectory, "projected.gdb")
projGDB = workspace_out = os.path.join(parentDirectory, "projected.gdb")
print(os.path.abspath(workspace_out))

print(arcpy.ListFeatureClasses())
for i in range(len(csv_file)):
    infile = csv_file[0][i]
    if(csv_file[1][i] == 'Feature Class'):
        outfc = os.path.join(workspace_out, infile + "_Projected")
        print("Feature Class")
        print(infile, outfc, arcpy.SpatialReference(csv_file[3][i]), arcpy.SpatialReference(csv_file[2][i]))
        arcpy.Project_management(infile, outfc, arcpy.SpatialReference(csv_file[3][i]), in_coor_system = arcpy.SpatialReference(csv_file[2][i]))
        print(arcpy.GetMessages())

    elif(csv_file[1][i] == 'Raster'):
        print("Raster")
        initraster = os.path.join(workspace_in, infile)
        print(initraster)
        arcpy.BuildRasterAttributeTable_management(initraster)
        outfc = os.path.join(workspace_out, infile + "_Projected")
        arcpy.ProjectRaster_management(infile, outfc, arcpy.SpatialReference(csv_file[3][i]),
                                       in_coor_system = arcpy.SpatialReference(csv_file[2][i]), resampling_type = csv_file[4][i])
        print(arcpy.GetMessages())



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


    list_of_inputs = args["ed_files"]

    for item in list_of_inputs:
        print(item)
        # Set local variables
        outfc = os.path.join(workspace_out, item + "_EucDist")

        # Execute EucDistance
        outEucDistance = EucDistance(in_source_data = item, maximum_distance = maxDistance, cell_size = 5000)


        # Save the output 
        outEucDistance.save(outfc)



###########################################################################

# Name: Extract_Attributes.py
# Description: For LULC, we only need certain categories,
# so we filter that raster
# Each alt energy is different, so we need a file for solar/wind/etc

if args["lulc_file"] is not None:

    # Set workspace
    
    print(arcpy.ListRasters())

    if args["solar"] is not None:
        solar_exclusion = """ "Value" In ({}) """.format(args["solar"][0])
        print(solar_exclusion)
    #solar_exclusion = """ "Value" In (1,2,3,4,5,6,11,12,13,14,15,18,19,20) """
    #wind_nonag_exclusion = """ "VALUE" In (1,2,3,4,5,11,12,13,14,15,18,19,20) """
    #wind_ag_exclusion = """ "VALUE" In (1,2,3,4,5,12,14,15,18,19,20) """


        arcpy.MakeRasterLayer_management(in_raster=args["lulc_file"][0], out_rasterlayer="lulc_for_solar_lyr", where_clause=solar_exclusion)
    #arcpy.MakeRasterLayer_management(in_raster='gm_lc_v3_2_2', out_rasterlayer="lulc_for_windnonag_lyr", where_clause=wind_nonag_exclusion)
    #arcpy.MakeRasterLayer_management(in_raster='gm_lc_v3_2_2', out_rasterlayer="lulc_for_windag_lyr", where_clause=wind_ag_exclusion)

        selc = arcpy.SelectLayerByAttribute_management("lulc_for_solar_lyr", 'NEW_SELECTION', solar_exclusion)
        outsol = os.path.join(workspace_out, "lulc_for_solar")
    #outwindnag = os.path.join(workspace, "lulc_for_windnonag_lyr")
    #outwindag = os.path.join(workspace, "lulc_for_windag_lyr")

        arcpy.CopyRaster_management(selc, outsol)
    #arcpy.CopyRaster_management("lulc_for_windnonag_lyr", outwindnag)
    #arcpy.CopyRaster_management("lulc_for_windag_lyr", outwindag)

    print(arcpy.GetMessages())



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



        



