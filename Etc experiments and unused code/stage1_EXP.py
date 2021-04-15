#from Scripts import
import import_functions.stage1_function as stage1_function
import arcpy
import os

stage1_function.my_function()

'''
############################################################################################################
## --------------------------------------- GET ALL INPUTS ----------------------------------------------- ##
############################################################################################################
'''
#####################
## USER SET INPUTS ##
#####################

technology = "wind"  ## required - enter "solar" or "wind"
yourSpace = "R:\\users\\anagha.uppal\\MapRE\\" ## required - This is the directory path for your parent folder structure
## SPATIAL INPUTS
templateRaster = yourSpace + "SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped" ## required - enter path to DEM data
countryBounds = yourSpace + "country_bounds.gdb\\SAPP"  ## required - boundary of region of interest
resourceInput = yourSpace + "SAPP.gdb\\SAPP_wind_windspeed_100m_Projected_Clipped"  ## required - raster dataset of resource quality for the region
## Resource input thresholds
thresholdList = [5.5]  ## required, this can be a multi-value list - minimum threshold for resource quality for siting
arcpy.AddMessage(thresholdList)

## NON-SPATIAL OUTPUTS
out_suitableSites_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\SAPP_Outputs.gdb"  ## required - a pre-created gdb for output files
fileNameSuffix = "suitability_baseScenario"  ## required - results file name
csvAreaOutput = "sitesuitability_wind"  ## required - results file name of total and subregional capacity information
scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb" ## required - a pre-created gdb for scratch files, can remain identical across stages
## If you don't have a gdb preference for scratch, you can choose the "scratch.gdb" folder in the ReZoningGISTools

## OPTIONS
rasterOutput = "True"  ## Boolean: TRUE or FALSE - if you would like an additional raster output

landUseEfficiency = 9  ## required - changes between wind (9) and solar (30)
landUseDiscount = 0.25  ## required - changes between wind (.25) and solar (.1)
avgCF = 0.2  ## required
minArea = 2  ## required

# geoUnits = "" ## enter "" for no value or file path
# geoUnits_attribute = "" ## enter "" for no value or "name of attribute"
geoUnits = yourSpace + "country_bounds.gdb\\SAPP" ## optional - if you wish to split your siting results based on subregional boundaries
geoUnits_attribute = "NAME" ## optional - if splitting results, column name representing name of each subregion
save_subunits_workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\baseScenario_solar.gdb" #optional - if geoUnits-split areas should be individually saved

import csv
import pandas
csvInput = yourSpace + "RequiredCSVs\\inputs_siteSuitabilityRasters.csv"  ## required - the path to spreadsheet with exclusion criteria info
df = pandas.read_csv(csvInput)
for i in range(len(df.columns)):
    col = [i]
    constraint = pandas.read_csv(csvInput, usecols=col, header=None)
    #print(constraint[i][0])
    with open(constraint[i][0]+".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        [writer.writerow([r]) for r in constraint[i]]

    csvInput1 = os.path.join(r"R:\users\anagha.uppal\MapRE\REzoningGIStools_v1_6\REzoningGIStools_v1_6\Scripts", constraint[i][0]+".csv")

    analysis = stage1_function.Suitability(technology, templateRaster, countryBounds, csvInput1, resourceInput,
                                           thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                                           scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF,
                                           minArea, geoUnits, geoUnits_attribute, save_subunits_workspace)
    analysis.identifySuitable()
    os.rename(csvAreaOutput+".csv", csvAreaOutput+"_"+constraint[i][0]+".csv")