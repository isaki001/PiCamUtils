import sys
import time
import picamera
import picamera.array
import numpy as np
from PIL import Image

def toGray(img):
    if hasattr(img, 'shape') == 0:
        sys.exit('ERROR image must be 3D array. Provided object does not have shape attribute')           
    if len(img.shape) != 3:
        sys.exit('ERROR image must be encoded as 3D: row, col, plane')
    return  np.dot(img[...,:3], [.299, .587, .114])


#utilizes png image captured by Rasberry Pi Camera
def GetGrayscale2D(label):
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as output:
            camera.resolution = (256, 256)
            camera.start_preview()
            time.sleep(2)

            #store photo taken from camero to output
            camera.capture(output, 'rgb')
            #convert 3D array to a 2D grayscale
            orig_image_gray = toGray(output.array)
            #create a PIL image from grayscale 2D array
            orig_image_gray_png = Image.fromarray(np.uint8(orig_image_gray), 'L')
            #save it for manual verification of proper grayscaling
            orig_image_gray_png.save(label+"_gray.png")

            #store original image as png as well for manual verification purposes
            orig_image = Image.fromarray(output.array)
            orig_image.save(label+'.png')
        
            orig_png_text = np.array(orig_image)
            return orig_image_gray


#utilizes a png image
def pngToGrayArray(png_img):   
    img = Image.open(png_img)  
    arrayForm = np.array(img)
    grImageArray = toGray(arrayForm)
    grImage = Image.fromarray(np.uint8(grImageArray), 'L')
    grImage.save("_gray.png")
    return grImageArray
    