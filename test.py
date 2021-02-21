import PiCamUtil
from gpiozero import LED
import time

empty = PiCamUtil.pngToGrayArray("Images/big_empty.png")
 #half_full = PiCamUtil.pngToGrayArray("Images/half_full.png")
current = PiCamUtil.GetGrayscale2D("currentFull")

test = PiCamUtil.Collection(4, 'realConfig.csv')
test.SetMaxAllowedDiffForEmpty(6000)
verbose = True
numEmpty = test.CompareImgs(empty, current, verbose)
print("Available spots ",numEmpty) 

led = LED(15)
if numEmpty > 0:
    print("Turning on the light")
    led.on()
    time.sleep(5)
else:
    led.off()
