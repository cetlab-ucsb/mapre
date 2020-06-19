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
projectsIn = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\AO_Outputs.gdb\wind_0_suitability_areas"  ##
projectsOut = projectsIn + "_attr"  ##
resourceInput = yourSpace + "Angola.gdb\\Angola_wind_capacityfactor_IEC2_Projected_Clipped"  ## MUST BE A RASTER
csvInput = yourSpace + "RequiredCSVs\\inputs_projectAreaAttributes.csv"  ## required
templateRaster = yourSpace + "Angola.gdb\\Angola_elevation500_DEMGADM_Projected_Clipped"  ## required
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\Scratch.gdb"

################
## PARAMETERS ##
################

RQtype = "Capacity Factor"  ## capacityFactor" or "windPowerDensity"
transmissionDistMultiplier = 1.3
cellSize = int(500)  ## 500
largestArea = 25  ## 500

## COSTS
capCost = 1700000
variableGenOMcost = 0
fixedGenOMcost = 50000
omer = 0  # Fixed O&M costs escalation rate

effLoss = 0.17  ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
outageRate = 0.02  ## solar PV only # RD: for both wind and solar. Give option to user to set this to zero for the IRENA dataset.
cfdr = 0  # Capacity factor degradation rate

transCost = 990
subCost = 71000
roadCost = 407000
discountRate = 0.1
plantLifetime = 25

## OTHERS
powerDensity = 9 #Land use efficiency (MW/km2)
landUseDiscount = 0.1




analysis = stage3_function.Attributes(technology, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount)
analysis.addAttributes()