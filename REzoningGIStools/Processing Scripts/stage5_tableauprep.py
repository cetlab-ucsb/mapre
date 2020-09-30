import arcpy
from itertools import count, product, islice

arcpy.env.overwriteOutput = True

arcpy.env.workspace = scenario_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario.gdb"
scenario = "baseScenario"
technology = "solarPV"

featureclasses = arcpy.ListFeatureClasses("*_skater_clustered")
print(featureclasses)

countries = {
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

#########################
## CREATE NEW ZONE IDS ##
#########################

def multiletters(seq):
    for n in count(1):
        for s in product(seq, repeat=n):
            yield ''.join(s)


for each in featureclasses:
    numRows = arcpy.GetCount_management(each)
    print(numRows)
    zoneIDlist = list(islice(multiletters('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), int(
        str(numRows))))  ## numRows is a "result," so need to convert it to a string first then integer
    print("number of zones: " + str(len(zoneIDlist)))
    arcpy.AddField_management(each, "zoneID", "Text")
    i = 0
    cursor = arcpy.UpdateCursor(each)
    for row in cursor:
        row.setValue("zoneID", str(zoneIDlist[i]))
        cursor.updateRow(row)
        i = i + 1

    # Add country name, code and energy source
    arcpy.AddField_management(each, "Energy_Source", "Text")
    arcpy.CalculateField_management(each, "Energy_Source", "'{}'".format(technology))
    arcpy.AddField_management(each, "Country", "Text")
    country = each.split("_")[0]
    arcpy.CalculateField_management(each, "Country", "'{}'".format(country))
    arcpy.AddField_management(each, "CountryCode", "Text")
    country_code = countries.get(country)
    arcpy.CalculateField_management(each, "CountryCode", "'{}'".format(country_code))
    arcpy.AddField_management(each, "SAPPzoneID", "Text")
    arcpy.CalculateField_management(each, "SAPPzoneID", "'{}_{}'".format(country, country_code))


outputfilename = scenario + "_" + technology + "_finalOutput"
scenarioCountries = arcpy.Merge_management(featureclasses, outputfilename)

arcpy.AlterField_management(outputfilename, "SUM_egen", "Egen")
arcpy.AlterField_management(outputfilename, "SUM_incap", "Incap")
arcpy.AlterField_management(outputfilename, "SUM_d_road_weighted", "D Road")
arcpy.AlterField_management(outputfilename, "SUM_d_water_weighted", "D Water")
arcpy.AlterField_management(outputfilename, "SUM_m_elev_weighted", "M Elev")
arcpy.AlterField_management(outputfilename, "SUM_m_slope_weighted", "M Slope")
arcpy.AlterField_management(outputfilename, "SUM_m_popden_weighted", "M Popden")
arcpy.AlterField_management(outputfilename, "SUM_m_humfoot_weighted", "M Humfoot")
arcpy.AlterField_management(outputfilename, "SUM_m_cf_weighted", "M Cf")
arcpy.AlterField_management(outputfilename, "SUM_l_road_weighted", "L Road")
arcpy.AlterField_management(outputfilename, "SUM_l_gen_weighted", "L gen")
arcpy.AlterField_management(outputfilename, "SUM_d_trans_weighted", "D Trans")
arcpy.AlterField_management(outputfilename, "SUM_d_rail_weighted", "D Rail")
arcpy.AlterField_management(outputfilename, "SUM_d_anyre_weighted", "D Anyre")
arcpy.AlterField_management(outputfilename, "SUM_d_airport_weighted", "D Air")
arcpy.AlterField_management(outputfilename, "SUM_m_resource_weighted", "M Resource")
arcpy.AlterField_management(outputfilename, "SUM_m_lulc_weighted", "M Lulc")
arcpy.AlterField_management(outputfilename, "SUM_m_rangeland_weighted", "M Rangeland")
arcpy.AlterField_management(outputfilename, "SUM_l_tra_weighted", "L Tra")
arcpy.AlterField_management(outputfilename, "SUM_lt_tra_weighted", "Lt Tra")


print(arcpy.GetMessages())
