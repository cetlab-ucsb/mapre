#from Scripts import
import import_functions.stage3_function as stage3
import arcpy
import pandas as pd


stage3.my_function()

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
resource = str(csv_file[1][0]) ##
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
transmissionDistMultiplier = float(csv_file[1][8])
cellSize = int(csv_file[1][9]) ## 500
largestArea = int(csv_file[1][10]) ## 500

## COSTS
capCost = int(csv_file[1][11])
variableGenOMcost = int(csv_file[1][12])
fixedGenOMcost = int(csv_file[1][13])
omer = int(csv_file[1][14]) # Fixed O&M costs escalation rate

effLoss = float(csv_file[1][15]) ## Assume wind losses (15%) without outage rate (2%). So default value should be 0.85;
outageRate = float(csv_file[1][16]) ## solar PV only # RD: for both wind and solar. Give option to user to set this to zero for the IRENA dataset.
cfdr = float(csv_file[1][17]) # Capacity factor degradation rate

transCost = int(csv_file[1][18])
subCost =  int(csv_file[1][19])
roadCost = int(csv_file[1][20])
discountRate = float(csv_file[1][21])
plantLifetime = int(csv_file[1][22])

## OTHERS
powerDensity = int(csv_file[1][23])
landUseDiscount = float(csv_file[1][24])




analysis = stage3.Attributes(resource, projectsIn, projectsOut, resourceInput, csvInput, templateRaster,
                 scratch, RQtype, transmissionDistMultiplier, cellSize, largestArea, capCost,
                 variableGenOMcost, fixedGenOMcost, omer, effLoss, outageRate, cfdr,
                 transCost, subCost, roadCost, discountRate, plantLifetime, powerDensity, landUseDiscount)
analysis.addAttributes()