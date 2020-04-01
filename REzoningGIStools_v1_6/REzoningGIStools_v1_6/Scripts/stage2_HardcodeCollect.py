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

defaultInputWorkspace = "R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\"

## SPATIAL INPUTS

suitableSites = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb\wind_0_suitability_butwaterline"  ## required

projectsOut = suitableSites + "_areas"  ##

scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\Scratch.gdb"  ## required scratch GDB

templateRaster = defaultInputWorkspace + "GHI_Projected_Africa"  ## required

countryBounds = "R:\\users\\anagha.uppal\\MapRE\\MapRE_Data\\INPUTS\\Countries\\southAfrica\\za.gdb\\za_GADM_countryBounds"  ## optional

geoUnits = "" ## optional

# csvInput = arcpy.GetParameterAsText(3) ## required

## PARAMETERS

fishnetSize = 5  ## in km

fishnetDirectory = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"

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