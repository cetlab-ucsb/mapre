

# import system modules
import arcpy
import os
import pandas as pd

# Set environment settings
csv_path = r"R:\users\anagha.uppal\MapRE\Scripts\RequiredCSVs\csv_processing_file.csv"
list_of_countries = ["South Africa", "Angola", "Botswana"]
workspace = r"R:\users\anagha.uppal\MapRE\inputs2020.gdb"

#Create folder
parentDirectory = os.path.abspath(os.path.join(workspace, os.pardir))
if arcpy.Exists(os.path.join(parentDirectory, "final.gdb")):
    arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, "final.gdb")
else:
    arcpy.CreateFileGDB_management(parentDirectory, "final.gdb")
    arcpy.env.workspace = workspace_out = os.path.join(parentDirectory, "final.gdb")
print(os.path.abspath(workspace_out)) #final.gdb

csv_file = pd.read_csv(csv_path, header=0)

filenamesDict = { i : [] for i in csv_file['Output File Name'] }
ed = csv_file[csv_file['Euclidean Distance Raster'] == "Yes"]
filenamesDict.update({ i+"_EucDist" : [] for i in ed['Output File Name'] })
extract = csv_file[csv_file['Extract Attributes Raster'].notnull()]
filenamesDict.update({ i+"_Extract" : [] for i in extract['Output File Name'] })
print(filenamesDict)

#Find relevant files
for country in list_of_countries:
    country = country.replace(" ", "_")
    walk = arcpy.da.Walk(os.path.join(parentDirectory, country+".gdb"))
    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            dataset = filename.replace(country+"_", "")
            dataset = dataset.replace("_Projected_Clipped", "")
            filenamesDict[dataset].append(os.path.join(parentDirectory, country+".gdb", filename))

print(filenamesDict)

for key, value in filenamesDict.items():
    # Use Merge tool to move features into single dataset
    if len(value) > 0:
        dsc = arcpy.Describe(value[0])
        if dsc.dataType == "FeatureClass":
            arcpy.Merge_management(value, key)
        elif dsc.dataType == "RasterDataset":
            arcpy.MosaicToNewRaster_management(value, output_location = arcpy.env.workspace,
                                               raster_dataset_name_with_extension = key, number_of_bands = "1",
                                               pixel_type="32_BIT_FLOAT")

