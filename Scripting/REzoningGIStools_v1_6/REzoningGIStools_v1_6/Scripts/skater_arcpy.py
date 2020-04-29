import arcpy
import math

arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"

in_features = "wind_0_suitability_areas_attr"
numFeatures = arcpy.GetCount_management(in_features)
numClusters = math.ceil(float(numFeatures[0])/300)
output_features = "wind_0_skater"
analysis_fields = ["m_cf"]
size_constraints = "NONE"
constraint_field = None
min_constraint = None
max_constraint = None
#number_of_clusters = None
number_of_clusters = numClusters
print("Number of clusters to be created = ", number_of_clusters)
spatial_constraints = "TRIMMED_DELAUNAY_TRIANGULATION"
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
out_feature_class = in_features + "_clustered"
dissolve_field = "CLUSTER_ID"

arcpy.Dissolve_management(in_features, out_feature_class, dissolve_field)