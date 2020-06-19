#from Scripts import
import stage1_function
import arcpy

stage1_function.my_function()

technology = "wind"  ## required
yourSpace = "R:\\users\\anagha.uppal\\MapRE\\" ##^^ This is the directory path before the IRENA folder structure
#defaultInputWorkspace = yourSpace + "INPUTS\\" ##^^ enter the path to your DEFAULT INPUT path
## SPATIAL INPUTS
templateRaster = yourSpace + "Angola.gdb\\Angola_elevation500_DEMGADM_Projected_Clipped" ##^^ enter path to DEM data  ## required
countryBounds = yourSpace + "country_bounds.gdb\\Angola"  ## optional
csvInput = yourSpace + "RequiredCSVs\\inputs_siteSuitabilityRasters.csv"  ## required
resourceInput = yourSpace + "Angola.gdb\\Angola_wind_capacityfactor_IEC2_Projected_Clipped"  ## required
## SITE SUITABILITY  PARAMETERS
## Resource input thresholds
thresholdList = [0]  ## required, this can be a multi-value list
arcpy.AddMessage(thresholdList)

## SPATIAL AND NON-SPATIAL OUTPUTS
out_suitableSites_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\AO_Outputs.gdb"  ## required

fileNameSuffix = "suitability"  ## SITE SUITABILITY FC

csvAreaOutput = "sitesuitability_wind.csv"  ## required

scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\Scratch.gdb"

## OPTIONS
rasterOutput = "True"  ## Boolean: TRUE or FALSE

landUseEfficiency = 30  ## required
landUseDiscount = 0.1  ## required
avgCF = 0.2  ## required
minArea = 2  ## required

#geoUnits = yourSpace + "country_bounds.gdb\\South_Africa" # optional
#geoUnits_attribute = "NAME" #optional
geoUnits = "" # "" for no value or file path
geoUnits_attribute = "" # "" for no value or "Attribute name"


analysis = stage1_function.Suitability(technology, templateRaster, countryBounds, csvInput, resourceInput,
                                       thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                                       scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF,
                                       minArea, geoUnits, geoUnits_attribute)
analysis.identifySuitable()