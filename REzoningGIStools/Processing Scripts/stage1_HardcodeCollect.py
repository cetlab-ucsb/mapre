#from Scripts import
import stage1_function
import arcpy

stage1_function.my_function()

technology = "wind"  ## required
yourSpace = "R:\\users\\anagha.uppal\\MapRE\\" ##^^ This is the directory path before the IRENA folder structure
#defaultInputWorkspace = yourSpace + "INPUTS\\" ##^^ enter the path to your DEFAULT INPUT path
## SPATIAL INPUTS
templateRaster = yourSpace + "SAPP.gdb\\SAPP_elevation500_DEMGADM_Projected_Clipped" ##^^ enter path to DEM data  ## required
countryBounds = yourSpace + "country_bounds.gdb\\SAPP"  ## optional
csvInput = yourSpace + "RequiredCSVs\\inputs_siteSuitabilityRasters.csv"  ## required
resourceInput = yourSpace + "SAPP.gdb\\SAPP_wind_windspeed_100m_Projected_Clipped"  ## required
## SITE SUITABILITY  PARAMETERS
## Resource input thresholds
thresholdList = [5.5]  ## required, this can be a multi-value list
arcpy.AddMessage(thresholdList)

## SPATIAL AND NON-SPATIAL OUTPUTS
out_suitableSites_gdb = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\SAPP_Outputs.gdb"  ## required

fileNameSuffix = "suitability_allTiers_nolulc"  ## SITE SUITABILITY FC

csvAreaOutput = "sitesuitability_wind.csv"  ## required

scratch = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\Scratch.gdb"

## OPTIONS
rasterOutput = "True"  ## Boolean: TRUE or FALSE

landUseEfficiency = 30  ## required
landUseDiscount = 0.25  ## required
avgCF = 0.2  ## required
minArea = 2  ## required

# geoUnits = "" # "" for no value or file path
# geoUnits_attribute = "" # "" for no value or "Attribute name"
geoUnits = yourSpace + "country_bounds.gdb\\SAPP" # optional
geoUnits_attribute = "NAME" #optional
save_subunits_workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\allTiers_nolulc_wind.gdb" #optional - if geoUnits-split areas should be individually saved


analysis = stage1_function.Suitability(technology, templateRaster, countryBounds, csvInput, resourceInput,
                                       thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                                       scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF,
                                       minArea, geoUnits, geoUnits_attribute, save_subunits_workspace)
analysis.identifySuitable()