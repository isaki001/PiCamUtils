#!/usr/bin/env	python3

# For working with Python Camera: https://medium.com/@petehouston/capture-images-from-raspberry-pi-camera-module-using-picamera-505e9788d609
# TODO:Test the below codes
# https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
# https://www.pyimagesearch.com/2017/06/19/image-difference-with-opencv-and-python/
# https://www.thepythoncode.com/article/contour-detection-opencv-python: Contour Detection

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

from configmanagement import setup_config_file
from configmanagement import read_config_file


def capture_images(**kw):
    camera = picamera.PiCamera()
    camera.resolution = (256, 256)
    if not os.path.exists(os.path.join(os.getcwd(), "images")):
        os.mkdir(os.path.join(os.getcwd(), "images"))
    if not os.path.exists(os.path.join(os.getcwd(), "images", "training")):
        os.mkdir(os.path.join(os.getcwd(), "images", "training"))
    camera.start_preview()
    time.sleep(2)
    text = None
    while text != "":
        text = input("Hit Enter to capture image")
    sys.stdout.write("Writing images to: {}\n".format(os.path.join(os.getcwd(), "images", "training", kw["out"])))
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
    trainingData = measure_water_level("mid.jpg", configObj)
    kw["midWater"] = trainingData["waterHeight"]
    kw["midLand"] = trainingData["heightDifference"]
    setup_config_file(**kw)
    configObj = read_config_file()
    if configObj["debug"]: sys.stdout.write("Trained Config: {}\n".format(configObj))
    # measure_water_level("mid1.jpg", configObj)

def test_images(**kw):
    configObj = read_config_file()
    configObj["training"] = False
    if configObj["debug"]: sys.stdout.write("Config: {}\n".format(configObj))
    level = measure_water_level(kw["f1"], configObj)
    print(level)

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
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
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
    flag = False
    for i in range(0, 255):
        pixel_match = 0
        if flag:
            break
        else:
            for j in range(0, 255):
                # Checking for water pixels by discarding the top rows of the image
                if i > 50 and img[i][j] == 255:
                    pixel_match += 1
            # Checking to make sure the water pixels are more than 10% of the entire width
            if (pixel_match / 255) > 0.1:
                image_height = i
                flag = True
    if debug: sys.stdout.write("Image Height: {}\n".format(image_height))
    return image_height

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
                if j < 20:
                    water_height = i
        # Testing to see if water level has been reached
        if 0.3 < (pixel_match / 255) < 0.6 and water_height < i:
            water_height = i
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
    image_height = get_image_crop_height(img, configObj["debug"])

    # cropping the image
    crop_img = img[image_height:255, 0:255]
    cv2.imwrite(os.path.join(os.getcwd(), "images", "intermediate", "croppedImage.png"), crop_img)
    dict_pixel_height = find_heights(crop_img, image_height, configObj["debug"])
    diff = dict_pixel_height["water"] - dict_pixel_height["land"]
    waterHeight = (dict_pixel_height["base"] - dict_pixel_height["water"])/dict_pixel_height["base"]
    heightDifference = diff/dict_pixel_height["base"]
    if configObj["debug"]: sys.stdout.write("Land and Water Height Difference: {} \n".format(diff))
    if configObj["debug"]: sys.stdout.write("Scaling Ratio of Height Difference between land and water: {}\n".format(heightDifference))
    if configObj["debug"]: sys.stdout.write("Scaling Ratio of Water Height: {}\n".format(waterHeight))
    #if configObj["debug"] and not configObj["training"]:
    #    cv2.imshow("GreyImage", img)
    #    cv2.imshow("Crop", crop_img)
    #    cv2.waitKey()
    if configObj["training"]:
        return {"waterHeight": waterHeight, "heightDifference": heightDifference}
    else:
        if waterHeight < configObj["waterHeightMid"]:
            return {"level": "low", "led": "green"}
        elif waterHeight < configObj["waterHeightHigh"]:
            return {"level": "mid", "led": "yellow"}
        else:
            return {"level": "high", "led": "red"}

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
