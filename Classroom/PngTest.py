import sys
sys.path.insert(0, '../Utils/')
import PixelUtils as PU
import ImageProcessingUtils as IPU
import numpy as np
import PiCamUtil as PCU

#get image of empty array from png file
empty = IPU.pngToGrayArray("Images/empty.png")

#create a collection from demoConfig
test = PU.PixelBlockSetCollection(10, 'demoConfig.csv')
test.SetMaxAllowedDiffForEmpty(2000)

verbose = False

#compare against image with single available spot
current = IPU.pngToGrayArray("Images/7risk.png") 
DeskEmpty = test.GetImageDiffs(empty, current)
print(DeskEmpty)

def Populate2DGrid(rows, cols, PixelBlockEmpty):
     grid = np.empty([rows, cols], dtype=int)
     for i in range(0, rows):
         for j in range(0, cols):
             grid[i,j] = PixelBlockEmpty[i*rows + j]
     print(grid)
     return grid
     
def TopNeighborEmpty(i, j, grid, rows, cols):
     if i == 0:
          return True
     if grid[i-1, j] == 0:
          return False
     else:
          return True

def BottomNeighborEmpty(i, j, grid, rows, cols):
     if i == rows -1:
          return True
     if grid[i+1, j] == 0:
          return False
     else:
          return True
     
def RightNeighborEmpty(i, j, grid, rows, cols):
     if j == cols-1:
          return True
     if grid[i, j+1] == 0:
          return False
     else:
          return True
     
def LeftNeighborEmpty(i, j, grid, rows, cols):
     if j == 0:
          return True
     if grid[i, j-1] == 0:
          return False
     else:
          return True

def NeighborNonEmpty(i, j, grid, rows, cols):
     violation = False
     if LeftNeighborEmpty(i, j, grid, rows, cols) == False:
          return True

     if RightNeighborEmpty(i, j, grid, rows, cols) == False:
          return True

     if BottomNeighborEmpty(i, j, grid, rows, cols) == False:
          return True
     
     if TopNeighborEmpty(i, j, grid, rows, cols) == False:
          return True
     return False

def GetNumViolations(grid, rows, cols):
     #first check the inner slots, the ones that have four neighobors
     numViolations = 0
     for i in range(0, rows):
         for j in range(0, cols):
              if grid[i,j] == 0 and NeighborNonEmpty(i, j, grid, rows, cols) == True:
                numViolations = numViolations + 1
     return numViolations

rows = 3
cols = 3
grid = Populate2DGrid(rows ,cols, DeskEmpty)
peopleAtRisk = GetNumViolations(grid, rows, cols)
print("People at risk", peopleAtRisk)
