#from Scripts import
import stage1_function
import arcpy

stage1_function.my_function()

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

analysis = stage1_function.Suitability(technology, templateRaster, countryBounds, csvInput, resourceInput,
                                       thresholdList, out_suitableSites_gdb, fileNameSuffix, csvAreaOutput,
                                       scratch, rasterOutput, landUseEfficiency, landUseDiscount, avgCF, minArea)
analysis.identifySuitable()