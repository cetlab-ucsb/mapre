import arcpy

arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"

in_features = "solarPV_2_suitability_lulcenvslopelev_areas_attr"
output_features = "solarPV_2_suitability_lulcenvslopelev_c"
analysis_fields = ["d_water"]
size_constraints = "NONE"
constraint_field = None
min_constraint = None
max_constraint = None
number_of_clusters = None
spatial_constraints = "CONTIGUITY_EDGES_CORNERS"
weights_matrix_file = None
number_of_permutations = 0
output_table = "numClusters"

arcpy.SpatiallyConstrainedMultivariateClustering_stats(in_features, output_features, analysis_fields,
                                                       size_constraints, constraint_field, min_constraint,
                                                       max_constraint, number_of_clusters, spatial_constraints,
                                                       weights_matrix_file, number_of_permutations, output_table)
print(arcpy.GetMessages())

# Dissolve cluster results

in_features = output_features
out_feature_class = in_features + "lustered"
dissolve_field = "CLUSTER_ID"

arcpy.Dissolve_management(in_features, out_feature_class, dissolve_field)