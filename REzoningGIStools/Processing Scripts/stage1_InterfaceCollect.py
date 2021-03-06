#from Scripts import
import  import_functions.stage1_function as stage1
import arcpy

stage1.my_function()

technology = arcpy.GetParameterAsText(0) ## required

## SPATIAL INPUTS
templateRaster = arcpy.GetParameterAsText(1) ## required

countryBounds = arcpy.GetParameterAsText(2) ## optional

csvInput = arcpy.GetParameterAsText(3) ## required

resourceInput = arcpy.GetParameterAsText(4) ## required

## SITE SUITABILITY  PARAMETERS
## Resource input thresholds
thresholdList = arcpy.GetParameter(5) ## required, this can be a multi-value list
arcpy.AddMessage(thresholdList)

## SPATIAL AND NON-SPATIAL OUTPUTS
out_suitableSites_gdb = arcpy.GetParameterAsText(6) ## required

fileNameSuffix = arcpy.GetParameterAsText(7) ## SITE SUITABILITY FC

csvAreaOutput = arcpy.GetParameterAsText(8) ## required

scratch = arcpy.GetParameterAsText(9)

## OPTIONS
rasterOutput = arcpy.GetParameterAsText(10) ## Boolean: TRUE or FALSE

landUseEfficiency = arcpy.GetParameter(11) ## required
landUseDiscount = arcpy.GetParameter(12) ## required
avgCF = arcpy.GetParameter(13) ## required
minArea = arcpy.GetParameter(14) ## required

geoUnits = arcpy.GetParameter(15) ## required
geoUnits_attribute = arcpy.GetParameter(16) ## required
save_subunits_workspace = arcpy.GetParameter(17) ## required

analysis = stage1.Suitability(technology, templateRaster, countryBounds, csvInput, resourceInput,
                                       thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                                       scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF,
                                       minArea, geoUnits, geoUnits_attribute, save_subunits_workspace)
analysis.identifySuitable()
