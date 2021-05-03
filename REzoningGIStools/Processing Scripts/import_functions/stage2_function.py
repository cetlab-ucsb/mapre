import arcpy, time

start_time = time.time()

arcpy.CheckOutExtension("spatial")
from arcpy import env
from arcpy.sa import *
import arcpy.cartography as CA

arcpy.env.overwriteOutput = True



def my_function():
    print("Hello World")


# Defining a class
class ProjectCreation:
    def __init__(self, suitableSites, projectsOut, scratch, templateRaster, countryBounds,
                 geoUnits, fishnetSize, fishnetDirectory, whereClauseMax, whereClauseMinContArea):
        ## SPATIAL INPUTS

        '''
        ############################################################################################################
        ## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
        ############################################################################################################
        '''
        #####################
        ## USER SET INPUTS ##
        #####################

        ## SPATIAL INPUTS

        self.suitableSites = str(suitableSites)  ## required

        self.projectsOut = str(projectsOut)  ##

        self.scratch = str(scratch)  ## required scratch GDB

        self.templateRaster = str(templateRaster)  ## required

        self.countryBounds = str(countryBounds)  ## required

        self.geoUnits = str(geoUnits)  ## optional

        # csvInput = arcpy.GetParameterAsText(3) ## required

        ## PARAMETERS

        self.fishnetSize = fishnetSize  ## in km

        self.fishnetDirectory = str(fishnetDirectory)

        # Parameter: area above which to intersect (b)
        self.whereClauseMax = '"Area" > ' + str(whereClauseMax)  ## 25'

        # Parameter: area below which to aggregate (d)
        # self.whereClauseMin = '"Area" < ' + str(whereClauseMin)  ## 5'

        # Parameter: threshold for minimum contiguous project area (a)
        self.whereClauseMinContArea = '"Area" > ' + str(whereClauseMinContArea)  ## 2'

    def createProjectAreas(self):
        '''
        #####################################################################################
        #### --------------------------------GEOPROCESSES--------------------------------####
        #####################################################################################
        ############################################
        ## Set environments and scratch workspace ##
        ############################################
        '''
        # set environments for ansey raster analyses
        arcpy.env.snapRaster = Raster(self.templateRaster)
        arcpy.env.extent = self.countryBounds
        arcpy.env.mask = self.countryBounds
        arcpy.env.cellSize = Raster(self.templateRaster)

        env.workspace = self.scratch
        env.scratchWorkspace = self.scratch

        '''
        #################################################
        ## Check for fishnet file and create if needed ##
        #################################################
        '''

        fishnetSizeStr = str(self.fishnetSize).replace(".", "_")

        fishnet = "in_memory/fishnet_" + fishnetSizeStr \
                  + "km"  ## MUST add .shp if not putting file in gdb (for add field function)
        # fishnet = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\SAPP_Outputs.gdb" + "\\" + "fishnet_" + fishnetSizeStr + "km"
        clippedFishnet = self.fishnetDirectory + "\\" + "fishnet_" + fishnetSizeStr + "km"

        env.outputCoordinateSystem = self.templateRaster
        if not (arcpy.Exists(clippedFishnet)):
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
                                           "", "", "", "NO_LABELS", self.countryBounds, "POLYGON")

            fields = arcpy.ListFields(fishnet)
            for field in fields:
                arcpy.AddMessage(field.name)
            # Change fishnet Object ID name:
            arcpy.AddField_management(fishnet, "Text", "Text", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            # Process: Calculate Field to create new alphanumeric OID column
            arcpy.CalculateField_management(fishnet, "Text", "'A' + str(!OID!)", "PYTHON_9.3", "")

            arcpy.AddMessage("Creating country-boundary-clipped fishnet " + fishnetSizeStr
                             + " km in size to file: " + clippedFishnet)
            arcpy.Clip_analysis(fishnet, self.countryBounds, clippedFishnet)

        arcpy.AddMessage("Copying fishnet to memory :" + clippedFishnet)
        fishnetInMemory = arcpy.CopyFeatures_management(clippedFishnet, "in_memory/clipped_fishnet")

        # Temporary variables:
        IntermediateIntersect_geoUnits = "IntermediateIntersect_geoUnits"
        Intermediate = "in_memory/intermediate_2"
        IntermediateErased = "in_memory/intermediateErased_2"
        IntermediateIntersect = "in_memory/IntermediateIntersect_2"
        IntermediateIntersect_singlept = "in_memory/IntermediateIntersect_singlept"
        # IntermediateAggregatedFeatures = "in_memory/IntermediateAggregatedFeatures_2"
        # IntermediateIntersectErased = "in_memory/IntermediateIntersectErased_2"
        IntermediateEliminated = "in_memory/IntermediateEliminated"
        IntermediateEliminated2 = "in_memory/IntermediateEliminated2"
        # IntermediateSelectedForAggregation1 = "in_memory/IntermediateSelectedForAggregation1_2"
        # IntermediateSelectedForAggregation2 = "in_memory/IntermediateSelectedForAggregation2_2"
        # IntermediateIntersect_geoUnits_2 = "in_memory/IntermediateIntersect_geoUnits_2"

        '''
        ###############
        ## Intersect ##
        ###############
        '''
        ## COPY SUITABLE SITES FEATURE CLASS TO MEMORY
        sites = arcpy.CopyFeatures_management(self.suitableSites, "in_memory/suitableSites")

        ## INTERSECT Geographic Unit of Analysis, if provided
        if arcpy.Exists(self.geoUnits):
            arcpy.AddMessage("Intersecting by geographic units of analysis")
            arcpy.Intersect_analysis([sites, self.geoUnits], IntermediateIntersect_geoUnits, "NO_FID")
        else:
            IntermediateIntersect_geoUnits = sites

        # calculate area:
        arcpy.AddField_management(IntermediateIntersect_geoUnits, "Area", "DOUBLE", "", "", "", "", "NULLABLE",
                                  "NON_REQUIRED", "")
        # Process: Calculate Field
        arcpy.CalculateField_management(IntermediateIntersect_geoUnits, "Area", "!Shape.Area@squarekilometers!",
                                        "PYTHON_9.3", "")

        # select polygons greater than max area to split
        arcpy.Select_analysis(IntermediateIntersect_geoUnits, Intermediate, self.whereClauseMax)
        # erase selected areas from potentialSites (isolate all polygons less than max to merge later)
        arcpy.Erase_analysis(IntermediateIntersect_geoUnits, Intermediate, IntermediateErased)

        # Intersect regions above max area using fishnet
        arcpy.AddMessage("Intersecting by fishnet")
        arcpy.Intersect_analysis([Intermediate, fishnetInMemory], IntermediateIntersect, "NO_FID")
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

        # # Execute SelectLayerByAttribute to define features to be eliminated
        # arcpy.SelectLayerByAttribute_management(in_layer_or_view=tempLayer, selection_type="NEW_SELECTION",
        #                                         where_clause=self.whereClauseMin)
        #
        # # Execute Eliminate
        # arcpy.Eliminate_management("tempLayer", IntermediateEliminated, "LENGTH")

        ## iteration 2

        # # Execute MakeFeatureLayer
        # IntermediateEliminated_tempLayer = arcpy.MakeFeatureLayer_management(IntermediateEliminated,
        #                                                                      "IntermediateEliminated")
        #
        # # Execute SelectLayerByAttribute to define features to be eliminated
        # arcpy.SelectLayerByAttribute_management(in_layer_or_view=IntermediateEliminated_tempLayer,
        #                                         selection_type="NEW_SELECTION", where_clause=self.whereClauseMin)
        #
        # # Execute Eliminate
        # arcpy.Eliminate_management(IntermediateEliminated_tempLayer, IntermediateEliminated2, "LENGTH")

        '''
        ################################################
        ## Merge aggregated with intersected features ##
        ################################################
        '''
        # # Merge aggregated polygons with larger, split polygons
        # merged = arcpy.Merge_management([IntermediateErased, IntermediateEliminated2], "in_memory/intermediateProjects")

        ## AGAIN, INTERSECT Geographic Unit of Analysis, if provided
        if arcpy.Exists(self.geoUnits):
            arcpy.AddMessage("Intersecting by geographic units of analysis")
            arcpy.Intersect_analysis([tempLayer, self.geoUnits], IntermediateIntersect_geoUnits, "NO_FID")
            arcpy.AddMessage("Finished intersecting by geographic units of analysis")
        else:
            IntermediateIntersect_geoUnits = tempLayer

        # recalculate area
        arcpy.CalculateField_management(IntermediateIntersect_geoUnits, "Area", "!Shape.Area@squarekilometers!",
                                        "PYTHON_9.3", "")
        arcpy.CopyFeatures_management(IntermediateIntersect_geoUnits, "intermediate_1")
        # select areas above minimum and save ## CREATE PROJECT FEATURE CLASS
        try:
            arcpy.Select_analysis(IntermediateIntersect_geoUnits, self.projectsOut, self.whereClauseMinContArea)
        except:
            arcpy.CopyFeatures_management(IntermediateIntersect_geoUnits, self.projectsOut)
        ## Process: Summary Statistics
        ## arcpy.Statistics_analysis(selectOut, outputFGDB + filename + '_stats', "Area SUM", "") ## CREATE PROJECT STATS
        arcpy.AddMessage('Finished merging')