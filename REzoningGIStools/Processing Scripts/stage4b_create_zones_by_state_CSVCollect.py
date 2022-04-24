
import arcpy
import pandas as pd

import import_functions.stage4_clustering_fishnet_function as stage4_clustering_fishnet

arcpy.env.overwriteOutput = True

csv_file = pd.read_csv(r"D:\mmeng\mapre\RequiredCSVs\stage4_input_india_solar.csv", header=None)

# arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_solar.gdb"
arcpy.env.workspace = workspace = str(csv_file[1][1])
resource = str(csv_file[1][0])
zonesclasses = arcpy.ListFeatureClasses("*_areas_attr_100km_zones")

outputfile = str(csv_file[1][1]) + "\\india_zones_combined_100km"
out_xls = "D:\mmeng\mapre\\india_combined_zones_solar_20220419_100km.xlsx"

print(workspace)
print(zonesclasses)
print(outputfile)

for i in range(len(zonesclasses)):

    country = zonesclasses[i]

    print("Starting : " + country)

    arcpy.DeleteField_management(country, "Lat")
    arcpy.DeleteField_management(country, "Lon")

    arcpy.AddField_management(country, "Lat", "DOUBLE")
    arcpy.AddField_management(country, "Lon", "DOUBLE")

    expressiony = 'arcpy.PointGeometry(!Shape!.centroid,!Shape!.spatialReference).projectAs(arcpy.SpatialReference(4326)).centroid.Y'
    arcpy.CalculateField_management(country, "Lat", expressiony, "PYTHON_9.3")

    expressionx = 'arcpy.PointGeometry(!Shape!.centroid,!Shape!.spatialReference).projectAs(arcpy.SpatialReference(4326)).centroid.X'
    arcpy.CalculateField_management(country, "Lon", expressionx, "PYTHON_9.3")

    # arcpy.CalculateField_management(country, "Lon", "!SHAPE.CENTROID.X!", "PYTHON_9.3")
    # arcpy.CalculateField_management(country, "Lat", "!SHAPE.CENTROID.Y!", "PYTHON_9.3")

    arcpy.AddField_management(country, "state_abbrv", "TEXT")
    arcpy.AddField_management(country, "state_zone", "TEXT")
    # arcpy.DeleteField_management(country, "state_abrv")

    cur = arcpy.UpdateCursor(country)

    for row in cur:
        row.setValue("state_abbrv", country[:2])
        row.setValue('state_zone', row.getValue('state_abbrv') + '_' + row.getValue('zoneID'))
        cur.updateRow(row)

arcpy.Merge_management(zonesclasses, outputfile)

# Execute TableToExcel
arcpy.TableToExcel_conversion(outputfile, out_xls)