
###################################################################
## This script creates projects from a resource potential layer  ##
###################################################################
# BOTTOM UP APPROACH (SIMPLE) TO PROJECT CREATION

##--------------------------------Preamble ----------------------------------
import arcpy, time
start_time = time.time()
print start_time
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
from arcpy import env
from arcpy.sa import *
import arcpy.cartography as CA
arcpy.env.overwriteOutput = True

'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

## SPATIAL INPUTS

suitableSites = arcpy.GetParameterAsText(0) ## required

projectsOut = arcpy.GetParameterAsText(1) ##

scratch = arcpy.GetParameterAsText(2) ## required scratch GDB

templateRaster = arcpy.GetParameterAsText(3) ## required

countryBounds = arcpy.GetParameterAsText(4) ## optional

# csvInput = arcpy.GetParameterAsText(3) ## required

## PARAMETERS

fishnetSize = int(arcpy.GetParameterAsText(5)) ## in km

fishnetDirectory = arcpy.GetParameterAsText(6)

# Parameter: area above which to intersect (b)
whereClauseMax = '"Area" > ' + str(arcpy.GetParameter(7)) ## 25'

# Parameter: area below which to aggregate (d)
whereClauseMin = '"Area" < ' + str(arcpy.GetParameter(8)) ## 5'

# Parameter: threshold for minimum contiguous project area (a)
whereClauseMinContArea = '"Area" > ' + str(arcpy.GetParameter(9))  ## 2'

'''
#####################################################################################
#### --------------------------------GEOPROCESSES--------------------------------####
#####################################################################################

############################################
## Set environments and scratch workspace ##
############################################
'''   
# set environments for any raster analyses
arcpy.env.snapRaster = Raster(templateRaster)
arcpy.env.extent = countryBounds
arcpy.env.mask = countryBounds
arcpy.env.cellSize = Raster(templateRaster)

env.workspace = scratch
env.scratchWorkspace = scratch

'''
#################################################
## Check for fishnet file and create if needed ##
#################################################
'''   

fishnet = "in_memory/fishnet_" + str(fishnetSize) + "km" ## MUST add .shp if not putting file in gdb (for add field function)
clippedFishnet = fishnetDirectory + "\\"+ "fishnet_" + str(fishnetSize) + "km"

env.outputCoordinateSystem = templateRaster
if not(arcpy.Exists(clippedFishnet)):
    #Create fishnet if one does not already exist:
    arcpy.AddMessage("Creating fishnet " + str(fishnetSize) + " km in size to file: " + fishnet)

    extent = Raster(templateRaster).extent
    
    XMin = extent.XMin ## left
    
    YMin = extent.YMin ## Bottom
    
    origin = str(XMin) + " " + str(YMin)
    
    YMax = extent.YMax ## top
    
    ycoord = str(XMin) + " " + str(YMax)
    
    arcpy.CreateFishnet_management(fishnet, origin, ycoord, \
                                   fishnetSize * 1000,fishnetSize * 1000, '0', '0', "", "NO_LABELS", \
                                   "#", "POLYGON")
                                   
    fields = arcpy.ListFields(fishnet)
    for field in fields:    
        arcpy.AddMessage(field.name)
    # Change fishnet Object ID name:
    arcpy.AddField_management(fishnet, "Text", "Text", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    # Process: Calculate Field to create new alphanumeric OID column
    arcpy.CalculateField_management(fishnet, "Text", "'A' + str(!OID!)", "PYTHON_9.3", "")

    arcpy.AddMessage("Creating country-boundary-clipped fishnet " + str(fishnetSize) + " km in size to file: " + clippedFishnet)
    arcpy.Clip_analysis(fishnet, countryBounds, clippedFishnet)

arcpy.AddMessage("Copying fishnet to memory :"  + clippedFishnet)
fishnetInMemory = arcpy.CopyFeatures_management(clippedFishnet, "in_memory/clipped_fishnet")

# Temporary variables:
Intermediate = "in_memory/intermediate_2"
IntermediateErased = "in_memory/intermediateErased_2"
IntermediateIntersect = "in_memory/IntermediateIntersect_2"
IntermediateAggregatedFeatures = "in_memory/IntermediateAggregatedFeatures_2"
IntermediateIntersectErased = "in_memory/IntermediateIntersectErased_2"
IntermediateSelectedForAggregation1 = "in_memory/IntermediateSelectedForAggregation1_2"
IntermediateSelectedForAggregation2 = "in_memory/IntermediateSelectedForAggregation2_2"

'''
###############
## Intersect ##
###############
''' 
## COPY SUITABLE SITES FEATURE CLASS TO MEMORY
sites = arcpy.CopyFeatures_management(suitableSites, "in_memory/suitableSites")
# calculate area:
arcpy.AddField_management(sites, "Area", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
# Process: Calculate Field
arcpy.CalculateField_management(sites, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3", "")

# select polygons greater than max area to split
arcpy.Select_analysis(sites, Intermediate, whereClauseMax)
# erase selected areas from potentialSites
arcpy.Erase_analysis(sites, Intermediate, IntermediateErased)

# Intersect regions above max area using fishnet
arcpy.AddMessage("Intersecting by fishnet")
arcpy.Intersect_analysis([Intermediate, fishnetInMemory], IntermediateIntersect, "NO_FID")
arcpy.AddMessage("finished intersecting by fishnet")
# Process: Calculate Area
arcpy.CalculateField_management(IntermediateIntersect, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3", "")

'''
###############
## Aggregate ##
###############
''' 
arcpy.AddMessage("Starting aggregation")
# select areas under min to aggregate
arcpy.Select_analysis(IntermediateIntersect, IntermediateSelectedForAggregation1, whereClauseMin)
# Process: erase small areas from larger areas
arcpy.Erase_analysis(IntermediateIntersect, IntermediateSelectedForAggregation1, IntermediateIntersectErased)
# merge those under min area to aggregate
arcpy.Merge_management([IntermediateSelectedForAggregation1, IntermediateErased],IntermediateSelectedForAggregation2)
# aggregate smaller abutting areas into one polygon
CA.AggregatePolygons(IntermediateSelectedForAggregation2, IntermediateAggregatedFeatures, 1, "", 0, "ORTHOGONAL", "", "aggregatedTable")
arcpy.AddMessage("Finished Aggregation")

'''
################################################
## Merge aggregated with intersected features ##
################################################
''' 
# Merge aggregated polygons with larger, split polygons
merged = arcpy.Merge_management([IntermediateIntersectErased, IntermediateAggregatedFeatures], "in_memory/intermediateProjects")
# recalculate area
arcpy.CalculateField_management(merged, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3", "")
# select areas above minimum and save
selectOut = arcpy.Select_analysis(merged, projectsOut, whereClauseMinContArea) ## CREATE PROJECT FEATURE CLASS
## Process: Summary Statistics
## arcpy.Statistics_analysis(selectOut, outputFGDB + filename + '_stats', "Area SUM", "") ## CREATE PROJECT STATS
arcpy.AddMessage('Finished merging')

