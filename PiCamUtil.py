import sys
import numpy as np
from PIL import Image

def DisplayImgArray(img):
     grImage = Image.fromarray(np.uint8(img), 'L')
     grImage.show()

def toGray(img):
    if hasattr(img, 'shape') == 0:
        sys.exit('ERROR image must be 3D array. Provided object does not have shape attribute')           
    if len(img.shape) != 3:
        sys.exit('ERROR image must be encoded as 3D: row, col, plane')
    return  np.dot(img[...,:3], [.299, .587, .114])


#utilizes a png image
def pngToGrayArray(png_img):   
    img = Image.open(png_img)  
    arrayForm = np.array(img)
    grImageArray = toGray(arrayForm)
    grImage = Image.fromarray(np.uint8(grImageArray), 'L')
    grImage.save("_gray.png")
    return grImageArray
    
#def CalibrateParkingSpots(img):
    
class ParkingSpotSet:
    def __init__(self, numPspots):
        self.numPspots = numPspots
    
    def SetOriginRow(self, row):
        self.origin_row = row
        
    def SetOriginCol(self, col):
        self.origin_col = col
        
    def SetLength(self, length):
        self.pSlotLength = length
        
    def SetWidth(self, width):
        self.pSlotWidth = width   
    
    def Display(self, imgArray):

        for i in range(0, self.numPspots):
            upperLeftcolIndex  = self.origin_col + i * (self.pSlotWidth + (0 if i == 0 else self.linewidth))
            upperRightcolIndex = upperLeftcolIndex + self.pSlotWidth 
            
            #set the top side of parking spot's outline in black
            imgArray[self.origin_row, upperLeftcolIndex:upperRightcolIndex] = 0
             #set the bottom side of parking spot's outline in black
            imgArray[self.origin_row + self.pSlotLength, upperLeftcolIndex:upperRightcolIndex] = 0
            #set the left side of the parking spot's outline in black
            imgArray[self.origin_row:self.origin_row + self.pSlotLength, upperLeftcolIndex] = 0
            #set the right side of the parking spot's outline in black
            imgArray[self.origin_row:self.origin_row + self.pSlotLength, upperLeftcolIndex + self.pSlotWidth] = 0
        PNG_IMAGE = Image.fromarray(np.uint8(imgArray), 'L')
            
        PNG_IMAGE.show()
            
    origin_row = 0
    origin_col = 0    
    
    pSlotWidth = 0
    pSlotLength = 0
    linewidth = 5
    numPspots = 0
    
x = pngToGrayArray("plot.png")
#TopRowParkingSpotRow = ParkingSpotSet(5)
#TopRowParkingSpotRow.SetOriginRow(95)
#TopRowParkingSpotRow.SetOriginCol(33)
#TopRowParkingSpotRow.SetWidth(157)
#TopRowParkingSpotRow.SetLength(200)
#TopRowParkingSpotRow.Display(x)

TopRowParkingSpotRow = ParkingSpotSet(5)
TopRowParkingSpotRow.SetOriginRow(95)
TopRowParkingSpotRow.SetOriginCol(33)
TopRowParkingSpotRow.SetWidth(72)
TopRowParkingSpotRow.SetLength(150)
TopRowParkingSpotRow.Display(x)
