
import arcpy
from itertools import count, product, islice
import pandas as pd
# import stage2_function
import numpy

arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers.gdb"

featureclasses = arcpy.ListFeatureClasses("*_areas_attr")
print(featureclasses)

def multiletters(seq):
    for n in count(1):
        for s in product(seq, repeat=n):
            yield ''.join(s)

def run_it(countryName):
    ########INPUTS###########
    in_features = countryName
    output_features = countryName+"_5_5_skater"
    country = countryName.split("_")[0]
    resource = "solarPV"
    min_constraint = 25.000000  # cluster to be no less than this area in km
    max_constraint = 500.000000  # cluster to be no larger than this area in km
    # distance_between_projects = 20 #in
    buff_width = "2550 meters"  # acceptable distance between projects in a single zone
    fields_to_sum_cluster = ["egen", "incap"]  # original field values summed for final clusters/zones
    fields_to_average_cluster = ["d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_humfoot", "m_cf",
                                 "l_road", "l_gen", "d_trans", "d_rail", "d_anyre", "d_airport",
                                 "m_resource", "m_lulc", "m_rangeland", "l_tra",
                                 "lt_tra"]  # original fields averaged for final clusters/zones
    analysis_fields = ["m_cf"]  # field on which to cluster projects: capacity factor or resource quality

    ################################################################################
    # RUN SKATER

    # #^^buffering width in meters:
    sideType = "FULL"
    endType = "ROUND"
    dissolveType = "ALL"

    # ## 1. Buffering projects
    # ## create buffers:
    buffProjects = arcpy.Buffer_analysis(in_features, "in_memory/zoneBuffer", buff_width, sideType, endType,
                                         dissolveType)
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
                                       '"SUM_Area" < ' + str(max_constraint) + ' and "SUM_Area" >= ' + str(
                                           min_constraint))

    arcpy.CalculateField_management(smallZones, "GroupVal", "!ZONE_ID!", "PYTHON_9.3")
    aboveMax = arcpy.Select_analysis(joined, "zones_forGrouping",
                                     '"SUM_Area" >=' + str(max_constraint))  ## projects that require clustering

    print("Begin clustering analysis")

    ##########################################################################

    size_constraints = "ATTRIBUTE_VALUE"
    constraint_field = "Shape_Area"
    min_constraint = min_constraint * 1000000
    max_constraint = max_constraint * 1000000

    number_of_clusters = None
    # number_of_clusters = numClusters
    # print("Number of clusters to be created = ", number_of_clusters)
    spatial_constraints = "TRIMMED_DELAUNAY_TRIANGULATION"
    weights_matrix_file = None
    number_of_permutations = 0

    ##############################################################
    zoneList = [row.getValue("ZONE_ID") for row in arcpy.SearchCursor("zones_forGrouping", "", "", "ZONE_ID")]
    frqDict = {}
    for s in zoneList:
        if not s in frqDict:
            frqDict[s] = 1
        else:
            frqDict[s] = frqDict[s] + 1
    print("Running SKATER {} times".format(frqDict))
    for i in range(len(frqDict)):
        cluster = arcpy.MakeFeatureLayer_management("zones_forGrouping", "cluster" + str(i),
                                                    """ "ZONE_ID" = {} """.format(list(frqDict)[i]))
        arcpy.SpatiallyConstrainedMultivariateClustering_stats(cluster, output_features + str(i), analysis_fields,
                                                               size_constraints, constraint_field, min_constraint,
                                                               max_constraint, number_of_clusters, spatial_constraints,
                                                               weights_matrix_file, number_of_permutations)
        print(arcpy.GetMessages())

        arcpy.JoinField_management(output_features + str(i), "OBJECTID", cluster, "OBJECTID")

        statsFields = []
        for each in fields_to_sum_cluster:
            fieldStatement = [each, "SUM"]  ##
            statsFields.append(fieldStatement)

        for each in fields_to_average_cluster:
            arcpy.AddField_management(in_table=output_features + str(i),
                                      field_name=each + "_weighted", field_type="DOUBLE")
            condition = """!{}!*!Shape_Area!""".format(each)
            arcpy.CalculateField_management(output_features + str(i), each + "_weighted", condition)
            fieldStatement = [each + "_weighted", "SUM"]  ##
            statsFields.append(fieldStatement)

        # Dissolve cluster results
        in_features = output_features + str(i)
        out_feature_class = output_features + "_clustered" + str(i)
        dissolve_field = "CLUSTER_ID"
        arcpy.Dissolve_management(in_features, out_feature_class, dissolve_field,
                                  statistics_fields=statsFields)
        print(arcpy.GetMessages())
        for each in fields_to_average_cluster:
            condition = """!{}!/!Shape_Area!""".format("SUM_" + each + "_weighted")
            arcpy.CalculateField_management(output_features + "_clustered" + str(i), "SUM_" + each + "_weighted",
                                            condition)

    ##########################################################################

    # Merge all clusters projects
    clusterList = []
    for i in range(len(frqDict)):
        clusterList.append(output_features+"_clustered" + str(i))
    print(clusterList)

    # Add Zone ID
    output = arcpy.Merge_management(clusterList, output_features+"_clustered")
    print(arcpy.GetMessages())
    numRows = arcpy.GetCount_management(output)
    print(numRows)
    zoneIDlist = list(islice(multiletters('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), int(
        str(numRows))))  ## numRows is a "result," so need to convert it to a string first then integer
    print(zoneIDlist)
    print("number of zones: " + str(len(zoneIDlist)))
    arcpy.AddField_management(output, "zoneIdentification", "Text")
    i = 0
    cursor = arcpy.UpdateCursor(output)
    for row in cursor:
        row.setValue("zoneIdentification", str(zoneIDlist[i]))
        cursor.updateRow(row)
        i = i + 1

    # Add country name, code and energy source
    arcpy.AddField_management(output, "Energy_Source", "Text")
    arcpy.CalculateField_management(output, "Energy_Source", "'{}'".format(resource))
    arcpy.AddField_management(output, "Country", "Text")
    arcpy.CalculateField_management(output, "Country", "'{}'".format(country))

    # Delete unnecessary files
    arcpy.Delete_management("tooSmallforZoning")
    arcpy.Delete_management("zones_forGrouping")
    arcpy.Delete_management("smallZones")


##################################################
for i in range(len(featureclasses)):

    country = featureclasses[i]
    print(country)
    run_it(country)
    print("Finished " + country)