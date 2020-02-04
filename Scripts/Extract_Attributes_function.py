# Name: Extract_Attributes.py
# Description: For LULC, we only need certain categories,
# so we filter that raster
# Each alt energy is different, so we need a file for solar/wind/etc

import arcpy
import os
import argparse


#argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, nargs='+', help="input directory", type=str)
ap.add_argument("-if", "--input_file", required=True, nargs='+', help="name of land use land cover file to extract", type=str)
ap.add_argument("-o", "--output", required=True, nargs='+', help="output directory", type=str)
ap.add_argument("-s", "--solar", required=False, nargs='+',
                help="which land use categories to extract for solar (numbers separated by commas) \n"
                "Reference for LULC Categories to Process LULC Data \n"
                "# Code   Class Name \n"
                "# 1  Broadleaf Evergreen Forest \n"
                "# 2  Broadleaf Deciduous Forest \n"
                "# 3  Needleleaf Evergreen Forest \n"
                "# 4  Needleleaf Deciduous Forest \n"
                "# 5  Mixed Forest \n"
                "# 6  Tree Open \n"
                "# 7  Shrub \n"
                "# 8  Herbaceous \n"
                "# 9  Herbaceous with Sparse Tree/Shrub \n"
                "# 10 Sparse vegetation \n"
                "# 11   Cropland \n"
                "# 12  Paddy field \n"
                "# 13  Cropland / Other Vegetation Mosaic \n"
                "# 14  Mangrove \n"
                "# 15  Wetland \n"
                "# 16  Bare area,consolidated(gravel,rock) \n"
                "# 17  Bare area,unconsolidated (sand) \n"
                "# 18  Urban \n"
                "# 19  Snow / Ice \n"
                "# 20  Water bodies", type=str)
ap.add_argument("-wn", "--wind_nonag", required=False, nargs='+',
                help="which land use categories to extract for non-ag wind (numbers separated by commas)", type=str)
ap.add_argument("-wa", "--wind_ag", required=False, nargs='+',
                help="which land use categories to extract for ag wind (numbers separated by commas)", type=str)

#----------------------------------- Process LULC data ----------------------------
# global map:


args = vars(ap.parse_args())

# Set workspace
arcpy.env.workspace = args["input"][0]
print(arcpy.ListRasters())


solar_exclusion = """ "Value" In ({}) """.format(args["solar"][0])
print(solar_exclusion)
#solar_exclusion = """ "Value" In (1,2,3,4,5,6,11,12,13,14,15,18,19,20) """
#wind_nonag_exclusion = """ "VALUE" In (1,2,3,4,5,11,12,13,14,15,18,19,20) """
#wind_ag_exclusion = """ "VALUE" In (1,2,3,4,5,12,14,15,18,19,20) """


arcpy.MakeRasterLayer_management(in_raster=args["input_file"][0], out_rasterlayer="lulc_for_solar_lyr", where_clause=solar_exclusion)
#arcpy.MakeRasterLayer_management(in_raster='gm_lc_v3_2_2', out_rasterlayer="lulc_for_windnonag_lyr", where_clause=wind_nonag_exclusion)
#arcpy.MakeRasterLayer_management(in_raster='gm_lc_v3_2_2', out_rasterlayer="lulc_for_windag_lyr", where_clause=wind_ag_exclusion)

workspace = args["output"][0]


selc = arcpy.SelectLayerByAttribute_management("lulc_for_solar_lyr", 'NEW_SELECTION', solar_exclusion)
outsol = os.path.join(workspace, "lulc_for_solar")
#outwindnag = os.path.join(workspace, "lulc_for_windnonag_lyr")
#outwindag = os.path.join(workspace, "lulc_for_windag_lyr")

arcpy.CopyRaster_management(selc, outsol)
#arcpy.CopyRaster_management("lulc_for_windnonag_lyr", outwindnag)
#arcpy.CopyRaster_management("lulc_for_windag_lyr", outwindag)

print(arcpy.GetMessages())
