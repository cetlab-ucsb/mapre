#from Scripts import
import stage2_function

stage2_function.my_function()


'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

defaultInputWorkspace = "R:\\users\\anagha.uppal\\MapRE\\"

## SPATIAL INPUTS

suitableSites = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers.gdb\Democratic_Republic_of_the_Congo"  ## required

projectsOut = suitableSites + "_areas"  ##

scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\DRC\Scratch.gdb"  ## required scratch GDB

templateRaster = defaultInputWorkspace + "DRC.gdb\\DRC_elevation500_DEMGADM_Projected_Clipped"  ## required

countryBounds = defaultInputWorkspace + "country_bounds.gdb\\DRC"  ## optional

geoUnits = "" ## optional

# csvInput = arcpy.GetParameterAsText(3) ## required

## PARAMETERS

fishnetSize = 5  ## in km

fishnetDirectory = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\DRC\DRC_Outputs.gdb"

# Parameter: area above which to intersect (b)
whereClauseMax = str(100)  ## 25'

# Parameter: area below which to aggregate (d)
whereClauseMin = str(5)  ## 5'

# Parameter: threshold for minimum contiguous project area (a)
whereClauseMinContArea = str(2)  ## 2'


analysis = stage2_function.ProjectCreation(suitableSites, projectsOut, scratch,
                                           templateRaster, countryBounds, geoUnits, fishnetSize,
                                           fishnetDirectory, whereClauseMax, whereClauseMin, whereClauseMinContArea)
analysis.createProjectAreas()