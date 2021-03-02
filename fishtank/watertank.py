#!/usr/bin/env	python3

import picamera
import os
import argparse
import sys
import re
import time
from PIL import Image, ImageOps, ImageChops
import cv2
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt
from gpiozero import LED

from configmanagement import setup_config_file
from configmanagement import read_config_file


def capture_images(imageName, debug):
    """
    Function to capture images from PI camera

    Parameters:
        imageName (str): Name of captured Image
        debug (bool): Debug Mode

    Returns:
        (bool): True on Success and False on Failure

    """
    try:
        setup_config_file({"debug": True if debug=="y" else False, "training": False})
        configObj = read_config_file()
        camera = picamera.PiCamera()
        # Capture 256*256 resolution images
        camera.resolution = (256, 256)
        # Check if testing folder is present or not
        if not os.path.exists(os.path.join(os.getcwd(), "images")):
            os.mkdir(os.path.join(os.getcwd(), "images"))
        if not os.path.exists(os.path.join(os.getcwd(), "images", "testing")):
            os.mkdir(os.path.join(os.getcwd(), "images", "testing"))
        camera.start_preview()
        time.sleep(2)
        text = None
        while text != "":
            text = input("Hit Enter to capture image\n")
        if configObj["debug"]: sys.stdout.write("Writing images to: {}\n".format(os.path.join(os.getcwd(), "images", "testing", imageName)))
        camera.capture(os.path.join(os.getcwd(), "images", "testing", imageName))
        camera.stop_preview()
        return True
    except Exception as e:
        sys.stderr.write("Error from capture_images: {}\n".format(e))
    return False

def train_images(debug):
    """
    Function to train the water level model

    Parameters:
        debug (bool): Debug Mode

    Returns:
        (bool): True on Success and False on Failure
    """
    try:
        setup_config_file({"debug": True if debug=="y" else False, "training": True})
        configObj = read_config_file()
        if configObj["debug"]: sys.stdout.write("Initial Config: {}\n".format(configObj))
        trainingValues = {}
        # Training on low level image
        trainingData = measure_flooding_level("low.jpg", configObj)
        # Adding the values to configObj to update it back to config
        trainingValues["lowWater"] = trainingData["waterHeight"]
        trainingValues["lowLand"] = trainingData["heightDifference"]
        trainingValues["ratioLow"] = trainingData["wlratio"]
        trainingData = measure_flooding_level("mid.jpg", configObj)
        trainingValues["midWater"] = trainingData["waterHeight"]
        trainingValues["midLand"] = trainingData["heightDifference"]
        trainingValues["ratioMid"] = trainingData["wlratio"]
        trainingData = measure_flooding_level("high.jpg", configObj)
        trainingValues["highWater"] = trainingData["waterHeight"]
        trainingValues["highLand"] = trainingData["heightDifference"]
        trainingValues["ratioHigh"] = trainingData["wlratio"]
        trainingValues["debug"] = True if debug=="Y" else False
        trainingValues["training"] = True
        setup_config_file(trainingValues)
        configObj = read_config_file()
        if configObj["debug"]: sys.stdout.write("Trained Config: {}\n".format(configObj))
        return True
    except Exception as e:
        sys.stderr.write("Error from train_images: {}\n".format(e))
    return False

def test_images(imageName, debug):
    """
    Function to test images

    Parameters:
        imageName (str): Name of testing image
        debug (bool): Debug Mode

    Returns:
        (bool): True on Success and False on Failure

    """
    try:
        configObj = read_config_file()
        configObj["debug"] = True if debug == "y" else False
        configObj["training"] = False
        if configObj["debug"]: sys.stdout.write("Config: {}\n".format(configObj))
        if configObj["waterHeightLow"] == -1:
            print("Train your model and then test it")
        level = measure_flooding_level(imageName, configObj)
        if level["led"] == "red":
            redPin = LED(configObj["redled"])
            redPin.on()
            time.sleep(5)
            redPin.off()
        elif level["led"] == "yellow":
            yellowPin = LED(configObj["yellowled"])
            yellowPin.on()
            time.sleep(5)
            yellowPin.off()
        elif level["led"] == "green":
            greenPin = LED(configObj["greenled"])
            greenPin.on()
            time.sleep(5)
            greenPin.off()
        return True
    except Exception as e:
        sys.stderr.write("Error from test_images: {}\n".format(e))
    return False


