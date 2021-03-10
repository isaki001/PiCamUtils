from gpiozero import LED
import time
import sys
sys.path.insert(0, '../Utils/')
import PixelUtils as PU
import ImageProcessingUtils as IPU
import PiCamUtil

empty = IPU.pngToGrayArray("Images/empty.png")

test = PU.PixelBlockSetCollection(9, 'demoConfig.csv')
test.SetMaxAllowedDiffForEmpty(1100)

verbose = True
led = LED(15)

while(True):
    current = PiCamUtil.GetGrayscale2D("Images/current")
    numEmpty = test.CompareImgs(empty, current, verbose)
    print("Available spots ",numEmpty) 

    if numEmpty > 0:
        print("Turning on the light")
        led.on()
        time.sleep(5)
        led.off()
    else:
        led.off()

