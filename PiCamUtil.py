import sys
import time
import picamera
import picamera.array
import numpy as np
from PIL import Image
import csv
import os.path # for checking if file exists

#convert a png image to grayscale, save the gray-scale image with name of _gray for testing purposes, return 2D array of  gray-scale values
def pngToGrayArray(png_img):   
    img = Image.open(png_img)  
    arrayForm = np.array(img)
    grImageArray = toGray(arrayForm)
    grImage = Image.fromarray(np.uint8(grImageArray), 'L')
    grImage.save("_gray.png")
    return grImageArray

def DisplayImgArray(img):
     grImage = Image.fromarray(np.uint8(img), 'L')
     grImage.show()

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
          
            camera.capture(output, 'rgb')  #store photo taken from camero to output
            orig_image_gray = toGray(output.array)   #convert 3D array to a 2D grayscale
            orig_image_gray_png = Image.fromarray(np.uint8(orig_image_gray), 'L') #create a PIL image from grayscale 2D array
            orig_image_gray_png.save(label+"_gray.png") #save it for manual verification of proper grayscaling

            #store original image as png as well for manual verification purposes
            orig_image = Image.fromarray(output.array)
            orig_image.save(label+'.png')
        
            orig_png_text = np.array(orig_image)
            return orig_image_gray

#class for the configuration of parking spot boundaries in terms of pixel-counts
class ParkingSpotSet:
    def __init__(self, numPspots):
        self.numPspots = numPspots
        self.pslot_origins = np.empty([numPspots, 2], dtype=int)
        
    def SetOriginRow(self, row):
        self.origin_row = row
        
    def SetOriginCol(self, col):
        self.origin_col = col
        
    def SetLength(self, length):
        self.pSlotLength = length
        
    def SetWidth(self, width):
        self.pSlotWidth = width   
        
    def ManualConfig(self, row, col, length, width, linewidth, appendToFile=False):
         self.origin_row = row
         self.origin_col = col
         self.pSlotLength = length
         self.pSlotWidth = width   
         self.linewidth = linewidth
         #outfile.write("rowName, originRow, originCol, length, width, lineWidth")
         self.Set_ParkingSpotOrigins()
         
         if(appendToFile == True):
             outfile = open("config.csv", "a")
             outfile.write('{},{},{},{},{},{}\n'.format(self.numPspots, row, col, length, width, linewidth))
             outfile.close()
                             
    #sets the origin for each parking spot for easy slicing 
    def Set_ParkingSpotOrigins(self):
        
        if(self.pSlotLength == 0 or self.pSlotWidth == 0):
            sys.exit('Parking Spot length or width is set to zero, object has not been properly initialized')
        if(self.numPspots <1):
            sys.exit('Need at least one parking spot, current value smaller than 1, check if object has been properly initialized')
            
        for i in range(0, self.numPspots):
            upperLeftcolIndex  = self.origin_col + i * (self.pSlotWidth + (0 if i == 0 else self.linewidth))
            self.pslot_origins[i,0] = self.origin_row
            self.pslot_origins[i,1] = upperLeftcolIndex 
            
    # displays the configured bounds as hollow black rectangles, for testign purposes only
    def DisplayConfigurationBounds(self, imgArray):

        for i in range(0, self.numPspots):
            upperLeftcolIndex  = self.origin_col + i * (self.pSlotWidth + (0 if i == 0 else self.linewidth))
            upperRightcolIndex = upperLeftcolIndex + self.pSlotWidth 
            
            #set the top, bottom, left, and right sides of parking spot's outline in black
            imgArray[self.origin_row, upperLeftcolIndex:upperRightcolIndex] = 0
            imgArray[self.origin_row + self.pSlotLength, upperLeftcolIndex:upperRightcolIndex] = 0
            imgArray[self.origin_row:self.origin_row + self.pSlotLength, upperLeftcolIndex] = 0
            imgArray[self.origin_row:self.origin_row + self.pSlotLength, upperLeftcolIndex + self.pSlotWidth] = 0
            
        PNG_IMAGE = Image.fromarray(np.uint8(imgArray), 'L')
        PNG_IMAGE.show()
    
    pslot_origins = []        
    origin_row = 0
    origin_col = 0    
    
    pSlotWidth = 0
    pSlotLength = 0
    linewidth = 0
    numPspots = 0
    
class Collection:
    
    def __init__(self, numSets):
        self.numSets = numSets
        if(os.path.isfile("config.csv") == True):
            self.ConfigFromFile("config.csv") 
    
    def SetMaxAllowedDiffForEmpty(self, threshold):
        self.threshold = threshold
        
    def ConfigFromFile(self, filename):
       with open(filename) as csvfile:
           reader = csv.reader(csvfile, delimiter=',')
          
           for row in reader:
               numSpots = int(row[0])
               origin_row = int(row[1])
               origin_col = int(row[2])
               pSlotLength = int(row[3])
               pSlotWidth = int(row[4])   
               linewidth = int(row[5])
               
               temp = ParkingSpotSet(numSpots)
               temp.ManualConfig(origin_row, origin_col, pSlotLength, pSlotWidth, linewidth, appendToFile=False)
               self.Sets.append(temp)
    
    def CompareImgs(self, empty, current, verbose=False):
       numEmpty = 0
       for set in self.Sets:
           for i in range(0, set.numPspots):
               row = set.pslot_origins[i,0]
               col = set.pslot_origins[i,1]
               length = set.pSlotLength
               width = set.pSlotWidth

               spot_current_img = current[row:row + length, col:col + width]
               spot_ref_img = empty[row:row + length, col:col + width]
               
               if(verbose == True):
                   DisplayImgArray(spot_ref_img)
                   DisplayImgArray(spot_current_img)
        
               spot_diffs = np.subtract(spot_current_img, spot_ref_img)
               spot_diffs = np.absolute(spot_diffs)
        
               total_pixel_diff = np.sum(spot_diffs)
               
               if(verbose == True):
                   print("Difference in parking spot ", i, total_pixel_diff)    
                   
               if(total_pixel_diff < self.threshold):
                   numEmpty = numEmpty +1
                   
       return numEmpty
   
    Sets = []       
    numSets = 0
    threshold = 0


