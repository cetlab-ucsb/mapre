import arcpy
import math
import arcpy
import os
########INPUTS###########

arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"
in_features = "wind_0_suitability_areas_attr"
output_features = "wind_0_skater"
country = "South Africa"
resource = "Wind"
min_constraint = 25.000000 #in km
max_constraint = 500.000000 #in km
# distance_between_projects = 20 #in
buff_width = "2550 meters"
fields_to_sum_cluster = ["egen"]
fields_to_average_cluster = ["d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_humfoot", "m_cf",
                             "incap", "l_road", "l_gen"]

################################################################################
# RUN SKATER

# #^^buffering width in meters:
sideType = "FULL"
endType = "ROUND"
dissolveType = "ALL"
projectFileName = "projects1"
# outputFolder = "R:\\users\\anagha.uppal\\MapRE\\"
# gdbName = "test1.gdb\\" ## ^^ Name of the fgdb to store outputs
# gdbNameForCreatingFGDB = "test1.gdb" ## ^^ here re-write the name of the file geodatabase
# if not(os.path.exists(outputFolder + gdbName)): # Create new fgdb if one does not already exist
#     print(gdbName + " does not exist. Ensure you have selected the right date's resource potential feature class")

# outputFGDB = outputFolder + gdbName # sets workspace as your fgdb

# ## 1. Buffering projects
# ## create buffers:
buffProjects = arcpy.Buffer_analysis(in_features, "in_memory/zoneBuffer", buff_width, sideType, endType, dissolveType)
print("finished buffering")
## form different rows for each discontinous polygon using multipart (polygon with disjointed pieces) to singlepart
## (no disjointed pieces):
intermediate = arcpy.MultipartToSinglepart_management(buffProjects, "in_memory/zoneIntermediate_buffering")
## add field and calculate field to identify each zone to the buttered layer:
arcpy.AddField_management(intermediate, "ZONE_ID", "LONG")
arcpy.CalculateField_management(intermediate, "ZONE_ID", "!OBJECTID!", "PYTHON_9.3")
## join original projects with buffered zones, thus adding ORIG_ID to the projects table
joined = arcpy.SpatialJoin_analysis(in_features, intermediate, "in_memory/" + "zoneJoined", "JOIN_ONE_TO_ONE", "")
# calculate stats for each zone using ZONE_ID to group projects
stats = arcpy.Statistics_analysis(joined, "in_memory/zoneIntermediate_Stats", [["Area", "SUM"], ["Area", "COUNT"]],
                                  "ZONE_ID")
# # add the stats table to the original project file to get zone stats:
arcpy.JoinField_management(joined, "ZONE_ID", stats, "ZONE_ID", "")
# ## since the above causes ZONE_ID_1 to be created, delete it:
arcpy.DeleteField_management(joined, "ZONE_ID_1")
#
# ## 2. Separate large zones from small zones
# # Select projects that are below minimum zone size threshold and save it as _smallAreas
arcpy.AddField_management(joined, "GroupVal", "Text", field_length=20)

tooSmall = arcpy.Select_analysis(joined, "tooSmallforZoning",
                                 '"SUM_Area" < ' + str(min_constraint))
smallZones = arcpy.Select_analysis(joined, "smallZones",
                                   '"SUM_Area" < ' + str(max_constraint) + ' and "SUM_Area" >= ' + str(min_constraint))

arcpy.CalculateField_management(smallZones, "GroupVal", "!ZONE_ID!", "PYTHON_9.3")
aboveMax = arcpy.Select_analysis(joined, "zones_forGrouping",
                                 '"SUM_Area" >=' + str(max_constraint))  ## projects that require clustering

print("Begin clustering analysis")

##########################################################################

