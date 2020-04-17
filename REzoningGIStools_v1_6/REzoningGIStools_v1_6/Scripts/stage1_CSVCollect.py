#from Scripts import
import stage1_function
import arcpy
import pandas as pd

stage1_function.my_function()

csv_file = pd.read_csv(r"R:\users\anagha.uppal\MapRE\RequiredCSVs\stage1_input.csv", header=None)


technology = str(csv_file[1][0])  ## required
#yourSpace = "R:\\users\\anagha.uppal\\MapRE\\" ##^^ This is the directory path before the IRENA folder structure
#defaultInputWorkspace = yourSpace + "INPUTS\\" ##^^ enter the path to your DEFAULT INPUT path
## SPATIAL INPUTS
templateRaster = str(csv_file[1][1]) ##^^ enter path to DEM data  ## required
countryBounds = str(csv_file[1][2])  ## optional
csvInput = str(csv_file[1][3])  ## required
resourceInput = str(csv_file[1][4])  ## required
## SITE SUITABILITY  PARAMETERS
## Resource input thresholds
thresholdList = csv_file[1][5].split(",") ## required, this can be a multi-value list
thresholdList = [float(i) for i in thresholdList]
arcpy.AddMessage(thresholdList)

## SPATIAL AND NON-SPATIAL OUTPUTS
out_suitableSites_gdb = str(csv_file[1][6])  ## required

fileNameSuffix = str(csv_file[1][7])  ## SITE SUITABILITY FC

csvAreaOutput = str(csv_file[1][8])  ## required

scratch = str(csv_file[1][9])

## OPTIONS
rasterOutput = str(csv_file[1][10])  ## Boolean: TRUE or FALSE

landUseEfficiency = int(csv_file[1][11])  ## required
landUseDiscount = float(csv_file[1][12])  ## required
avgCF = float(csv_file[1][13])  ## required
minArea = float(csv_file[1][14])  ## required


analysis = stage1_function.Suitability(technology, templateRaster, countryBounds, csvInput, resourceInput,
                                       thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                                       scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF, minArea)
analysis.identifySuitable()