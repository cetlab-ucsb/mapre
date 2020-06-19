import arcpy

arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"

################################################################################
# RUN SKATER

in_features = ["wind_0_skater_clustered", "wind_0_botswana_skater_clustered"]

arcpy.Merge_management(in_features, "joined_output")