#from Scripts import
import stage2_function
import arcpy

stage2_function.my_function()

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

countryBounds = arcpy.GetParameterAsText(4) ## required

geoUnits = arcpy.GetParameterAsText(5) ## optional

# csvInput = arcpy.GetParameterAsText(3) ## required

## PARAMETERS

fishnetSize = float(arcpy.GetParameterAsText(6)) ## in km

fishnetDirectory = arcpy.GetParameterAsText(7)

# Parameter: area above which to intersect (b)
whereClauseMax = str(arcpy.GetParameter(8)) ## 25'

# Parameter: area below which to aggregate (d)
whereClauseMin = str(arcpy.GetParameter(9)) ## 5'

# Parameter: threshold for minimum contiguous project area (a)
whereClauseMinContArea = str(arcpy.GetParameter(10))  ## 2'



analysis = stage2_function.ProjectCreation(suitableSites, projectsOut, scratch,
                                           templateRaster, countryBounds, geoUnits, fishnetSize,
                                           fishnetDirectory, whereClauseMax, whereClauseMin, whereClauseMinContArea)
analysis.createProjectAreas()