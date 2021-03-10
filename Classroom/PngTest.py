import sys
sys.path.insert(0, '../Utils/')
import PixelUtils as PU
import ImageProcessingUtils as IPU
import numpy as np

#get image of empty array from png file
empty = IPU.pngToGrayArray("Images/empty.png")

#create a collection from demoConfig
test = PU.PixelBlockSetCollection(10, 'demoConfig.csv')
test.SetMaxAllowedDiffForEmpty(1200)

verbose = False


    

#compare against image with single available spot
current = IPU.pngToGrayArray("Images/current.png") 
DeskEmpty = test.GetImageDiffs(empty, current)
print(DeskEmpty)

def Populate2DGrid(rows, cols, PixelBlockEmpty):
     grid = np.empty([rows, cols], dtype=int)
     for i in range(0, rows):
         for j in range(0, cols):
             grid[i,j] = PixelBlockEmpty[i*rows + j]
     print(grid)
     return grid

Populate2DGrid(3,3, DeskEmpty)