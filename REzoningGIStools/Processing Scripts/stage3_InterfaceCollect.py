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

# technology = arcpy.GetParameterAsText(0) ## required

## SPATIAL INPUTS
resource = arcpy.GetParameterAsText(0) ##
projectsIn = arcpy.GetParameterAsText(1) ##
projectsOut = arcpy.GetParameterAsText(2) ##
resourceInput = arcpy.GetParameterAsText(3) ## MUST BE A RASTER
csvInput = arcpy.GetParameterAsText(4) ## required
templateRaster = arcpy.GetParameterAsText(5) ## required
scratch = arcpy.GetParameterAsText(6)

################
## PARAMETERS ##
################

RQtype = arcpy.GetParameterAsText(7) ## capacityFactor" or "windPowerDensity"
transmissionDistMultiplier = arcpy.GetParameter(8)
cellSize = int(arcpy.GetParameter(9)) ## 500
largestArea = arcpy.GetParameter(10) ## 500

## COSTS
capCost = arcpy.GetParameter(11)
variableGenOMcost = arcpy.GetParameter(12)
fixedGenOMcost = arcpy.GetParameter(13)
omer = arcpy.GetParameter(14) # Fixed O&M costs escalation rate

effLoss = arcpy.GetParameter(15) ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
outageRate = arcpy.GetParameter(16) ## solar PV only # RD: for both wind and solar. Give option to user to set this to zero for the IRENA dataset.
cfdr = arcpy.GetParameter(17) # Capacity factor degradation rate

transCost = arcpy.GetParameter(18)
subCost =  arcpy.GetParameter(19)
roadCost = arcpy.GetParameter(20)
discountRate = arcpy.GetParameter(21)
plantLifetime = arcpy.GetParameter(22)

## OTHERS
powerDensity = arcpy.GetParameter(23)
landUseDiscount = arcpy.GetParameter(24)




analysis = stage3.Attributes(resource, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount)
analysis.addAttributes()
