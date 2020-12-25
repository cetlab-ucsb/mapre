
import arcpy
import stage4_clustering_fishnet
arcpy.env.overwriteOutput = True

arcpy.env.workspace = workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_solar.gdb"
resource = "solar"
featureclasses = arcpy.ListFeatureClasses("*_areas_attr")
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

    templateRaster = r"R:\users\anagha.uppal\MapRE" + "\\SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required
    scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb"
    fishnetSize = 25  ## in km

    fields_to_sum_cluster = ["egen", "incap"]  # original field values summed for final clusters/zones
    fields_to_average_cluster = ["d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_humfoot", "m_cf",
                                 "l_road", "l_gen", "d_trans", "d_rail", "d_anyre", "d_airport",
                                 "m_resource", "m_rangeland", "l_tra", "j_lulc", "c_coloc",
                                 "lt_tra"]  # original fields averaged for final clusters/zones

    analysis = stage4_clustering_fishnet.ClusterTime(workspace, scratch, in_features, output_features,
                                                     templateRaster, fishnetSize, fields_to_sum_cluster,
                                                     fields_to_average_cluster)
    analysis.clusterProjectZones()


for i in range(len(featureclasses)):
    country = featureclasses[i]
    print("Starting " + country)
    run_it(country)
    print("Finished " + country)