# #test in_memory
# #1: Buffer analysis: No dissolve, 20km radius
# print("Buffering")
# if not arcpy.Exists(in_features+"_buffer"):
#     arcpy.Buffer_analysis(in_features, in_features+"_buffer", str(distance_between_projects)+" Kilometers",
#        line_side="FULL", dissolve_option="NONE",)
# # Spatial join target original, join original: this tells us how many polygons within a 20km radius of each polygon
# print("Spatially joining features with buffers")
#
# arcpy.AddField_management(in_features, "ID_Comb", "TEXT", field_length=4000,)
#
# # Create a new fieldmappings and add the two input feature classes.
# fieldmappings = arcpy.FieldMappings()
# fieldmappings.addTable(in_features)
# fieldmappings.addTable(in_features+"_buffer")
# # we'll work to create ID_comb
# IDFieldIndex = fieldmappings.findFieldMapIndex("ID_Comb")
# fieldmap = fieldmappings.getFieldMap(IDFieldIndex)
#
# # Get the output field's properties as a field object
# field = fieldmap.outputField
#
# # Set the merge rule to join and then replace the old fieldmap in the mappings object
# # with the updated one
# fieldmap.mergeRule = "join"
# fieldmap.joinDelimiter = ","
# # source add
# fieldmap.addInputField(in_features, "OBJECTID")
# fieldmap.addInputField(in_features+"_buffer", "OBJECTID")
# fieldmappings.replaceFieldMap(IDFieldIndex, fieldmap)
#
# # Delete fields that are no longer applicable
# # x = fieldmappings.findFieldMapIndex("CITY_NAME")
# # fieldmappings.removeFieldMap(x)
#
# # Run the Spatial Join tool, using the defaults for the join operation and join type
# # Spatial join target original, join buffer: this tells us how many polygons within a 20km radius of each polygon
# arcpy.SpatialJoin_analysis(target_features=in_features, join_features=in_features+"_buffer",
#                            out_feature_class=in_features+"_sj", join_operation="JOIN_ONE_TO_ONE",
#                            join_type="KEEP_ALL", field_mapping=fieldmappings, match_option="INTERSECT",)
# # arcpy.SpatialJoin_analysis(target_features=in_features, join_features=in_features,
# #                            out_feature_class=in_features+"_sj", join_operation="JOIN_ONE_TO_ONE",
# #                            join_type="KEEP_ALL", match_option="INTERSECT",
# #                            search_radius=str(distance_between_projects)+" Kilometers")
# print(arcpy.GetMessages())
#
# print("Bringing join_count back to features")
# arcpy.JoinField_management(in_data=in_features, in_field="OBJECTID",
#                            join_table=in_features+"_sj", join_field="OBJECTID",
#                            fields=["Join_Count", "ID_Comb"])
# print("Creating field sum_area")
# arcpy.AddField_management(in_features, "Area_Sum", "DOUBLE", field_length=150,)
# arcpy.CalculateField_management(in_table=in_features, field="Area_Sum", expression="!Shape_Area!")
#
# records = arcpy.GetCount_management(in_features)
# rows = arcpy.UpdateCursor(in_features)
# for row in rows:
#     print(row.getValue("ID_Comb"))
#     list = row[i]
#     rVal = row.getValue(field.name)
# # loop through all in in_features
# for i in range(len(records)):
#     list = in_features[i]["ID_Comb"]
#     for x in list:
#         if not x == i:
#             in_features[i]["Sum_Area"] += in_features[x]["Shape_Area"]
#
#
# print(arcpy.GetMessages())
#
# print("Separating isolated projects")
# # What is faster, cursor with if or select_management?
# arcpy.Select_analysis(in_features, "separated_projects",
#                       where_clause='"Join_Count" = 1 And "Shape_Area" > ' + str(min_constraint))
# print(arcpy.GetMessages())
# print("Grabbing cluster-relevant projects")
# skater_features = "skater_features"
# arcpy.Select_analysis(in_features, skater_features, where_clause='"Join_Count" > 1')
# # cursor = arcpy.UpdateCursor(in_features2, ["OBJECTID", "Join_Count", "Shape_Area"])
# # for row in cursor:
# #     # IF join_count = 1:
# #         # Go back to object ID of original polygon
# #         # If area < 25km2: delete_management
# #         # else: select (add to selection) and separate. Later you'll add it back to the skater zones
# #     nearPolygons = row[1] # value at Join_Count
# #     if nearPolygons == 1:
# #         # if row[2] < min_constraint:
# #         cursor.deleteRow()
#merge separated projects

