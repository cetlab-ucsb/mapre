import arcpy

##====================================
##Build Raster Attribute Table
##Usage: BuildRasterAttributeTable_management in_raster {NONE | Overwrite}
    
arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\inputs2020.gdb"

##Build attribute table for single band raster dataset
##Overwrite the existing attribute table file
arcpy.BuildRasterAttributeTable_management("Africa", "NONE")



my_raster_layer = arcpy.Raster(r"R:\users\anagha.uppal\MapRE\inputs2020.gdb\Africa")
if my_raster_layer.hasRAT:
     print("Has a VAT!")
else:
     print("No VAT!")
