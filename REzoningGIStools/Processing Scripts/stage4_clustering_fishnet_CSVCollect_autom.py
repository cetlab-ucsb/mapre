
import arcpy
import pandas as pd
import math

import import_functions.stage4_clustering_fishnet_function as stage4_clustering_fishnet

arcpy.env.overwriteOutput = True

csv_file = pd.read_csv(r"D:\mmeng\mapre\RequiredCSVs\stage3_input_india_wind.csv", header=None)

# arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_solar.gdb"
arcpy.env.workspace = workspace = str(csv_file[1][1])
resource = str(csv_file[1][0])
# featureclasses = arcpy.ListFeatureClasses("*_areas_attr")
featureclasses = [fc for fc in arcpy.ListFeatureClasses("*_areas_attr") if not ("fishnet_" in fc)]
print(workspace)
print(featureclasses)

def run_it(countryName):
    '''
    ############################################################################################################
    ## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
    ############################################################################################################
    '''

    #####################
    ## USER SET INPUTS ##
    #####################

    in_features = countryName
    output_features = countryName + "_zones"

    # templateRaster = r"R:\users\anagha.uppal\MapRE" + "\\SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required
    # scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb"
    templateRaster = str(csv_file[1][5])  ## required
    scratch = str(csv_file[1][6])
    fishnetSize = math.sqrt(float(csv_file[1][10]))  ## in km

    fields_to_sum_cluster = ["egen", "incap"]  # original field values summed for final clusters/zones

    fields_to_average_cluster = ["d_sub", "d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_cf",
                                 "l_road", "l_gen", "l_tra", "j_lulc", "c_coloc", "lt_tra",
                                 "lt_sub", "m_cf_noloss"]  # original fields averaged for final clusters/zones

    # fields_to_average_cluster = ["d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_humfoot", "m_cf",
    #                              "l_road", "l_gen", "d_trans", "d_rail", "d_anyre", "d_airport",
    #                              "m_resource", "m_rangeland", "l_tra", "j_lulc", "c_coloc",
    #                              "lt_tra"]  # original fields averaged for final clusters/zones

    analysis = stage4_clustering_fishnet.ClusterTime(workspace, scratch, in_features, output_features,
                                                     templateRaster, fishnetSize, fields_to_sum_cluster,
                                                     fields_to_average_cluster)
    analysis.clusterProjectZones()


for i in range(len(featureclasses)):
    country = featureclasses[i]
    print("Starting " + country)
    if str(arcpy.GetCount_management(country)) == "0":
        print("Skipping because 0 rows")
        continue
    run_it(country)
    print("Finished " + country)

# combine all zones into single feature class

# zonesclasses = arcpy.ListFeatureClasses("*_areas_attr_zones")
# combinedoutput = str(csv_file[1][1]) + "\\india_zones_combined"
#
# print(zonesclasses)
#
# for i in range(len(zonesclasses)):
#
#     country = zonesclasses[i]
#
#     print("Starting : " + country)
#
#     arcpy.AddField_management(country, "state_abbrv", "TEXT")
#     arcpy.AddField_management(country, "state_zone", "TEXT")
#
#     cur = arcpy.UpdateCursor(country)
#
#     for row in cur:
#         row.setValue("state_abbrv", country[:2])
#         row.setValue('state_zone', row.getValue('state_abbrv') + '_' + row.getValue('zoneID'))
#         cur.updateRow(row)
#
# arcpy.Merge_management(zonesclasses, combinedoutput)
