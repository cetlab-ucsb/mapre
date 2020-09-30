# Name: All_clip.py
# Description: Clip each file to each country (M x N)
#Feature classes = Clip and Rasters = Extract by Mask

import arcpy
import os

## arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"

  
workspace_files = r"R:\users\anagha.uppal\MapRE\outputs2020.gdb"
workspace_countries = r"R:\users\anagha.uppal\MapRE\country_bounds.gdb"
fc_vectors = []
vector_names = []
fc_rasters = []
raster_names = []
fc_countries = []
country_names = []

if arcpy.Exists('R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\ALL_AICD_Countries_Power_Plants_Projected'):
    arcpy.Rename_management('R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\ALL_AICD_Countries_Power_Plants_Projected', 'R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb\\Power_Plants_Projected')

walk = arcpy.da.Walk(workspace_files, datatype="FeatureClass")  
  
for dirpath, dirnames, filenames in walk:  
   for filename in filenames:
       fc_vectors.append(os.path.join(dirpath, filename))
       vector_names.append(filename)

walk = arcpy.da.Walk(workspace_files, datatype=["RasterCatalog", "RasterDataset"])

for dirpath, dirnames, filenames in walk:  
   for filename in filenames:
       fc_rasters.append(os.path.join(dirpath, filename))
       raster_names.append(filename)

walk = arcpy.da.Walk(workspace_countries, datatype="FeatureClass")  
  
for dirpath, dirnames, filenames in walk:  
   for filename in filenames:
       if filename != "shp":
           fc_countries.append(os.path.join(dirpath, filename))
           country_names.append(filename)

print(vector_names, raster_names, country_names)


# Set workspace
arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\prep_files.gdb"
   
for i in range(len(fc_vectors)):
    for j in range(len(fc_countries)):
        print(vector_names[i],country_names[j])
        outfc = "{}_{}_Clipped".format(country_names[j],vector_names[i])
        arcpy.Clip_analysis(fc_vectors[i], fc_countries[j], outfc)
        print(arcpy.GetMessages())


for i in range(len(fc_rasters)):
    for j in range(len(fc_countries)):
        print(raster_names[i],country_names[j])
        outfc = "{}_{}_Clipped".format(country_names[j],raster_names[i])
        arcpy.Clip_management(in_raster=fc_rasters[i], rectangle="",
                            clipping_geometry="ClippingGeometry",
                            in_template_dataset=fc_countries[j],
                            out_raster=outfc)
        print(arcpy.GetMessages())


        