def convert_to_greyscale(image_path, debug):
    """
    Function to convert an image to grey scale by applying Binary Threshold and OTSU's binarization
    More info on greyscale parameters: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html

    Parameters:
        image_path (str): Image Path
        debug (bool): Debug Mode

    Returns:
        img (image): OpenCV image type
    """
    img = cv2.imread(image_path)
    # convert to grayscale

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # create a binary thresholded image
    img = cv2.GaussianBlur(img, (5,5), 0)
    _, img = cv2.threshold(img, 105, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(os.getcwd(), "images", "intermediate" , "grey.jpg"), img)
    if debug: sys.stdout.write("convert_to_greyscale done\n")
    return img

def get_heights(img, debug):
    """
    Function to get the height pixel value to crop the image

    Top of the tank:    white pixel with least pixel value on the image
    Tank Width:         maximum white pixel value to the right of image
    Bottom of the tank: white pixel with greatest pixel value on the image
    Top of the land:    row with white pixel value less than 0.8, tested after
                    discarding all the rows with white pixel values greater than
                    0.95 that represent the white background of the image
    Water level:        checking from the bottom of the image to the top of the
                    land in the second half of the image for row with white
                    pixel values between 0.3 and 0.43

    Parameters:
        img (image): OpenCV image type
        debug (bool): Debug Mode

    Returns:
        image_height (int): Pixel value for height of image
    """
    fishtank_top = -1
    tank_width = -1
    flag = True
    for i in range(0, 255):
        for j in range(0, 255):
            if img[i][j] == 255 and flag:
                fishtank_top = i
                flag = False
            if img[i][j] == 255 and tank_width < j:
                tank_width = j
    if debug: sys.stdout.write("Tank top: " + str(fishtank_top) + "\n")
    if debug: sys.stdout.write("Tank Width: " + str(tank_width) + "\n")

    flag = False
    reset = False
    tank_bottom = -1
    water_level = -1
    for i in range(0, 255):
        pixel_match = 0
        for j in range(0, 255):
            # Checking for water pixels by discarding the top rows of the image
            if i > fishtank_top and img[i][j] == 255:
                pixel_match += 1
                if tank_bottom < i:
                    tank_bottom = i
        if not flag:
            # Checking for all white
            if (pixel_match / tank_width) > 0.95:
                reset = True
                continue
            # Checking to make sure the water pixels are more than 10% of the entire width
            if (pixel_match / tank_width) < 0.8 and reset:
                land_level = i
                flag = True
    flag = True
    for i in range(255, land_level, -1):
        testing = []
        if flag:
            for j in range(tank_width, int((tank_width)/2), -1):
                if img[i][j] == 255:
                    testing.append(1)
                else:
                    testing.append(0)
            if 0.3 < (testing.count(1)/tank_width) < 0.43:
                water_level = i
                flag = False
    if debug: sys.stdout.write("Land Level: " + str(land_level) + "\n")
    if debug: sys.stdout.write("Tank bottom: " + str(tank_bottom) + "\n")
    land_height = tank_bottom - land_level
    if debug: sys.stdout.write("Land Height: " + str(land_height) + "\n")
    if debug: sys.stdout.write("Water Level: " + str(water_level) + "\n")
    if debug: sys.stdout.write("Water Height: " + str(tank_bottom - water_level) + "\n")
    return {"land": land_level, "water": water_level, "base": tank_bottom, "top": fishtank_top}

