import PiCamUtil
import numpy as np

def DisplayCurrentConfig(imgGrayArray, configFile):
    test = PiCamUtil.Collection(4, configFile)
    #test.Sets[0].DisplayConfigurationBounds(imgGrayArray)
    test.Sets[0].DisplayConfigurationBounds(imgGrayArray)
    test.Sets[1].DisplayConfigurationBounds(imgGrayArray)
    test.Sets[2].DisplayConfigurationBounds(imgGrayArray)
    test.Sets[3].DisplayConfigurationBounds(imgGrayArray)
   


def ConfigHelper(testingImg):
    acceptable = 0
    tempCopy = testingImg
    while acceptable == 0:
        tempCopy = np.copy(testingImg)
        
        print("Enter number of parking spots in set")
        numSpots = int(input())
        print("Enter row (in pixel count) of origin")
        row = int(input())
        print("Enter col (in pixel count) of origin")
        col = int(input())
        print("Enter length of parking spot")
        length = int(input())
        print("Width of parking spot")
        width = int(input())
        print("Line width")
        lineWidth = int(input())
    
        test = PiCamUtil.Collection(2, 'config.csv')
        test.SetMaxAllowedDiffForEmpty(5000)

        first = PiCamUtil.ParkingSpotSet(numSpots)
        first.ManualConfig(row, col, length, width, lineWidth)
        first.DisplayConfigurationBounds(tempCopy)

        print("Is image good? Enter 1 or 0 for yes or no")
        acceptable = int(input())

        if(acceptable == 0):
            del test
            del first

        if(acceptable != 1 and acceptable != 0):
            acceptable = 0

#from gpiozero import LED
#led = LED(15)
#led.off()

empty = PiCamUtil.GetGrayscale2D("big_empty")
DisplayCurrentConfig(empty, "realConfig.csv")            
#empty = PiCamUtil.pngToGrayArray("Images/empty.png")
#half_full = PiCamUtil.pngToGrayArray("Images/half_full.png")

#ConfigHelper(empty)

#numEmpty = test.CompareImgs(empty, half_full)
#rint("Available spots ",numEmpty) 
