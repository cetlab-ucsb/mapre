#from Scripts import
import stage3_function
import arcpy

stage3_function.my_function()

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
projectsIn = r"R:\users\anagha.uppal\MapRE\global_wind_solar_2020\global_wind_solar_2020\global_wind_solar_2020.gdb\global_solar_2020_SAPP" ## required - output of stage 2
resourceInput = yourSpace + "SAPP.gdb\\SAPP_solar_GTI_CF_Projected_Clipped"  ## required raster - solar or wind resource capacity factor file
csvInput = yourSpace + "RequiredCSVs\\inputs_projectAreaAttributes.csv"  ## required - attributes to add and file locations
templateRaster = yourSpace + "SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped"  ## required - retain same raster file (e.g. DEM data) across stages, runs and total region of analysis
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb" ## required - scratch GDB

################
## PARAMETERS ##
################
RQtype = "Capacity Factor"  ## capacityFactor" or "windPowerDensity"
transmissionDistMultiplier = 1.3
cellSize = int(500)  ## 500
largestArea = 25  ## 500
transCost = 990
subCost = 71000
roadCost = 407000
discountRate = 0.1
if resource == "solar":
    ## COSTS
    capCost = 2000000 ## changes between wind and solar
    variableGenOMcost = 4 ## changes between wind and solar
    fixedGenOMcost = 50000 ## changes between wind and solar
    omer = 0  # Fixed O&M costs escalation rate

    effLoss = 0  ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
    outageRate = 0.0  ## changes between wind and solar
    cfdr = 0  # Capacity factor degradation rate

    plantLifetime = 25

    ## OTHERS
    powerDensity = 30  # Land use efficiency (MW/km2) ## changes between wind and solar
    landUseDiscount = 0.1 ## changes between wind and solar
if resource == "wind":
    ## COSTS
    capCost = 1700000  ## changes between wind and solar
    variableGenOMcost = 0  ## changes between wind and solar
    fixedGenOMcost = 60000  ## changes between wind and solar
    omer = 0  # Fixed O&M costs escalation rate

    effLoss = 0.15  ## Assume wind losses (15%) without outage rate (2%).
    outageRate = 0.02  ## changes between wind and solar
    cfdr = 0  # Capacity factor degradation rate

    plantLifetime = 25

    ## OTHERS
    powerDensity = 9  # Land use efficiency (MW/km2) ## changes between wind and solar
    landUseDiscount = 0.25  ## changes between wind and solar

############################DO NOT EDIT BELOW THIS LINE#########################################
projectsOut = projectsIn + "_attr"  ##

analysis = stage3_function.Attributes(resource, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount)
analysis.addAttributes()