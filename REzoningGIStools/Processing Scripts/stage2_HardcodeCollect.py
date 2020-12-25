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

yourSpace = "R:\\users\\anagha.uppal\\MapRE\\" ## optional - can be used to shorten filepaths if all files are located together
suitableSites = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\environment.gdb\Angola"  ## required - output of stage 1
projectsOut = suitableSites + "_areas"  ##
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\angola\Scratch.gdb"  ## required - scratch GDB
templateRaster = yourSpace + "SAPP.gdb\\" + "SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required - retain same raster file (e.g. DEM data) across stages, runs and total region of analysis
countryBounds = yourSpace + "country_bounds.gdb\\Angola"  ## required - boundary of region of interest
geoUnits = "" ## optional - if you wish to split your siting results based on subregional boundaries

## USER SET PARAMETERS

fishnetSize = 5  ## required - in km
fishnetDirectory = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\Angola\AO_Outputs.gdb"
# Parameter: area above which to intersect (b)
whereClauseMax = str(50)  ## required - replace value within str() eg 25
# # Parameter: area below which to aggregate (d)
# whereClauseMin = str(5)  ## 5'
# Parameter: threshold for minimum contiguous project area (a)
whereClauseMinContArea = str(3)  ## 2'

############################DO NOT EDIT BELOW THIS LINE#########################################
analysis = stage2_function.ProjectCreation(suitableSites, projectsOut, scratch,
                                           templateRaster, countryBounds, geoUnits, fishnetSize,
                                           fishnetDirectory, whereClauseMax, whereClauseMinContArea)
analysis.createProjectAreas()