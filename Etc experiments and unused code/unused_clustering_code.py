import geopandas as gpd

# with columns "id", "latitude", "longitude" - 10k records
df

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"],
    ),
    crs={"init":"EPSG:4326"},
)

# 10 records
filtered_df

filtered_gdf = gpd.GeoDataFrame(
    filtered_df,
    geometry=gpd.points_from_xy(
        filtered_df["longitude"],
        filtered_df["latitude"],
    ),
    crs={"init":"EPSG:4326"},
)

# EPSG:3857 converts it to meters, correct?

gdf_proj = gdf.to_crs({"init": "EPSG:3857"})
filtered_gdf_proj = filtered_gdf.to_crs({"init": "EPSG:3857"})

# so 100 miles would be 160934 meters

x = filtered_gdf_proj.buffer(160934).unary_union

neighbours = gdf_proj["geometry"].intersection(x)

# print all the nearby points
print(gdf_proj[~neighbours.is_empty])



## ---------------------------------------------------------------------------------------------------
## ------------------------------- ITERATION 2 -------------------------------------------------------
## ---------------------------------------------------------------------------------------------------

# #############################################
# ## SELECT ZONES TO CLUSTER IN ITERATION 2  ##
# #############################################
#
## select zones greater than maximum zone size resulting from iteration 1 for clustering:
selectZone_it2 = arcpy.Select_analysis(out_feature_class, "iteration2", \
                                       '"Shape_Area" >= ' + str(max_constraint))

##################################################
## ARE THERE ZONES TO CLUSTER IN ITERATION 2??  ##
##################################################

########
## NO ##
########

# check if there are any zones above max clustered area:
## if not, then project the iteration 1 outputFile
if int(arcpy.management.GetCount(selectZone_it2)[0]) == 0:

    #################################################
    ## PROJECT OUTPUT AND CALCULATE GROUPVAL FIELD ##
    #################################################
    print("There are no clustered areas greater than " + str(max_constraint))
    # Anagha: why the need to project file?
    # dsc = arcpy.Describe(projectFile)
    # coord_sys = dsc.spatialReference
    # arcpy.DefineProjection_management(outputFilename, coord_sys)
    # print("Projected output")

    ## create unique identification codes for newly clustered zones using "clustered_" from R and putting it under the "GroupVal" Field
#     arcpy.CalculateField_management(outputFilename, "GroupVal",
#                                     "str(!ZONE_ID!) + '.' + str(!iteration!) + '.' + str(int(!clustered_!))",
#                                     "PYTHON_9.3")
#
#     arcpy.CopyFeatures_management(outputFilename, outputFilename[:-4] + "_merged.shp")


#########
## YES ##
#########

  else:
    print("-----------> Begin iteration 2")

    ## Anagha: what's the need for this part?
    ## Anagha: you used buffers to separate and not fishnet
    ###############################################
    ## SET ASIDE ZONES CLUSTERED IN ITERATION 1  ##
    ###############################################
    # select zones that have been clustered (iteration 1):
    outputFilename_it1 = arcpy.Select_analysis(out_feature_class, "iteration1.shp", \
      '"Shape_Area" < ' + str(max_constraint))

    #################################################
    ## DELETE FIELDS THAT WILL BE CALCULATED AGAIN ##
    #################################################

    # arcpy.DeleteField_management(selectZone_it2, ["clustered_", "SUM_Area_1", "COUNT_Area"])
