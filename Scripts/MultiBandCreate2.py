
import arcpy

arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE"

file1 = r"R:\users\anagha.uppal\MapRE\DNI.tif"
file2 = r"R:\users\anagha.uppal\MapRE\joined.tif"

arcpy.MosaicToNewRaster_management([file1, file2], output_location=arcpy.env.workspace,
                                   raster_dataset_name_with_extension="file3.tif", number_of_bands="1")
