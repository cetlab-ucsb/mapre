# Name: Extract_Attributes.py
# Description: For LULC, we only need certain categories,
# so we filter that raster
# Each alt energy is different, so we need a file for solar/wind/etc
# Requirements: Spatial Analyst Extension

import arcpy
import os
from arcpy.sa import *
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Set workspace
arcpy.env.workspace = workspace_out = r"R:\users\anagha.uppal\MapRE\MapRE_data\INPUTS\Environmental.gdb"

# Set local variables
inRaster = "lulc2_Projected"
#solar_exclusion = """ "VALUE" = 1 """

solar_exclusion = """ "VALUE" NOT IN (1,2,3,4,5,6,11,12,13,14,15,18,19,20) """
wind_nonag_exclusion = """ "VALUE" NOT In (1,2,3,4,5,11,12,13,14,15,18,19,20) """
wind_ag_exclusion = """ "VALUE" NOT In (1,2,3,4,5,12,14,15,18,19,20) """

# Execute ExtractByAttributes
solar_extract = ExtractByAttributes(inRaster, solar_exclusion)

wind_nonag_extract = ExtractByAttributes(inRaster, wind_nonag_exclusion)
wind_ag_extract = ExtractByAttributes(inRaster, wind_ag_exclusion)

# Save the output
solar_extract.save(os.path.join(workspace_out,"lulc_for_solar"))
wind_nonag_extract.save(os.path.join(workspace_out,"lulc_for_wind_nonag"))
wind_ag_extract.save(os.path.join(workspace_out,"lulc_for_wind_ag"))

#############################################

#
# solar_exclusion = """ "Value" In (1,2,3,4,5,6,11,12,13,14,15,18,19,20) """
# #wind_nonag_exclusion = """ "VALUE" In (1,2,3,4,5,11,12,13,14,15,18,19,20) """
# #wind_ag_exclusion = """ "VALUE" In (1,2,3,4,5,12,14,15,18,19,20) """
#
#
# arcpy.MakeRasterLayer_management(in_raster='LULC_Projected2', out_rasterlayer="lulc_for_solar_lyr", where_clause=solar_exclusion)
# #arcpy.MakeRasterLayer_management(in_raster='gm_lc_v3_2_2', out_rasterlayer="lulc_for_windnonag_lyr", where_clause=wind_nonag_exclusion)
# #arcpy.MakeRasterLayer_management(in_raster='gm_lc_v3_2_2', out_rasterlayer="lulc_for_windag_lyr", where_clause=wind_ag_exclusion)
#
# workspace = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"
#
#
# selc = arcpy.SelectLayerByAttribute_management("lulc_for_solar_lyr", 'NEW_SELECTION', solar_exclusion)
# outsol = os.path.join(workspace, "lulc_for_solar")
# #outwindnag = os.path.join(workspace, "lulc_for_windnonag_lyr")
# #outwindag = os.path.join(workspace, "lulc_for_windag_lyr")
#
# arcpy.CopyRaster_management(selc, outsol)
# #arcpy.CopyRaster_management("lulc_for_windnonag_lyr", outwindnag)
# #arcpy.CopyRaster_management("lulc_for_windag_lyr", outwindag)
#
# print(arcpy.GetMessages())
#
# #wait till all eucl dist rasters have run, then rerun this script to see if solar_exclusion
# #applies, finally, must rerun All_Clip.py
