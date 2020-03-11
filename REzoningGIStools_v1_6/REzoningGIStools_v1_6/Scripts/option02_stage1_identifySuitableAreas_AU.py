# -*- coding: utf-8 -*-
"""
Created on Sat Sep 05 13:40:19 2015

@author: Grace
"""

### Preamble:
import arcpy, os, sys, time, csv

# start_time = time.time()
# print start_time
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

from arcpy import env
from arcpy.sa import *

arcpy.env.overwriteOutput = True

'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

technology = "solarPV"  ## required

yourSpace = "R:\\users\\anagha.uppal\\MapRE\\MapRE_Data\\" ##^^ This is the directory path before the IRENA folder structure
defaultInputWorkspace = yourSpace + "INPUTS\\" ##^^ enter the path to your DEFAULT INPUT path

## SPATIAL INPUTS
templateRaster = defaultInputWorkspace + "technoeconomic.gdb\\elevation500_DEMGADM_Project" ##^^ enter path to DEM data  ## required

countryBounds = defaultInputWorkspace + "Countries\\southAfrica\\za.gdb\\za_GADM_countryBounds"  ## optional

csvInput = "R:\\users\\anagha.uppal\\MapRE\\inputs_siteSuitabilityRasters.csv"  ## required

resourceInput = defaultInputWorkspace + "Resources.gdb\\GHI_Projected_Africa"  ## required

## SITE SUITABILITY  PARAMETERS
## Resource input thresholds
thresholdList = [2]  ## required, this can be a multi-value list
arcpy.AddMessage(thresholdList)

## SPATIAL AND NON-SPATIAL OUTPUTS
out_suitableSites_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"  ## required

fileNameSuffix = "suitability_plusall"  ## SITE SUITABILITY FC

csvAreaOutput = "sitesuitability_solarPV_SA.csv"  ## required

scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\Scratch.gdb"

## OPTIONS
rasterOutput = "True"  ## Boolean: TRUE or FALSE

landUseEfficiency = 30  ## required
landUseDiscount = 0.1  ## required
avgCF = 0.2  ## required
minArea = 2  ## required

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
arcpy.env.extent = countryBounds
arcpy.env.mask = countryBounds
arcpy.env.snapRaster = templateRaster
arcpy.env.cellSize = templateRaster

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
env.scratchWorkspace = scratch

'''
##############
## Read CSV ##
##############
'''
with open(csvInput, "rt") as csvfile:
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
for threshold in thresholdList:  ## .split(','): ## Multivalue is comma delimited. Split on that and loop through them.
    resourceArea = Con(resourceInput, ifTrue, ifFalse, "Value >= " + str(threshold))
    rasterSelection_final = rasterSelection_constraints * resourceArea
    arcpy.AddMessage("Finished raster calculation for resource threshold: " + str(threshold))

    if countryBounds == "":
        outExtractByMask = rasterSelection_final
    else:
        outExtractByMask = ExtractByMask(rasterSelection_final, countryBounds)

    thresholdStr = str(threshold)
    thresholdStr = thresholdStr.replace(".", "_")

    thresholdFileName = technology + "_" + thresholdStr
    outputFileName = os.path.join(out_suitableSites_gdb, \
                                  str(thresholdFileName) + "_" + fileNameSuffix)

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

    # Process: select areas above minimum contiguous area and SAVE to file
    select = arcpy.Select_analysis(selectIntermediate, outputFileName, \
                                   '"Area" >= ' + str(minArea))

    if rasterOutput.lower() == 'true':  ##save the raster output
        out_resourceRaster = ExtractByMask(resourceInput, select)
        out_resourceRaster.save(outputFileName + "_resourceRaster")

    # get total area of potential:
    arcpy.AddMessage("Finished resource estimate for threshold: " + str(threshold) + ", start calculating area")
    cursor = arcpy.SearchCursor(select)
    areaList = []
    generationList = []
    for row in cursor:
        area = row.getValue("Area")

        generation = area * landUseEfficiency * avgCF * 8760 / 1000 * landUseDiscount

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

# Write Area Sums table as CSV file
with open(csvAreaOutput, 'w') as csvfile:
    writer = csv.writer(csvfile)
    [writer.writerow(r) for r in areaTable]