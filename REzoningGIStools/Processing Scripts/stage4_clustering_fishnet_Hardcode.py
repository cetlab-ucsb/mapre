import stage4_clustering_fishnet
import arcpy
arcpy.env.overwriteOutput = True


workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_solar.gdb" # req - folder containing output of stage 3
in_features = "Angola_areas_attr" ## required - output of stage 3

templateRaster = r"R:\users\anagha.uppal\MapRE" + "\\SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required - retain same raster file (e.g. DEM data) across stages, runs and total region of analysis
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb" ## required - scratch GDB
fishnetSize = 25  ## in km

fields_to_sum_cluster = ["egen", "incap"] # original field values summed for final clusters/zones
fields_to_average_cluster = ["d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_humfoot", "m_cf",
                                 "l_road", "l_gen", "d_trans", "d_rail", "d_anyre", "d_airport",
                                 "m_resource", "m_rangeland", "l_tra", "j_lulc", "c_coloc",
                                 "lt_tra"] # original fields averaged for final clusters/zones

############################DO NOT EDIT BELOW THIS LINE#########################################
output_features = in_features + "_zones"
analysis = stage4_clustering_fishnet.ClusterTime(workspace, scratch, in_features, output_features,
                                                 templateRaster, fishnetSize, fields_to_sum_cluster,
                                                 fields_to_average_cluster)
analysis.clusterProjectZones()