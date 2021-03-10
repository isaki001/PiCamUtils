import sys
sys.path.insert(0, '../Utils/')
import PixelUtils as PU
import ImageProcessingUtils as IPU

#given a png image, create 2D gray-scale array   
empty = IPU.pngToGrayArray("Images/empty.png")      
#create a collection of pixel sets, with each bound on the coordinates specified by demoConfig.csv
test = PU.PixelBlockSetCollection(9, "demoConfig.csv") 
#overlay the bounds of the pixel blocks on the provided 2D gray-scale array
test.DisplayConfigurationBounds(empty)
