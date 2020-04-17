import arcpy, os, sys, time, csv
from arcpy import env
from arcpy.sa import *

def my_function():
    print("Hello World")


# Defining a class
class Suitability:
    def __init__(self, technology, templateRaster, countryBounds, csvInput, resourceInput,
                     thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                     scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF, minArea, geoUnits):
        ## SPATIAL INPUTS
        self.technology = str(technology)

        self.templateRaster = str(templateRaster)  ##^^ enter path to DEM data  ## required

        self.countryBounds = str(countryBounds)  ## optional

        self.csvInput = str(csvInput)  ## required

        self.resourceInput = str(resourceInput)  ## required

        ## SITE SUITABILITY  PARAMETERS
        ## Resource input thresholds
        self.thresholdList = thresholdList  ## required, this can be a multi-value list

        ## SPATIAL AND NON-SPATIAL OUTPUTS
        self.out_suitableSites_gdb = str(out_suitableSites_gdb)  ## required

        self.fileNameSuffix = str(fileNameSuffix)  ## SITE SUITABILITY FC

        self.csvAreaOutput = str(csvAreaOutput)  ## required

        self.scratch = str(scratch)

        ## OPTIONS
        self.rasterOutput = str(rasterOutput)  ## Boolean: TRUE or FALSE

        self.landUseEfficiency = landUseEfficiency  ## required
        self.landUseDiscount = landUseDiscount  ## required
        self.avgCF = avgCF  ## required
        self.minArea = minArea  ## required
        self.geoUnits = geoUnits

    def identifySuitable(self):

        ### Preamble:

        # start_time = time.time()
        # print start_time
        # Check out the ArcGIS Spatial Analyst extension license
        arcpy.CheckOutExtension("Spatial")

        arcpy.env.overwriteOutput = True

        '''
        ############################################################################################################
        ## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
        ############################################################################################################
        '''
        #####################
        ## USER SET INPUTS ##
        #####################

        #yourSpace = "R:\\users\\anagha.uppal\\MapRE\\MapRE_Data\\" ##^^ This is the directory path before the IRENA folder structure
        #defaultInputWorkspace = yourSpace + "INPUTS\\" ##^^ enter the path to your DEFAULT INPUT path


        ##########################
        ## SET FIXED PARAMETERS OR INPUTS ##
        ##########################

        ## FIXED PARAMETERS
        days = 365
        hours = 8760

        ### Other conditional clauses. Change as needed:
        ifTrue = 1
        ifFalse = 0

        ## BUFFER
        sideType = "FULL"
        endType = "ROUND"
        dissolveType = "ALL"

        selectIntermediate_geoUnits=""


        ###############
        ## FUNCTIONS ##
        ###############
        def getFields(data):
            fieldList = []
            fields = arcpy.ListFields(data)
            for field in fields:
                fieldList.append(field.name)
            return fieldList


        '''
        #####################################################################################
        #### --------------------------------GEOPROCESSES--------------------------------####
        #####################################################################################
        '''
        '''
        ############################################
        ## Set environments and scratch workspace ##
        ############################################
        '''

        # set environments for raster analyses
        arcpy.env.extent = self.countryBounds
        arcpy.env.mask = self.countryBounds
        arcpy.env.snapRaster = self.templateRaster
        arcpy.env.cellSize = self.templateRaster

        ## INPUTS
        scriptpath = sys.path[0]
        toolpath = os.path.dirname(scriptpath)
        # tooldatapath = os.path.join(toolpath, "FOLDERNAME")
        # datapath = os.path.join(tooldatapath, "FILENAME.")

        ## SET SCRATCH WORKSPACES (AND CREATE SCRATCH.GDB IF IT DOESN'T EXIST)
        # scratchws = env.scratchWorkspace
        # scriptpath = sys.path[0]
        # toolpath = os.path.dirname(scriptpath)
        # if not env.scratchWorkspace:
        #    if not(os.path.exists(os.path.join(toolpath, "Scratch/scratch.gdb"))): # Create new fgdb if one does not already exist
        #        arcpy.AddMessage("Creating fgdb " + os.path.join(toolpath, "Scratch/scratch.gdb"))
        #        arcpy.CreateFileGDB_management(toolpath + "/Scratch", "scratch.gdb")
        #    scratchws = os.path.join(toolpath, "Scratch/scratch.gdb")
        #    arcpy.AddMessage("Set scratch workspace")
        env.scratchWorkspace = self.scratch

        '''
        ##############
        ## Read CSV ##
        ##############
        '''
        with open(self.csvInput, "rt") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            fields = next(reader)
            inputData = []
            for row in reader:
                inputData.append(dict(zip(fields, row)))

        ## inputDataPath is a dictionary of all the input datasets
        inputDataPath = {}

        ## populate the inputDataPath for each of the data categories.
        for dataCategory in fields:
            inputDataPath.update({dataCategory: [inputData[0][dataCategory], \
                                                 inputData[1][dataCategory], inputData[2][dataCategory]]})

        #    print dataCategory
        #    if not(inputData[0][dataCategory] == "no"):
        #        if (inputData[1][dataCategory] == "default"):
        #            inputDataPath[dataCategory] = defaultInputWorkspace + inputData[2][dataCategory] ##^^ enter local path for rail file.
        #        elif (inputData[1][dataCategory] == "country"):
        #            inputDataPath[dataCategory] = countryWorkspace + inputData[2][dataCategory] ##^^ enter local path for rail file.
        #        else: print dataCategory + "no data"
        #    print inputDataPath[dataCategory]

        ## Calculate the non-technology-specific conditional rasters for the data categories that may or may not have any datasets. If the data for that category does not exist, then the conditional raster variable is assigned a scalar value of 1
        '''
        ########################
        ## Raster Calculation ##
        ########################
        '''
        ## initiate rasterSelection_constraints
        rasterSelection_constraints = 1

        ## CALCULATE CONSTRAINT-ONLY RASTER
        for constraint in inputDataPath:
            if inputDataPath[constraint][0] == "yes":
                rasterSelection = Con(inputDataPath[constraint][1], ifTrue, ifFalse, \
                                      str(inputDataPath[constraint][2]))
                rasterSelection_constraints = rasterSelection * rasterSelection_constraints
                arcpy.AddMessage("Finished raster calculation for " + constraint)

        ## LISTS TO HOLD THE AREAS AND WRITE TO CSV
        areaSumList = ["Area_km2"]
        generationSumList = ["Generation_MWh"]
        areaLabelList = ["Scenarios"]

        ## CREATE THRESHOLD SCENARIOS
        for threshold in self.thresholdList:  ## .split(','): ## Multivalue is comma delimited. Split on that and loop through them.
            resourceArea = Con(self.resourceInput, ifTrue, ifFalse, "Value >= " + str(threshold))
            rasterSelection_final = rasterSelection_constraints * resourceArea
            arcpy.AddMessage("Finished raster calculation for resource threshold: " + str(threshold))

            if self.countryBounds == "":
                outExtractByMask = rasterSelection_final
            else:
                outExtractByMask = ExtractByMask(rasterSelection_final, self.countryBounds)

            thresholdStr = str(threshold)
            thresholdStr = thresholdStr.replace(".", "_")

            thresholdFileName = self.technology + "_" + thresholdStr
            outputFileName = os.path.join(self.out_suitableSites_gdb, \
                                          str(thresholdFileName) + "_" + self.fileNameSuffix)

            ## Raster to polygon conversion
            intermediate = arcpy.RasterToPolygon_conversion(outExtractByMask, "in_memory/intermediate", "NO_SIMPLIFY", "Value")

            ## Process: select gridcode = 1
            intermediateFields = getFields(intermediate)

            ## check the name of the "grid code" field in the polygon output.
            if "grid_code" in intermediateFields:
                selectIntermediate = arcpy.Select_analysis(intermediate, "in_memory/selectIntermediate", '"grid_code" = 1')

            if "gridcode" in intermediateFields:
                selectIntermediate = arcpy.Select_analysis(intermediate, "in_memory/selectIntermediate", '"gridcode" = 1')

            # Process: Add Field
            arcpy.AddField_management(selectIntermediate, "Area", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

            # Process: Calculate Field
            arcpy.CalculateField_management(selectIntermediate, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3", "")

            # Anagha adding geoUnits to stage1 analysis
            ## INTERSECT Geographic Unit of Analysis, if provided
            if arcpy.Exists(self.geoUnits):
                arcpy.AddMessage("Intersecting by geographic units of analysis")
                arcpy.Intersect_analysis([selectIntermediate, self.geoUnits], selectIntermediate_geoUnits, "NO_FID")
            else:
                selectIntermediate_geoUnits = selectIntermediate


            # Process: select areas above minimum contiguous area and SAVE to file
            select = arcpy.Select_analysis(selectIntermediate_geoUnits, outputFileName, \
                                           '"Area" >= ' + str(self.minArea))

            if self.rasterOutput.lower() == 'true':  ##save the raster output
                out_resourceRaster = ExtractByMask(self.resourceInput, select)
                out_resourceRaster.save(outputFileName + "_resourceRaster")

            # get total area of potential:
            arcpy.AddMessage("Finished resource estimate for threshold: " + str(threshold) + ", start calculating area")
            cursor = arcpy.SearchCursor(select)
            areaList = []
            generationList = []
            for row in cursor:
                area = row.getValue("Area")

                generation = area * self.landUseEfficiency * self.avgCF * 8760 / 1000 * self.landUseDiscount

                generationList.append(generation)
                areaList.append(area)
            areaSumList.append(sum(areaList))
            generationSumList.append(sum(generationList))
            areaLabelList.append(outputFileName)

        '''
        #######################################
        ## Write area csv for all thresholds ##
        #######################################
        '''
        areaTable = [areaLabelList, areaSumList, generationSumList]

        if arcpy.Exists(self.geoUnits):
            pass

        # Write Area Sums table as CSV file
        with open(self.csvAreaOutput, 'w') as csvfile:
            writer = csv.writer(csvfile)
            [writer.writerow(r) for r in areaTable]