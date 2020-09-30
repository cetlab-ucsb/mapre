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

# technology = arcpy.GetParameterAsText(0) ## required

yourSpace = "R:\\users\\anagha.uppal\\MapRE\\"

## SPATIAL INPUTS
technology = "Wind"  ##
projectsIn = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_wind.gdb\Tanzania_areas"  ##
projectsOut = projectsIn + "_attr"  ##
resourceInput = yourSpace + "Tanzania.gdb\\Tanzania_wind_CF_calc_Projected_Clipped"  ## MUST BE A RASTER
csvInput = yourSpace + "RequiredCSVs\\inputs_projectAreaAttributesw.csv"  ## required
templateRaster = yourSpace + "Tanzania.gdb\\Tanzania_elevation500_DEMGADM_Projected_Clipped"  ## required
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb"

################
## PARAMETERS ##
################
RQtype = "Capacity Factor"  ## capacityFactor" or "windPowerDensity"
transmissionDistMultiplier = 1.3
cellSize = int(500)  ## 500
largestArea = 25  ## 500

capCost = 1700000  ## changes between wind and solar
variableGenOMcost = 0  ## changes between wind and solar
fixedGenOMcost = 60000  ## changes between wind and solar
omer = 0  # Fixed O&M costs escalation rate

effLoss = 0.17  ## Assume wind losses (15%) without outage rate (2%).
outageRate = 0.02  ## changes between wind and solar
cfdr = 0  # Capacity factor degradation rate

transCost = 990
subCost = 71000
roadCost = 407000
discountRate = 0.1
plantLifetime = 25

## OTHERS
powerDensity = 9  # Land use efficiency (MW/km2) ## changes between wind and solar
landUseDiscount = 0.25  ## changes between wind and solar




analysis = stage3_function.Attributes(technology, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount)
analysis.addAttributes()