# numFeatures = arcpy.GetCount_management(in_features)
# numClusters = math.ceil(float(numFeatures[0])/300)

analysis_fields = ["m_cf"]

size_constraints = "ATTRIBUTE_VALUE"
constraint_field = "Shape_Area"
min_constraint = min_constraint*1000000
max_constraint = max_constraint*1000000

# size_constraints = "NONE"
# constraint_field = None
# min_constraint = None
# max_constraint = None


number_of_clusters = None
#number_of_clusters = numClusters
#print("Number of clusters to be created = ", number_of_clusters)
spatial_constraints = "TRIMMED_DELAUNAY_TRIANGULATION"
weights_matrix_file = None
number_of_permutations = 0


###################################################################

# arcpy.SpatiallyConstrainedMultivariateClustering_stats("zones_forGrouping", output_features, analysis_fields,
#                                                        size_constraints, constraint_field, min_constraint,
#                                                        max_constraint, number_of_clusters, spatial_constraints,
#                                                        weights_matrix_file, number_of_permutations)
#
# print(arcpy.GetMessages())
#
# # Dissolve cluster results
#
# in_features = output_features
# out_feature_class = in_features + "_clustered"
# dissolve_field = "CLUSTER_ID"
#
# arcpy.Dissolve_management(in_features, out_feature_class, dissolve_field,
#                           statistics_fields=[["m_cf", "SUM"], ["m_cf", "MEAN"]])
# print(arcpy.GetMessages())
#Merge previously pulled out projects
# arcpy.Merge_management([out_feature_class, "separated_projects"],
#                        "all_zones", field_mappings="")
###### Field_Mappings!?

##############################################################
zoneList = [row.getValue("ZONE_ID") for row in arcpy.SearchCursor("zones_forGrouping","","","ZONE_ID")]
frqDict = {}
for s in zoneList:
    if not s in frqDict:
        frqDict[s] = 1
    else:
        frqDict[s] = frqDict[s] + 1
for i in range(len(frqDict)):
    cluster = arcpy.MakeFeatureLayer_management("zones_forGrouping","cluster"+str(i),
                                                """ "ZONE_ID" = {} """.format(list(frqDict)[i]))
    arcpy.SpatiallyConstrainedMultivariateClustering_stats(cluster, output_features + str(i), analysis_fields,
                                                           size_constraints, constraint_field, min_constraint,
                                                           max_constraint, number_of_clusters, spatial_constraints,
                                                           weights_matrix_file, number_of_permutations)
    print(arcpy.GetMessages())

    arcpy.JoinField_management(output_features+str(i), "OBJECTID", cluster, "OBJECTID")

    statsFields = []
    for each in fields_to_sum_cluster:
        fieldStatement = [each, "SUM"]  ##
        statsFields.append(fieldStatement)

    for each in fields_to_average_cluster:
        arcpy.AddField_management(in_table=output_features+str(i),
                                  field_name=each+"_weighted", field_type="DOUBLE")
        condition = """!{}!*!Shape_Area!""".format(each)
        arcpy.CalculateField_management(output_features+str(i), each+"_weighted", condition)
        fieldStatement = [each+"_weighted", "SUM"]  ##
        statsFields.append(fieldStatement)

    # Dissolve cluster results
    in_features = output_features+str(i)
    out_feature_class = output_features + "_clustered"+str(i)
    dissolve_field = "CLUSTER_ID"
    arcpy.Dissolve_management(in_features, out_feature_class, dissolve_field,
                          statistics_fields=statsFields)
    print(arcpy.GetMessages())
    for each in fields_to_average_cluster:
        condition = """!{}!/!Shape_Area!""".format("SUM_"+each+"_weighted")
        arcpy.CalculateField_management(output_features + "_clustered"+str(i), "SUM_"+each+"_weighted", condition)

##########################################################################

# Merge all clusters projects
clusterList = []
for i in range(len(frqDict)):
    clusterList.append(out_feature_class[:-1]+str(i))
print(clusterList)
arcpy.Merge_management(clusterList, out_feature_class[:-1])
print(arcpy.GetMessages())










