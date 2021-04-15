## Takes in a gdb and outputs geojson versions of each
import arcpy
import os

input_gdbs = [""]
arcpy.env.workspace = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP"
input_gdbs = arcpy.ListWorkspaces("*", "FileGDB")
print(input_gdbs)
output_folder = r"R:\users\anagha.uppal\MapRE\MapRE_data\OUTPUTS\SAPP\outputs_for_web"
outCS = arcpy.SpatialReference(4326)

for each in input_gdbs:
    print(each)
    foldername = each.rsplit("\\",1)[1]
    foldername = foldername.split(".")[0]
    print(foldername)
    outdirname = os.path.join(output_folder, foldername)
    if not os.path.exists(outdirname):
        outdir = os.mkdir(outdirname)
    outdir = outdirname
    arcpy.env.workspace = each
    featureclasses = [fc for fc in arcpy.ListFeatureClasses("*_attr*")]
    print(featureclasses)
    for fc in featureclasses:
        print(fc)
        print(outdir)
        os.mkdir(os.path.join(outdir,fc))
        fcdir = os.path.join(outdir,fc)
        print(fcdir)
        shpout = os.path.join(fcdir, fc+".shp")
        shp = arcpy.Project_management(fc, shpout, outCS)
        #shutil.make_archive(fc, 'zip', root_dir=outdir)
        jsonout = os.path.join(outdir, fc+".json")
        print(jsonout)
        arcpy.FeaturesToJSON_conversion(shp, jsonout)
