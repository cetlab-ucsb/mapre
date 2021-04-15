#Name test os.path-join

import os
import arcpy

countryName = "southAfrica"
arcpy.CreateFileGDB_management(r"R:\users\anagha.uppal\MapRE", countryName+".gdb")
print(arcpy.GetMessages())