def measure_flooding_level(image_name, configObj):
    """
    Function to detect flooding water level

    Parameters:
        image_name (str): Image Name
        configObj (dict): Configuration Object
    """
    if configObj["training"]:
        img = convert_to_greyscale(os.path.join(os.getcwd(), "images", "training", image_name), configObj["debug"])
    else:
        img = convert_to_greyscale(os.path.join(os.getcwd(), "images", "testing", image_name), configObj["debug"])
    dict_pixel_height = get_heights(img, configObj["debug"])

    tank_height = dict_pixel_height["base"] - dict_pixel_height["top"]
    scaling_factor = tank_height/255;
    land_height = scaling_factor * (dict_pixel_height["base"] - dict_pixel_height["land"])
    water_height = scaling_factor * (dict_pixel_height["base"] - dict_pixel_height["water"])

    if configObj["debug"]: sys.stdout.write("Land and Water Height Difference: {} \n".format(land_height - water_height))
    if configObj["debug"]: sys.stdout.write("Scaling Ratio of Height Difference between land and water: {}\n".format((land_height - water_height)/ tank_height))
    if configObj["debug"]: sys.stdout.write("Scaling Ratio of Water Height: {}\n".format(water_height/ tank_height))
    if configObj["debug"]: sys.stdout.write("Ratio Water/Land: {}\n".format(water_height/land_height))

    '''
    if configObj["debug"] and not configObj["training"]:
        cv2.imshow("GreyImage", img)
        cv2.waitKey()
    '''

    if configObj["training"]:
        return {"waterHeight": round(water_height/ tank_height, 3), "heightDifference": round((land_height - water_height)/ tank_height, 3), "wlratio": round(water_height/land_height,3) }
    else:

        predicted_level = []
        if round((water_height/ tank_height), 3) < configObj["waterHeightMid"]:
            predicted_level.append("green")
        elif round((water_height/ tank_height), 3) < configObj["waterHeightHigh"]:
            predicted_level.append("yellow")
        else:
            predicted_level.append("red")

        if round((land_height - water_height)/ tank_height, 3) > configObj["heightDifferenceMid"]:
            predicted_level.append("green")
        elif round((land_height - water_height)/ tank_height, 3) > configObj["heightDifferenceHigh"]:
            predicted_level.append("yellow")
        else:
            predicted_level.append("red")

        if round(water_height/land_height, 3) < configObj["waterLandRatioMid"]:
            predicted_level.append("green")
        elif round(water_height/land_height, 3) < configObj["waterLandRatioHigh"]:
            predicted_level.append("yellow")
        else:
            predicted_level.append("red")

        if predicted_level.count("green") > 1:
            return({"level": "low", "led": "green"})
        elif predicted_level.count("yellow") > 1:
            return({"level": "mid", "led": "yellow"})
        elif predicted_level.count("red") > 1:
            return({"level": "high", "led": "red"})
        else:
            return {"level": "unknown", "led": "error"}

if __name__ == "__main__":

    choice = 1
    while(choice):
        choice = int(input("1: Capture Image \n2: Training the Model \n3: Testing the Model\n0: Exit\n"))
        if choice == 1:
            debug = ""
            while (debug not in ["y", "n"]):
                debug = input("Enter Debug Mode (Y/N):  ").lower()
                if debug.lower() not in ["y", "n"]:
                    print("Enter valid debug choice")
            imageName = input("Enter Image Name:  ")
            capture_images(imageName, debug)
        elif choice == 2:
            debug = ""
            while (debug not in ["y", "n"]):
                debug = input("Enter Debug Mode (Y/N):  ").lower()
                if debug.lower() not in ["y", "n"]:
                    print("Enter valid debug choice")
            train_images(debug)
        elif choice == 3:
            debug = ""
            while (debug not in ["y", "n"]):
                debug = input("Enter Debug Mode (Y/N):  ").lower()
                if debug.lower() not in ["y", "n"]:
                    print("Enter valid debug choice")
            imageName = input("Enter Image Name from the testing folder:  ")
            test_images(imageName, debug)
        elif choice != 0:
            print("Wrong Choice")
