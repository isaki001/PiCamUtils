import PiCamUtil
from gpiozero import LED
import time

empty = PiCamUtil.pngToGrayArray("big_empty.png")
#half_full = PiCamUtil.pngToGrayArray("Images/half_full.png")

test = PiCamUtil.Collection(10, 'demoConfig.csv')
test.SetMaxAllowedDiffForEmpty(500)
verbose = True
led = LED(15)
while(True):
    current = PiCamUtil.GetGrayscale2D("currentFull")
    numEmpty = test.CompareImgs(empty, current, verbose)
    print("Available spots ",numEmpty) 

    if numEmpty > 0:
        print("Turning on the light")
        led.on()
        time.sleep(5)
        led.off()
    else:
        led.off()

