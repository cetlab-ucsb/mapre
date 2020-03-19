# import imageio
# import numpy
#import matplotlib.image
#
# a = imageio.imread("R:\\users\\anagha.uppal\\MapRE\\DNI.tif")
# b = imageio.imread("R:\\users\\anagha.uppal\\MapRE\\GHI.tif")
#
# a = numpy.array(a)
# b = numpy.array(b)
#
# joined = numpy.stack((a, b))
# #joined = joined.astype("uint8")
# matplotlib.image.imsave('joined.tif', joined)


########

import numpy as np
#import tifffile
#import cv2
#import matplotlib.image
from skimage import io


#im = io.imread("R:\\users\\anagha.uppal\\MapRE\\DNI.tif")

#im = cv2.imread('R:\\users\\anagha.uppal\\MapRE\\DNI.tif', flags=(cv2.IMREAD_GRAYSCALE | cv2.IMREAD_ANYDEPTH))
#print(im)
#b = tifffile.imread("R:\\users\\anagha.uppal\\MapRE\\GHI.tif")
#print(im)
#tifffile.
#openCV already read as numpy array
#a = numpy.array(a)
#b = numpy.array(b)

#joined = np.stack((a, b))
#joined = joined.astype("uint8")
#cv2.imwrite('R:\\users\\anagha.uppal\\MapRE\\joined.tif', joined)
#print(joined[0])

################################################

import arcpy
import numpy
import cv2

arcpy.env.workspace = "R:\\users\\anagha.uppal\\MapRE\\outputs2020.gdb"

# Get input Raster properties
inRas1 = arcpy.Raster('DNI_Projected')

# Convert Raster to numpy array
arr1 = arcpy.RasterToNumPyArray(inRas1)

inRas2 = arcpy.Raster('GHI_Projected')
arr2 = arcpy.RasterToNumPyArray(inRas2)
print(arr1[0])
print(arr2[0])
joined = numpy.stack((arr1, arr2))
# #joined = joined.astype("uint8")
print(joined)
cv2.imwrite('R:\\users\\anagha.uppal\\MapRE\\joined.tif', joined)



# arcpy.CompositeBands_management("DNI_Projected;GHI_Projected", "joined")