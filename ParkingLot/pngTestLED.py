import sys
from gpiozero import LED
sys.path.insert(0, '../Utils/')
import PixelUtils as PU
import ImageProcessingUtils as IPU

led = LED(15)
led.off()
#get image of empty array from png file
empty = IPU.pngToGrayArray("Images/big_empty.png")

#create a collection from demoConfig
test = PU.PixelBlockSetCollection(10, 'demoConfig.csv')
test.SetMaxAllowedDiffForEmpty(500)

verbose = False

#compare against original image
numEmpty = test.CompareImgs(empty, empty, verbose)
print("Num empty spots", numEmpty)
if(numEmpty > 0):
    led.on()

#compare against image with single available spot
current = IPU.pngToGrayArray("Images/OneSpot.png") 
numEmpty = test.CompareImgs(empty, current, verbose)
print("Num empty spots", numEmpty)
if(numEmpty > 0):
    led.on()

led.off()

