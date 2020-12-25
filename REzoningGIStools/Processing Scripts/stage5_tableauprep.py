import arcpy
from itertools import count, product, islice

arcpy.env.overwriteOutput = True

arcpy.env.workspace = scenario_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers_wind.gdb"
scenario = "allTiers" # optional - a column of the  output shapefile will list which run or test the results refer to
technology = "wind" # solar or wind
print(scenario_gdb)

countries = {  ## required - enter regions and their abbreviation/country code
    'DRC': 'DRC',
    'Angola': 'AO',
    'Botswana': 'BW',
    'Eswatini': 'SZ',
    'Lesotho': 'LS',
    'Mozambique': 'MZ',
    'Malawi': 'MW',
    'Namibia': 'NA',
    'South_Africa': 'SA',
    'Tanzania': 'TZ',
    'Zambia': 'ZM',
    'Zimbabwe': 'ZI',
}

#######################EDIT
featureclasses = arcpy.ListFeatureClasses("*_zones")
print(featureclasses)



#########################
## CREATE NEW ZONE IDS ##
#########################

for each in featureclasses:
    print(each)
    # Add country name, code and energy source
    arcpy.AddField_management(each, "Energy_Source", "Text")
    arcpy.CalculateField_management(each, "Energy_Source", "'{}'".format(technology))
    arcpy.AddField_management(each, "Country", "Text")
    country = each.split("_areas_attr_zones")[0]
    arcpy.CalculateField_management(each, "Country", "'{}'".format(country))
    arcpy.AddField_management(each, "CountryCode", "Text")
    country_code = countries.get(country)
    arcpy.CalculateField_management(each, "CountryCode", "'{}'".format(country_code))
    arcpy.AddField_management(each, "SAPPzoneID", "Text")
    arcpy.CalculateField_management(each, "SAPPzoneID", """"{}_{}".format(!CountryCode!, !zoneID!)""")


outputfilename = scenario + "_" + technology + "_finalOutput"
scenarioCountries = arcpy.Merge_management(featureclasses, outputfilename)



print(arcpy.GetMessages())
