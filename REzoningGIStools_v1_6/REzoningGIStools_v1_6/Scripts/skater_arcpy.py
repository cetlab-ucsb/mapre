import arcpy

arcpy.SpatiallyConstrainedMultivariateClustering_stats(in_features, output_features, analysis_fields,
                                           {size_constraints}, {constraint_field}, {min_constraint},
                                                 {max_constraint}, {number_of_clusters}, {spatial_constraints},
                                                 {weights_matrix_file}, {number_of_permutations}, output_table)