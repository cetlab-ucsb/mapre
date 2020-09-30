# Name: Country_bounds.py
# Description: Take world boundaries file and divvy it up
# into indiv countries that we need

import arcpy
import os

workspace = arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\country_bounds.gdb"
print(arcpy.ListFeatureClasses())

#infile = r"C:\Users\anagha.uppal\Downloads\TM_WORLD_BORDERS-0.3\TM_WORLD_BORDERS-0.3.shp"
#arcpy.MakeFeatureLayer_management('TM_WORLD_BORDERS-0.3.shp',"countries_lyr")
arcpy.MakeFeatureLayer_management('shp',"countries_lyr")
##fc = arcpy.ListFields("countries_lyr")
##for field in fc:
##    print(field.name)
##
##myList = [row[0] for row in arcpy.da.SearchCursor("countries_lyr", "NAME")]
##print(myList)

list_of_countries = ["Angola", "Botswana", "DRC", "Lesotho", "Malawi",
                     "Mozambique", "Namibia", "South Africa", "Swaziland",
                     "Tanzania", "Zambia", "Zimbabwe"]


for item in list_of_countries:
    print(item)
    query = """"NAME" LIKE '%s'"""%item
    print(query)
    country = arcpy.SelectLayerByAttribute_management("countries_lyr", 'NEW_SELECTION', query)
    outfc = os.path.join(workspace, item)
    arcpy.CopyFeatures_management(country, outfc)
    arcpy.SelectLayerByAttribute_management("countries_lyr","CLEAR_SELECTION")

                            