#     ################################
#


    iteration2_clusteredList =[] ## list that holds all the clustered areas in iteration 2

    cursor_2 = arcpy.SearchCursor(selectZone_it2)
    origIDs = []
    for row in cursor_2:
      orig = row.getValue("Cluster ID")
      origIDs.append(orig)
    zoneIDs_2 = set(origIDs).tolist() ## get unique zone IDs that require clustering



    '''
    #################################################
    ## Check for fishnet file and create if needed ##
    #################################################
    '''

    fishnet = "in_memory/fishnet_" + str(max_constraint) \
              + "km"  ## MUST add .shp if not putting file in gdb (for add field function)
    # clippedFishnet = self.fishnetDirectory + "\\" + "fishnet_" + str(max_constraint) + "km"

    clippedFishnet = "fishnet_" + str(max_constraint) + "km"
    arcpy.env.outputCoordinateSystem = out_feature_class
    if not (arcpy.Exists(clippedFishnet)):
        # Create fishnet if one does not already exist:
        arcpy.AddMessage("Creating fishnet " + str(max_constraint) + " km in size to file: " + fishnet)

        # extent = arcpy.Raster(self.templateRaster).extent
        extent = out_feature_class.extent

        XMin = extent.XMin  ## left

        YMin = extent.YMin  ## Bottom

        origin = str(XMin) + " " + str(YMin)

        YMax = extent.YMax  ## top

        ycoord = str(XMin) + " " + str(YMax)
        # Anagha? Is this the right fishnet size? = max_constraint?
        arcpy.CreateFishnet_management(fishnet, origin, ycoord,
                                       max_constraint * 1000, max_constraint * 1000,
                                       '0', '0', "", "NO_LABELS", "#", "POLYGON")

        fields = arcpy.ListFields(fishnet)
        for field in fields:
            arcpy.AddMessage(field.name)
        # Change fishnet Object ID name:
        arcpy.AddField_management(fishnet, "Text", "Text", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        # Process: Calculate Field to create new alphanumeric OID column
        arcpy.CalculateField_management(fishnet, "Text", "'A' + str(!OID!)", "PYTHON_9.3", "")

        arcpy.AddMessage("Creating country-boundary-clipped fishnet " + str(max_constraint)
                         + " km in size to file: " + clippedFishnet)
        #arcpy.Clip_analysis(fishnet, self.countryBounds, clippedFishnet)

    arcpy.AddMessage("Copying fishnet to memory :" + clippedFishnet)
    fishnetInMemory = arcpy.CopyFeatures_management(clippedFishnet, "in_memory/clipped_fishnet")

    IntermediateIntersect = "in_memory/IntermediateIntersect_2"
    IntermediateIntersect_singlept = "in_memory/IntermediateIntersect_singlept"
    # Anagha? Can I start the cursor here?
    for row in cursor_2:
        # Intersect regions above max area using fishnet
        arcpy.AddMessage("Intersecting by fishnet")
        arcpy.Intersect_analysis([selectZone_it2, fishnetInMemory], IntermediateIntersect, "NO_FID")
        arcpy.AddMessage("finished intersecting by fishnet")
        # Process: Calculate Area
        arcpy.CalculateField_management(IntermediateIntersect, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3",
                                        "")

        '''
        ################################
        ## Create singlepart polygons ##
        ################################
        '''
        ## Multi-part to single part
        arcpy.MultipartToSinglepart_management(in_features=IntermediateIntersect,
                                               out_feature_class=IntermediateIntersect_singlept)
        ## Recalculate area
        arcpy.CalculateField_management(IntermediateIntersect_singlept, "Area", "!Shape.Area@squarekilometers!",
                                        "PYTHON_9.3", "")
        '''
        ###############################
        ## Eliminate slivers - twice ##
        ###############################
        '''
        arcpy.AddMessage("Starting elimination")
        # Execute MakeFeatureLayer
        tempLayer = arcpy.MakeFeatureLayer_management(IntermediateIntersect_singlept, "tempLayer")
        # Anagha? Does this apply? Should we eliminate slivers or they should also be combined with other polygons?
        # Is there any benefit to eliminating slivers, why was that done last time?
        # last time around, shouldn't the small slivers have been combined with other polygons?

        # # Execute SelectLayerByAttribute to define features to be eliminated
        # arcpy.SelectLayerByAttribute_management(in_layer_or_view=tempLayer, selection_type="NEW_SELECTION",
        #                                         where_clause=self.whereClauseMin)
        #
        # # Execute Eliminate
        # arcpy.Eliminate_management("tempLayer", IntermediateEliminated, "LENGTH")

        ## iteration 2

        # Execute MakeFeatureLayer
        IntermediateEliminated_tempLayer = arcpy.MakeFeatureLayer_management(IntermediateEliminated,
                                                                             "IntermediateEliminated")

        # Execute SelectLayerByAttribute to define features to be eliminated
        arcpy.SelectLayerByAttribute_management(in_layer_or_view=IntermediateEliminated_tempLayer,
                                                selection_type="NEW_SELECTION", where_clause=self.whereClauseMin)

        # Execute Eliminate
        arcpy.Eliminate_management(IntermediateEliminated_tempLayer, IntermediateEliminated2, "LENGTH")

        ### NOW run skater again on these
        # Anagha? Will the adding and subtracting of areas from clusters happen before or after skater?

#########################################################################################

# in_features = out_feature_class
# output_features = in_features+"_skater"
# analysis_fields = ["m_cf"]
# size_constraints = "ATTRIBUTE_VALUE"
# constraint_field = "Shape_Area"
# min_constraint = None
# max_constraint = 100000000
# number_of_clusters = None
# #number_of_clusters = numClusters
# #print("Number of clusters to be created = ", number_of_clusters)
# spatial_constraints = "TRIMMED_DELAUNAY_TRIANGULATION"
# weights_matrix_file = None
# number_of_permutations = 0
#
# SpatiallyConstrainedMultivariateClustering(in_features, output_features, analysis_fields, {size_constraints},
#                                            {constraint_field}, {min_constraint}, {max_constraint},
#                                            {number_of_clusters}, {spatial_constraints}, {weights_matrix_file},
#                                            {number_of_permutations})
#
#
# ##################################################################################
# # Area of each cluster in km^2
# # SHAPE_AREA / 1000000
#
# # Set local variables
# inFeatures = out_feature_class
# fieldName = "ClusterArea"
# fieldAlias = "Cluster Area"
# fieldType = "DOUBLE"
#
# # Add field clusterarea
# arcpy.AddField_management(in_table=inFeatures, field_name=fieldName, field_alias=fieldAlias, field_type=fieldType)
# print(arcpy.GetMessages())
#
# ## Calculate field clusterarea
# arcpy.CalculateField_management(inFeatures, fieldName,
#                                 "!Shape_Area!/1000000", "PYTHON3")
# print(arcpy.GetMessages())
#
#
# ##################################################################################
# # Columns for Country + Resource
#
# # Set local variables
# fieldName1 = "Country"
# fieldName2 = "Resource"
# fieldType = "TEXT"
#
# # Execute AddField twice for two new fields
# arcpy.AddField_management(in_table=inFeatures, field_name=fieldName1, field_type=fieldType)
# arcpy.AddField_management(in_table=inFeatures, field_name=fieldName2, field_type=fieldType)
# print(arcpy.GetMessages())
#
# ## Fill fields
#
# arcpy.CalculateField_management(inFeatures, field="Country",
#                                 expression='"{}"'.format(country), expression_type="PYTHON3")
# arcpy.CalculateField_management(inFeatures, field="Resource",
#                                 expression='"{}"'.format(resource), expression_type="PYTHON3")
# print(arcpy.GetMessages())


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