import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")

defaultInputWorkspace = "R:\\users\\anagha.uppal\\MapRE\\"

## SPATIAL INPUTS

suitableSites = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_wind.gdb\South_Africa"  ## required

projectsOut = suitableSites + "_areas_25_test1"  ##

scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\South_Africa\Scratch.gdb"  ## required scratch GDB

templateRaster = defaultInputWorkspace + "South_Africa.gdb\\South_Africa_elevation500_DEMGADM_Projected_Clipped"  ## required

countryBounds = defaultInputWorkspace + "country_bounds.gdb\\South_Africa"  ## optional

geoUnits = "" ## optional

## PARAMETERS

fishnetSize = 25  ## in km

fishnetDirectory = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\South_Africa\SA_Outputs.gdb"


'''
#####################################################################################
#### --------------------------------GEOPROCESSES--------------------------------####
#####################################################################################

############################################
## Set environments and scratch workspace ##
############################################
'''
# set environments for ansey raster analyses
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

fishnetSizeStr = str(fishnetSize).replace(".", "_")

fishnet = "in_memory/fishnet_" + fishnetSizeStr \
          + "km"  ## MUST add .shp if not putting file in gdb (for add field function)
clippedFishnet = fishnetDirectory + "\\" + "fishnet_" + fishnetSizeStr + "km"

env.outputCoordinateSystem = templateRaster
if not (arcpy.Exists(clippedFishnet)):
    # Create fishnet if one does not already exist:
    arcpy.AddMessage("Creating fishnet " + fishnetSizeStr + " km in size to file: " + fishnet)

    extent = Raster(templateRaster).extent

    XMin = extent.XMin  ## left

    YMin = extent.YMin  ## Bottom

    origin = str(XMin) + " " + str(YMin)

    YMax = extent.YMax  ## top

    ycoord = str(XMin) + " " + str(YMax)

    arcpy.CreateFishnet_management(fishnet, origin, ycoord,
                                   fishnetSize * 1000, fishnetSize * 1000,
                                   '0', '0', "", "NO_LABELS", "#", "POLYGON")

    fields = arcpy.ListFields(fishnet)
    for field in fields:
        arcpy.AddMessage(field.name)
    # Change fishnet Object ID name:

    arcpy.AddField_management(fishnet, "Text", "Text", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    # Process: Calculate Field to create new alphanumeric OID column
    arcpy.CalculateField_management(fishnet, "Text", "'A' + str(!OID!)", "PYTHON_9.3", "")

    arcpy.AddMessage("Creating country-boundary-clipped fishnet " + fishnetSizeStr
                     + " km in size to file: " + clippedFishnet)
    arcpy.Clip_analysis(fishnet, countryBounds, clippedFishnet)

arcpy.AddMessage("Copying fishnet to memory :" + clippedFishnet)
fishnetInMemory = arcpy.CopyFeatures_management(clippedFishnet, "in_memory/clipped_fishnet")

'''
###############
## Intersect ##
###############
'''
IntermediateIntersect = "in_memory/IntermediateIntersect_1"
## COPY SUITABLE SITES FEATURE CLASS TO MEMORY
sites = arcpy.CopyFeatures_management(suitableSites, "in_memory/suitableSites")
arcpy.Intersect_analysis([sites, fishnetInMemory], IntermediateIntersect, "NO_FID")
arcpy.CalculateField_management(IntermediateIntersect, "Area", "!Shape.Area@squarekilometers!", "PYTHON_9.3",
                                "")
arcpy.CopyFeatures_management(IntermediateIntersect, projectsOut)

