# import imageio
# import numpy
# import matplotlib.image
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
import cv2
#import matplotlib.image
from skimage import io


#im = io.imread("R:\\users\\anagha.uppal\\MapRE\\DNI.tif")

im = cv2.imread('R:\\users\\anagha.uppal\\MapRE\\DNI.tif', flags=(cv2.IMREAD_GRAYSCALE | cv2.IMREAD_ANYDEPTH))
print(im)
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

