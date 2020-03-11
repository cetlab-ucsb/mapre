#from Scripts import
import stage1_function
import arcpy

stage1_function.my_function()

technology = "wind"  ## required
yourSpace = "R:\\users\\anagha.uppal\\MapRE\\" ##^^ This is the directory path before the IRENA folder structure
#defaultInputWorkspace = yourSpace + "INPUTS\\" ##^^ enter the path to your DEFAULT INPUT path
## SPATIAL INPUTS
templateRaster = yourSpace + "outputs2020.gdb\\elevation500_DEMGADM_Projected" ##^^ enter path to DEM data  ## required
countryBounds = yourSpace + "MapRE_data\\INPUTS\\" + "Countries\\southAfrica\\za.gdb\\za_GADM_countryBounds"  ## optional
csvInput = yourSpace + "inputs_siteSuitabilityRasters.csv"  ## required
resourceInput = yourSpace + "outputs2020.gdb\\wind_powerdensity_100m_Africa"  ## required
## SITE SUITABILITY  PARAMETERS
## Resource input thresholds
thresholdList = [2]  ## required, this can be a multi-value list
arcpy.AddMessage(thresholdList)

## SPATIAL AND NON-SPATIAL OUTPUTS
out_suitableSites_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\SA_Outputs.gdb"  ## required

fileNameSuffix = "suitability"  ## SITE SUITABILITY FC

csvAreaOutput = "sitesuitability_solarPV_SA.csv"  ## required

scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\southAfrica\Scratch.gdb"

## OPTIONS
rasterOutput = "True"  ## Boolean: TRUE or FALSE

landUseEfficiency = 30  ## required
landUseDiscount = 0.1  ## required
avgCF = 0.2  ## required
minArea = 2  ## required


analysis = stage1_function.Suitability(technology, templateRaster, countryBounds, csvInput, resourceInput,
                                       thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                                       scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF, minArea)
analysis.identifySuitable()