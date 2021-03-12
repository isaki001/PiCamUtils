import time
import picamera
import picamera.array
import numpy as np
from PIL import Image
import ImageProcessingUtils

#utilizes png image captured by Rasberry Pi Camera
def GetGrayscale2D(label):
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as output:
            camera.resolution = (256, 256)
            camera.start_preview()
            time.sleep(2)
          
            camera.capture(output, 'rgb')  #store photo taken from camero to output
            orig_image_gray = ImageProcessingUtils.toGray(output.array)   #convert 3D array to a 2D grayscale
            orig_image_gray_png = Image.fromarray(np.uint8(orig_image_gray), 'L') #create a PIL image from grayscale 2D array
            orig_image_gray_png.save(label+"_gray.png") #save it for manual verification of proper grayscaling

            #store original image as png as well for manual verification purposes
            orig_image = Image.fromarray(output.array)
            orig_image.save(label+'.png')
        
            return orig_image_gray

def TurnOnCamera():
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as output:
            camera.resolution = (256, 256)
            camera.start_preview()
            time.sleep(60)

