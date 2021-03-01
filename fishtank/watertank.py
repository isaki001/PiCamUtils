#!/usr/bin/env	python3.7

# For working with Python Camera: https://medium.com/@petehouston/capture-images-from-raspberry-pi-camera-module-using-picamera-505e9788d609
# TODO:Test the below codes
# https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
# https://www.pyimagesearch.com/2017/06/19/image-difference-with-opencv-and-python/
# https://www.thepythoncode.com/article/contour-detection-opencv-python: Contour Detection

# import picamera
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

from configmanagement import setup_config_file
from configmanagement import read_config_file


def capture_images(**kw):
    camera = picamera.PiCamera()
    camera.resolution = (256, 256)
    if not os.path.exists(os.path.join(os.getcwd(), "images")):
        os.mkdir(os.path.join(os.getcwd(), "images"))
    if not os.path.exists(os.path.join(os.getcwd(), "images", "testing")):
        os.mkdir(os.path.join(os.getcwd(), "images", "testing"))
    camera.start_preview()
    time.sleep(2)
    text = None
    while text != "":
        text = input("Hit Enter to capture image")
    if debug: sys.stdout.write("Writing images to: {}\n".format(os.path.join(os.getcwd(), "images", "testing", kw["out"])))
    camera.capture(os.path.join(os.getcwd(), "images", "training", kw["out"]))
    camera.stop_preview()

def train_images(**kw):
    kw["training"] = True
    setup_config_file(**kw)
    configObj = read_config_file()
    if configObj["debug"]: sys.stdout.write("Initial Config: {}\n".format(configObj))
    trainingData = measure_water_level("low.jpg", configObj)
    # measure_water_level("low1.jpg", configObj)
    kw["lowWater"] = trainingData["waterHeight"]
    kw["lowLand"] = trainingData["heightDifference"]
    kw["ratioLow"] = trainingData["wlratio"]
    trainingData = measure_water_level("mid.jpg", configObj)
    kw["midWater"] = trainingData["waterHeight"]
    kw["midLand"] = trainingData["heightDifference"]
    kw["ratioMid"] = trainingData["wlratio"]
    trainingData = measure_water_level("high.jpg", configObj)
    kw["highWater"] = trainingData["waterHeight"]
    kw["highLand"] = trainingData["heightDifference"]
    kw["ratioHigh"] = trainingData["wlratio"]
    setup_config_file(**kw)
    configObj = read_config_file()
    if configObj["debug"]: sys.stdout.write("Trained Config: {}\n".format(configObj))
    # measure_water_level("mid1.jpg", configObj)

def test_images(**kw):
    configObj = read_config_file()
    configObj["debug"] = kw["debug"]
    configObj["training"] = False
    if configObj["debug"]: sys.stdout.write("Config: {}\n".format(configObj))
    level = measure_water_level(kw["f1"], configObj)
    print(level)

def test_images_function(arguments):
    configObj = read_config_file()
    configObj["training"] = False
    configObj["debug"] = arguments["debug"]
    if configObj["debug"]: sys.stdout.write("Config: {}\n".format(configObj))
    level = measure_water_level(arguments["f1"], configObj)
    return level

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

