import arcpy
import os
arcpy.env.overwriteOutput = True

resource = "wind"
new_attributes_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers_wind.gdb"
previous_zones_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_wind.gdb"
fields_to_sum_cluster = ["egen", "incap"]  # original field values summed for final clusters/zones
fields_to_average_cluster = ["d_road", "d_water", "m_elev", "m_slope", "m_popden", "m_humfoot", "m_cf",
                             "l_road", "l_gen", "d_trans", "d_rail", "d_anyre", "d_airport",
                             "m_resource", "l_tra", "lt_tra", "m_rangeland",
                             "c_coloc", "j_lulc"]  # original fields averaged for final clusters/zones

arcpy.env.workspace = new_attributes_gdb
featureclasses = arcpy.ListFeatureClasses("*_areas_attr")
print(featureclasses)
for fc in featureclasses:
    print(fc)
    previous_zones_file = "{}_zones".format(fc)
    new_attributes_filename = fc
    join_output = "in_memory/" + new_attributes_filename + "_joined"
    #join_output = new_attributes_filename + "_joined"

    if arcpy.GetCount_management(new_attributes_filename)[0] != "0":

        arcpy.SpatialJoin_analysis(new_attributes_filename,
                                   os.path.join(previous_zones_gdb, previous_zones_file),
                                   join_output, match_option="WITHIN")

        statsFields = []
        for each in fields_to_sum_cluster:
            fieldStatement = [each, "SUM"]  ##
            statsFields.append(fieldStatement)

        for each in fields_to_average_cluster:
            arcpy.AddField_management(in_table=join_output,
                                      field_name=each + "_weighted", field_type="DOUBLE")
            condition = """!{}!*!Shape_Area!""".format(each)
            arcpy.CalculateField_management(join_output, each + "_weighted", condition)
            fieldStatement = [each + "_weighted", "SUM"]  ##
            statsFields.append(fieldStatement)

        # Dissolve cluster results
        arcpy.Dissolve_management(in_features=join_output, out_feature_class=new_attributes_filename + "_zones",
                                  dissolve_field="zoneID", statistics_fields=statsFields)

        print(arcpy.GetMessages())

        with arcpy.da.UpdateCursor(new_attributes_filename + "_zones", "zoneID") as cursor:
            for row in cursor:
                if row[0] is None:
                    print(row)
                    cursor.deleteRow()

        for each in fields_to_average_cluster:
            condition = """!{}!/!Shape_Area!""".format("SUM_" + each + "_weighted")
            arcpy.CalculateField_management(new_attributes_filename + "_zones", "SUM_" + each + "_weighted", condition)
            arcpy.AlterField_management(new_attributes_filename + "_zones", "SUM_" + each + "_weighted", each)

    else:
        print(new_attributes_filename, ": Input file empty, no output to script")