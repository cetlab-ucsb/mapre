# Name: Country_bounds.py
# Description: Take world boundaries file and divvy it up
# into indiv countries that we need

import arcpy
import os
import argparse

#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-if", "--input_file", required=True, nargs='+',
                help="name of world country boundaries file to extract", type=str)
ap.add_argument("-o", "--output", required=True, nargs='+', help="output directory \n"
                "if input directory is same as output directory, we recommend removing original file from directory after running this function", type=str)
ap.add_argument("-c", "--country_list", required=True, nargs='*', help="list of countries separated by spaces", type=str)

args = vars(ap.parse_args())

arcpy.env.workspace = args["input"][0]
print(arcpy.ListFeatureClasses())
out_workspace = args["output"][0]

#infile = r"C:\Users\anagha.uppal\Downloads\TM_WORLD_BORDERS-0.3\TM_WORLD_BORDERS-0.3.shp"
#arcpy.MakeFeatureLayer_management('TM_WORLD_BORDERS-0.3.shp',"countries_lyr")
arcpy.MakeFeatureLayer_management(args["input_file"][0],"countries_lyr")
##fc = arcpy.ListFields("countries_lyr")
##for field in fc:
##    print(field.name)
##
##myList = [row[0] for row in arcpy.da.SearchCursor("countries_lyr", "NAME")]
##print(myList)

list_of_countries = args["country_list"][0]
print(list_of_countries)

##list_of_countries = ["Angola", "Botswana", "DRC", "Lesotho", "Malawi",
##                     "Mozambique", "Namibia", "South Africa", "Swaziland",
##                     "Tanzania", "Zambia", "Zimbabwe"]


for item in list_of_countries:
    print(item)
    query = """"NAME" LIKE '%s'"""%item
    print(query)
    country = arcpy.SelectLayerByAttribute_management("countries_lyr", 'NEW_SELECTION', query)
    outfc = os.path.join(out_workspace, item)
    arcpy.CopyFeatures_management(country, outfc)
    arcpy.SelectLayerByAttribute_management("countries_lyr","CLEAR_SELECTION")

                            
