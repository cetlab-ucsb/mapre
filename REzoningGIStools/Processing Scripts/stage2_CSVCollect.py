#from Scripts import
import import_functions.stage2_function as stage2
import arcpy
import pandas as pd

stage2.my_function()

'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

csv_file = pd.read_csv(r"R:\users\anagha.uppal\MapRE\RequiredCSVs\stage2_input.csv", header=None)

## SPATIAL INPUTS

suitableSites = str(csv_file[1][0]) ## required

projectsOut = str(csv_file[1][1]) ## required

scratch = str(csv_file[1][2]) ## required scratch GDB

templateRaster = str(csv_file[1][3]) ## required

countryBounds = str(csv_file[1][4]) ## required

geoUnits = str(csv_file[1][5]) ## optional

# csvInput = arcpy.GetParameterAsText(3) ## required

## PARAMETERS

fishnetSize = float(csv_file[1][6]) ## in km

fishnetDirectory = str(csv_file[1][7])

# Parameter: area above which to intersect (b)
whereClauseMax = str(csv_file[1][8]) ## 25'

# Parameter: area below which to aggregate (d)
# whereClauseMin = str(csv_file[1][9]) ## 5'

# Parameter: threshold for minimum contiguous project area (a)
whereClauseMinContArea = str(csv_file[1][9])  ## 2'


analysis = stage2.ProjectCreation(suitableSites, projectsOut, scratch,
                                           templateRaster, countryBounds, geoUnits, fishnetSize,
                                           fishnetDirectory, whereClauseMax, whereClauseMinContArea)
analysis.createProjectAreas()