def get_image_crop_height(img, debug):
    """
    Function to get the height pixel value to crop the image

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
            #if reset:
                #print(i)
                #print("Pixel Match: " + str(pixel_match))
                #print("Ratio: " + str(pixel_match/tank_width))
            if (pixel_match / tank_width) < 0.8 and reset:
                #print("Pixel Match: " + str(pixel_match))
                #print("Ratio: " + str(pixel_match/tank_width))
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
            # print("Count : " + str(testing.count(1)) + " Ratio: " + str(testing.count(1)/tank_width) + " Index: " + str(i))
            if 0.3 < (testing.count(1)/tank_width) < 0.43:
                water_level = i
                flag = False
    if debug: sys.stdout.write("Land Level: " + str(land_level) + "\n")
    if debug: sys.stdout.write("Tank bottom: " + str(tank_bottom) + "\n")
    land_height = tank_bottom - land_level
    if debug: sys.stdout.write("Land Height: " + str(land_height) + "\n")
    if debug: sys.stdout.write("Water Level: " + str(water_level) + "\n")
    if debug: sys.stdout.write("Water Height: " + str(tank_bottom - water_level) + "\n")
    # if debug: sys.stdout.write("Image Height: {}\n".format(image_height))
    return {"land": land_level, "water": water_level, "base": tank_bottom, "top": fishtank_top}

    #return image_height

def find_heights(crop_img, image_height, debug):
    """
    Function to find the land, water, and fishtank base heights

    Parameters:
        crop_img (image): OpenCV Image type cropped image
        image_height (int): Pixel value for height of image
        debug (bool): Debug Mode

    Returns:
        (dict): {"land": xxx, "water": xxx, "base": xxx}
    """
    water_height = 0
    land_height = -1
    fishtank_base = -1
    for i in range(0, 255 - image_height):
        pixel_match = 0
        for j in range(0, 255):
            if land_height == -1 and crop_img[i][j] == 255:
                land_height = i
            if crop_img[i][j] == 0:
                pixel_match += 1
                fishtank_base = i
                #if j < 20:
                #    water_height = i
        # Testing to see if water level has been reached

        if 0.3 < (pixel_match / 255) < 0.6 and water_height < i:
            # print("Matching pixels: " + str(pixel_match) + " water_height: " + str(water_height))
            water_height = i
    if abs(fishtank_base - water_height) < 3:
        fishtank_base = 255 - image_height
    if debug: sys.stdout.write("Fishtank Base Height Pixel Value: {}\n".format(fishtank_base))
    if debug: sys.stdout.write("Water Level Pixel Value: {}\n".format(water_height))
    if debug: sys.stdout.write("Top of the Land Pixel Value: {}\n".format(land_height))
    return {"land": land_height, "water": water_height, "base": fishtank_base}

def measure_water_level(image_name, configObj):
    """
    Function to detect water level

    Parameters:
        image_name (str): Image Name
        configObj (dict): Configuration Object
    """
    if configObj["training"]:
        img = convert_to_greyscale(os.path.join(os.getcwd(), "images", "training", image_name), configObj["debug"])
    else:
        img = convert_to_greyscale(os.path.join(os.getcwd(), "images", "testing", image_name), configObj["debug"])
    #image_height = get_image_crop_height(img, configObj["debug"])
    dict_pixel_height = get_image_crop_height(img, configObj["debug"])
    # cropping the image
    #crop_img = img[image_height:255, 0:255]
    #cv2.imwrite(os.path.join(os.getcwd(), "images", "intermediate", "croppedImage.png"), crop_img)
    #dict_pixel_height = find_heights(crop_img, image_height, configObj["debug"])
    #"land": image_height, "water": water_level, "base": tank_bottom, "top": fishtank_top

    tank_height = dict_pixel_height["base"] - dict_pixel_height["top"]
    scaling_factor = tank_height/255;
    land_height = scaling_factor * (dict_pixel_height["base"] - dict_pixel_height["land"])
    water_height = scaling_factor * (dict_pixel_height["base"] - dict_pixel_height["water"])
    #diff = dict_pixel_height["water"] - dict_pixel_height["land"]
    #waterHeight = (dict_pixel_height["base"] - dict_pixel_height["water"])/dict_pixel_height["base"]
    #heightDifference = diff/dict_pixel_height["base"]

    if configObj["debug"]: sys.stdout.write("Land and Water Height Difference: {} \n".format(land_height - water_height))
    if configObj["debug"]: sys.stdout.write("Scaling Ratio of Height Difference between land and water: {}\n".format((land_height - water_height)/ tank_height))
    if configObj["debug"]: sys.stdout.write("Scaling Ratio of Water Height: {}\n".format(water_height/ tank_height))
    if configObj["debug"]: sys.stdout.write("Ratio Water/Land: {}\n".format(water_height/land_height))

    if configObj["debug"] and not configObj["training"]:
        cv2.imshow("GreyImage", img)
        # cv2.imshow("Crop", crop_img)
        cv2.waitKey()


    if configObj["training"]:
        return {"waterHeight": round(water_height/ tank_height, 3), "heightDifference": round((land_height - water_height)/ tank_height, 3), "wlratio": round(water_height/land_height,3) }
    else:

        predicted_level = []
        if (water_height/ tank_height) < configObj["waterHeightMid"]:
            predicted_level.append("green")
        elif (water_height/ tank_height) < configObj["waterHeightHigh"]:
            predicted_level.append("yellow")
        else:
            predicted_level.append("red")

        if ((land_height - water_height)/ tank_height) > configObj["heightDifferenceMid"]:
            predicted_level.append("green")
        elif ((land_height - water_height)/ tank_height) > configObj["heightDifferenceHigh"]:
            predicted_level.append("yellow")
        else:
            predicted_level.append("red")

        if water_height/land_height < configObj["waterLandRatioMid"]:
            predicted_level.append("green")
        elif water_height/land_height < configObj["waterLandRatioHigh"]:
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

    parser = argparse.ArgumentParser(description="Raspberry Pi Water Tank Demo", prog="pi")
    subparsers = parser.add_subparsers()

    capture_parser = subparsers.add_parser("capture", help="Capture Images")
    capture_parser.add_argument("out", help="Image Name")
    capture_parser.set_defaults(func=capture_images)

    test_parser = subparsers.add_parser("test", help="Test images")
    test_parser.add_argument("--debug", action='store_true', default=False, help="Debug Mode")
    test_parser.add_argument("f1", help="Image Name")
    test_parser.set_defaults(func=test_images)

    train_parser = subparsers.add_parser("train", help="Train Images")
    train_parser.add_argument("--debug", action='store_true', default=False, help="Debug Mode")
    train_parser.set_defaults(func=train_images)

    args = parser.parse_args()
    try:
        args.func(**vars(args))
    except Exception as e:
        print(e)
        parser.print_help()
