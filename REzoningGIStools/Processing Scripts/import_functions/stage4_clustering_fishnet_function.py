
import arcpy, time
from itertools import count, product, islice

start_time = time.time()

arcpy.CheckOutExtension("spatial")
from arcpy import env
from arcpy.sa import *

########INPUTS###########

# create fishnet
# spatial join
# dissolve
# join back attributes

class ClusterTime:
    def __init__(self, workspace, scratch, in_features, output_features,
                templateRaster, fishnetSize, fields_to_sum_cluster, fields_to_average_cluster):
        ## SPATIAL INPUTS
        '''
        #####################################################################################
        #### --------------------------------GEOPROCESSES--------------------------------####
        #####################################################################################
        ############################################
        ## Set environments and scratch workspace ##
        ############################################
        '''
        env.workspace = self.workspace = str(workspace)

        self.in_features = str(in_features)  ## required

        self.output_features = str(output_features)  ##

        self.scratch = str(scratch)  ## required scratch GDB

        self.templateRaster = str(templateRaster)  ## required

        self.fishnetSize = fishnetSize  ## in km

        # set environments for ansey raster analyses
        arcpy.env.snapRaster = Raster(self.templateRaster)
        arcpy.env.cellSize = Raster(self.templateRaster)
        env.outputCoordinateSystem = self.templateRaster

        env.scratchWorkspace = self.scratch

        self.fields_to_sum_cluster = fields_to_sum_cluster
        self.fields_to_average_cluster = fields_to_average_cluster

    def multiletters(self,seq):
        for n in count(1):
            for s in product(seq, repeat=n):
                yield ''.join(s)

    def clusterProjectZones(self):
        '''
        #################################################
        ## Check for fishnet file and create if needed ##
        #################################################
        '''

        fishnetSizeStr = str(self.fishnetSize).replace(".", "_")
        fishnet = "fishnet_" + fishnetSizeStr + "km"
        print(fishnet)

        if not (arcpy.Exists(fishnet)):
            # Create fishnet if one does not already exist:
            arcpy.AddMessage("Creating fishnet " + fishnetSizeStr + " km in size to file: " + fishnet)

            extent = Raster(self.templateRaster).extent

            XMin = extent.XMin  ## left

            YMin = extent.YMin  ## Bottom

            origin = str(XMin) + " " + str(YMin)

            YMax = extent.YMax  ## top

            ycoord = str(XMin) + " " + str(YMax)
            arcpy.CreateFishnet_management(fishnet, origin, ycoord,
                                           self.fishnetSize * 1000, self.fishnetSize * 1000,
                                           '0', '0', "", "NO_LABELS", "#", "POLYGON")
            arcpy.AddMessage("Created fishnet")
            fields = arcpy.ListFields(fishnet)
            for field in fields:
                arcpy.AddMessage(field.name)
            # Change fishnet Object ID name:
            arcpy.AddField_management(fishnet, "Text", "Text", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            # Process: Calculate Field to create new alphanumeric OID column
            arcpy.CalculateField_management(fishnet, "Text", "'A' + str(!OID!)", "PYTHON_9.3", "")

        join_output = "in_memory/" + self.in_features + "_joined"
        # join_output = self.in_features + "_joined"
        arcpy.SpatialJoin_analysis(self.in_features, fishnet, join_output,
                                    match_option="HAVE_THEIR_CENTER_IN")
        arcpy.AddMessage("Joined infeatures with fishnet")

        statsFields = []
        for each in self.fields_to_sum_cluster:
            fieldStatement = [each, "SUM"]  ##
            statsFields.append(fieldStatement)

        for each in self.fields_to_average_cluster:
            arcpy.AddField_management(in_table=join_output,
                                      field_name=each+"_weighted", field_type="DOUBLE")
            condition = """!{}!*!Shape_Area!""".format(each)
            arcpy.CalculateField_management(join_output, each+"_weighted", condition)
            fieldStatement = [each+"_weighted", "SUM"]  ##
            statsFields.append(fieldStatement)

        # # Dissolve cluster results
        arcpy.Dissolve_management(in_features=join_output, out_feature_class=self.output_features,
                                  dissolve_field="Text_1", statistics_fields=statsFields)
        print(arcpy.GetMessages())
        for each in self.fields_to_average_cluster:
            condition = """!{}!/!Shape_Area!""".format("SUM_"+each+"_weighted")
            arcpy.CalculateField_management(self.output_features, "SUM_"+each+"_weighted", condition)
            arcpy.AlterField_management(self.output_features,"SUM_"+each+"_weighted", each)

        numRows = arcpy.GetCount_management(self.output_features)
        zoneIDlist = list(islice(self.multiletters(seq='ABCDEFGHIJKLMNOPQRSTUVWXYZ'), int(
            str(numRows))))  ## numRows is a "result," so need to convert it to a string first then integer
        print("number of zones: " + str(len(zoneIDlist)))
        arcpy.AddField_management(self.output_features, "zoneID", "Text")
        i = 0
        cursor = arcpy.UpdateCursor(self.output_features)
        for row in cursor:
            row.setValue("zoneID", str(zoneIDlist[i]))
            cursor.updateRow(row)
            i = i + 1

##########################################################################
