# Name: FeatureToRaster_Ex_02.py
# Description: Converts features to a raster dataset.

# Import system modules
import arcpy
from arcpy import env

# Set environment settings
env.workspace = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"

# Input feature classes
input_features = ["cities", "counties", "blocks", "crime"]

# Output workspace
out_workspace = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"

# Set local variables
#outRaster = "c:/output/roadsgrd"
cellSize = 25
field = "CLASS"

# Execute FeatureToRaster
for fc in arcpy.ListFeatureClasses("*Name*"):
    outRaster = arcpy.Describe(fc).baseName + "_Rasterized"
    arcpy.FeatureToRaster_conversion(input_features, field, outRaster, cellSize)
