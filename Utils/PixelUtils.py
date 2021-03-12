import sys
import numpy as np
from PIL import Image
import csv
import os.path # for checking if file exists
from numpy import genfromtxt


#class for the configuration of parking spot boundaries in terms of pixel-counts
class PixelBlockSet:
    def __init__(self, numPspots):
        self.numPspots = numPspots
        self.pslot_origins = np.empty([numPspots, 2], dtype=int)
        
    def SetOriginRow(self, row):
        self.origin_row = row
        
    def SetOriginCol(self, col):
        self.origin_col = col
        
    def SetLength(self, length):
        self.length = length
        
    def SetWidth(self, width):
        self.width = width   
     
    #initializes the pixel block's attributes    
    def Config(self, _row, _col, _length, _width, _spaceAmongMembers, appendToFile=False):
         self.origin_row = _row
         self.origin_col = _col
         self.length = _length
         self.width = _width   
         self.spaceAmongMembers = _spaceAmongMembers
         self.SetPixelBlockOrigins()
         
         if(self.numPspots < 1):
             sys.exit("Fewer than one pixel block, misconfiguration has occured")
             
         rightMostCoord = _col + self.numPspots*_width + (self.numPspots-1)*_spaceAmongMembers
         topMostCoord = _row + _length
         
         if(rightMostCoord > 256 or rightMostCoord < 0 or topMostCoord > 256 or topMostCoord < 0):
             sys.exit("Setting pixel bounds with provided parameters would result in assigning some pixel block, pixels that are out of bounds (greater than 256 or smaller than 0")
        
         if(appendToFile == True):
             outfile = open("config.csv", "a")
             outfile.write('{},{},{},{},{},{}\n'.format(self.numPspots, _row, _col, _length, _width, _spaceAmongMembers))
             outfile.close()
                             
    #sets the origin for each parking spot for easy slicing 
    def SetPixelBlockOrigins(self):
        
        if(self.length == 0 or self.width == 0):
            sys.exit('Parking Spot length or width is set to zero, object has not been properly initialized')
        if(self.numPspots <1):
            sys.exit('Need at least one parking spot, current value smaller than 1, check if object has been properly initialized')
            
        for i in range(0, self.numPspots):
            upperLeftcolIndex  = self.origin_col + i * (self.width + (0 if i == 0 else self.spaceAmongMembers))
            self.pslot_origins[i,0] = self.origin_row
            self.pslot_origins[i,1] = upperLeftcolIndex 
            
    # overides the pixels on the perimeter of the  block's bounds, with zero value (black color)
    def MarkConfigurationBounds(self, imgArray):

        for i in range(0, self.numPspots):
            upperLeftcolIndex  = self.origin_col + i * (self.width + (0 if i == 0 else self.spaceAmongMembers))
            upperRightcolIndex = upperLeftcolIndex + self.width 
            
            #set the top, bottom, left, and right sides of parking spot's outline in black
            imgArray[self.origin_row, upperLeftcolIndex:upperRightcolIndex] = 0
            imgArray[self.origin_row + self.length, upperLeftcolIndex:upperRightcolIndex] = 0
            imgArray[self.origin_row:self.origin_row + self.length, upperLeftcolIndex] = 0
            imgArray[self.origin_row:self.origin_row + self.length, upperLeftcolIndex + self.width] = 0
    
    pslot_origins = []        
    origin_row = 0
    origin_col = 0    
    
    width = 0
    length = 0
    spaceAmongMembers = 0
    numPspots = 0
    
class PixelBlockSetCollection:
    
    def __init__(self, numSets, filename):
        self.numSets = numSets
        if(os.path.isfile(filename) == True):
            self.ConfigFromFile(filename)
        else:
            print("Supplied Configuration File is not present on current path")
   
    #sets the threhold for the allowed cumulative pixel difference
    def SetMaxAllowedDiffForEmpty(self, threshold):
        self.threshold = threshold
        
    def ConfigFromFile(self, filename):
        data = genfromtxt(filename, delimiter=',')
        data = np.delete(data, 0, 0) #delete header
        for row in data:
            numSpots = int(row[0])
            origin_row = int(row[1])
            origin_col = int(row[2])
            length = int(row[3])
            width = int(row[4])   
            spaceAmongMembers = int(row[5])
            
            temp = PixelBlockSet(numSpots)
            temp.Config(origin_row, origin_col, length, width, spaceAmongMembers, appendToFile=False)
            self.Sets.append(temp)
            
    def CompareImgs(self, empty, current, verbose=False):
       numEmpty = 0
       for set in self.Sets:
           for i in range(0, set.numPspots):
               row = set.pslot_origins[i,0]
               col = set.pslot_origins[i,1]
               length = set.length
               width = set.width

               spot_current_img = current[row:row + length, col:col + width]
               spot_ref_img = empty[row:row + length, col:col + width]
                      
               spot_diffs = np.subtract(spot_current_img, spot_ref_img)
               spot_diffs = np.absolute(spot_diffs)
        
               total_pixel_diff = np.sum(spot_diffs)
               
               if(verbose == True):
                   print("Difference in parking spot ", i, total_pixel_diff)    
                   
               if(total_pixel_diff < self.threshold):
                   numEmpty = numEmpty +1                                     
       return numEmpty
   
    # returns an array for each PixelBlock, with a 1 if its empty, and a zero otherwise
    def GetImageDiffs(self, empty, current):
       StatusEmpty = []
       pixelBlockStatus = 1
       for set in self.Sets:
           for i in range(0, set.numPspots):
               row = set.pslot_origins[i,0]
               col = set.pslot_origins[i,1]
               length = set.length
               width = set.width

               spot_current_img = current[row:row + length, col:col + width]
               spot_ref_img = empty[row:row + length, col:col + width]
                      
               spot_diffs = np.subtract(spot_current_img, spot_ref_img)
               spot_diffs = np.absolute(spot_diffs)
        
               total_pixel_diff = np.sum(spot_diffs)
               print("Pixel diff", total_pixel_diff)                 
               if(total_pixel_diff < self.threshold):
                    pixelBlockStatus = 1
               else:
                    pixelBlockStatus = 0
               StatusEmpty.append(pixelBlockStatus)
                                                        
       return StatusEmpty
   
    
    def DisplayConfigurationBounds(self, imgArray):
        for set in self.Sets:
            set.MarkConfigurationBounds(imgArray)   
        PNG_IMAGE = Image.fromarray(np.uint8(imgArray), 'L')
        PNG_IMAGE.show() 

    Sets = []       
    numSets = 0
    threshold = 0


