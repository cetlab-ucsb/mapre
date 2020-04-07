#from Scripts import
import stage3_function
import arcpy
import pandas as pd


stage3_function.my_function()

'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

csv_file = pd.read_csv(r"R:\users\anagha.uppal\MapRE\RequiredCSVs\stage3_input.csv", header=None)


# technology = arcpy.GetParameterAsText(0) ## required

## SPATIAL INPUTS
technology = str(csv_file[1][0]) ##
projectsIn = str(csv_file[1][1]) ##
projectsOut = str(csv_file[1][2]) ##
resourceInput = str(csv_file[1][3]) ## MUST BE A RASTER
csvInput = str(csv_file[1][4]) ## required
templateRaster = str(csv_file[1][5]) ## required
scratch = str(csv_file[1][6])

################
## PARAMETERS ##
################

RQtype = csv_file[1][7] ## capacityFactor" or "windPowerDensity"
transmissionDistMultiplier = csv_file[1][8]
cellSize = int(csv_file[1][9]) ## 500
largestArea = csv_file[1][10] ## 500

## COSTS
capCost = csv_file[1][11]
variableGenOMcost = csv_file[1][12]
fixedGenOMcost = csv_file[1][13]
omer = csv_file[1][14] # Fixed O&M costs escalation rate

effLoss = csv_file[1][15] ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
outageRate = csv_file[1][16] ## solar PV only # RD: for both wind and solar. Give option to user to set this to zero for the IRENA dataset.
cfdr = csv_file[1][17] # Capacity factor degradation rate

transCost = csv_file[1][18]
subCost =  csv_file[1][19]
roadCost = csv_file[1][20]
discountRate = csv_file[1][21]
plantLifetime = csv_file[1][22]

## OTHERS
powerDensity = csv_file[1][23]
landUseDiscount = csv_file[1][24]




analysis = stage3_function.Attributes(technology, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount)
analysis.addAttributes()