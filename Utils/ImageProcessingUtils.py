import sys
import numpy as np
from PIL import Image

#convert a png image to grayscale, save the gray-scale image with name of _gray for testing purposes, return 2D array of  gray-scale values
def pngToGrayArray(png_img):   
    img = Image.open(png_img)  
    arrayForm = np.array(img)
    grImageArray = toGray(arrayForm)
    grImage = Image.fromarray(np.uint8(grImageArray), 'L')
    grImage.save("_gray.png")
    return grImageArray

# Create an image to display, from a 2D array of pixel values
def DisplayImgArray(img):
     grImage = Image.fromarray(np.uint8(img), 'L')
     grImage.show()

#convert 3D array of pixel values, to gray-scale 2D array of pixel values
def toGray(img):
    if hasattr(img, 'shape') == 0:
        sys.exit('ERROR image must be 3D array. Provided object does not have shape attribute')           
    if len(img.shape) != 3:
        sys.exit('ERROR image must be encoded as 3D: row, col, plane')
    return  np.dot(img[...,:3], [.299, .587, .114])

