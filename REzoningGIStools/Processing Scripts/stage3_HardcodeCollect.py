#from Scripts import
import import_functions.stage3_function as stage3
import arcpy

stage3.my_function()

'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

yourSpace = "R:\\users\\anagha.uppal\\MapRE\\" ## optional - can be used to shorten filepaths if all files are located together

## SPATIAL INPUTS
resource = "solar"  ## required - "solar" or "wind"
projectsIn = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\human.gdb\Democratic_Republic_of_the_Congo_areas" ## required - output of stage 2
projectsOut = projectsIn + "_attr"  ##
resourceInput = yourSpace + "DRC.gdb\\DRC_solar_GTI_CF_Projected_Clipped"  ## required raster - solar or wind resource capacity factor file
csvInput = yourSpace + "RequiredCSVs\\inputs_projectAreaAttributes.csv"  ## required - attributes to add and file locations
templateRaster = yourSpace + "SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required - retain same raster file (e.g. DEM data) across stages, runs and total region of analysis
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb" ## required - scratch GDB

################
## PARAMETERS ##
################
RQtype = "Capacity Factor"  ## "Capacity Factor" or "kWh/m2-day" or "Wind speed (m/s)" or "W/m2"
transmissionDistMultiplier = 1.3 ##
cellSize = int(500)  ## 500
largestArea = 25  ## 500

capCost = 1700000  ## Capital Cost - changes between wind and solar
variableGenOMcost = 0  ## Variable Generation O&M cost - changes between wind and solar
fixedGenOMcost = 60000  ## Fixed Generation O&M cost - changes between wind and solar
omer = 0  # Fixed O&M costs escalation rate

effLoss = 0.17  ## Energy loss in the line - can change between wind and solar
outageRate = 0.02  ## changes between wind and solar
cfdr = 0  # Capacity factor degradation rate

transCost = 990
subCost = 71000
roadCost = 407000
discountRate = 0.1
plantLifetime = 25

## OTHERS
powerDensity = 9  # Land use efficiency (MW/km2) - changes between wind and solar
landUseDiscount = 0.25  ## Land use discount factor - changes between wind and solar


############################DO NOT EDIT BELOW THIS LINE#########################################

analysis = stage3.Attributes(resource, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount)
analysis.addAttributes()