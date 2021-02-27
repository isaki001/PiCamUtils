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

debug = True

def capture_images(**kw):
    camera = picamera.PiCamera()
    camera.resolution = (256, 256)
    if not os.path.exists(os.path.join(os.getcwd(), "Images")):
        os.mkdir(os.path.join(os.getcwd(), "Images"))
    if not kw["out"]:
        images = os.listdir(os.path.join(os.getcwd(), "Images"))
        if debug: sys.stdout.write("images {}\n".format(images))
        count = 0
        for image in images:
            match = re.findall(r'\d+', image)
            if debug: sys.stdout.write("digit from image: {}\n".format(match))
            if match and int(match[0]) >= count:
                count = int(match[0]) + 1
        test_image = "snapshot" + str(count) + ".jpg"
    else:
        test_image = kw["out"]
    camera.start_preview()
    time.sleep(2)
    text = None
    while text != "":
        text = input("Hit Enter to capture image")
    if debug: sys.stdout.write("Writing images to: {}\n".format(os.path.join(os.getcwd(), "Images", test_image)))
    camera.capture(os.path.join(os.getcwd(), "Images",test_image))
    camera.stop_preview()

def convert_to_greyscale(**kw):
    im1 = Image.open(os.path.join(os.getcwd(), "Images", kw["f"]))
    im2 = ImageOps.grayscale(im1)
    im2.save(os.path.join(os.getcwd(), "Images", "greyscale" + ".jpg"))

def train_images(**kw):
    print_image_details(os.path.join(os.getcwd(), "FishTankImages", "training", "Fishtank_Low.jpg"))
    # print_image_details(os.path.join(os.getcwd(), "FishTankImages", "training", "Fishtank_Low1.jpg"))
    # print_image_details(os.path.join(os.getcwd(), "FishTankImages", "training", "Fishtank_Mid.jpg"))
    #print_image_details(os.path.join(os.getcwd(), "FishTankImages", "training", "Fishtank_Mid_1.jpg"))

def test_images(**kw):
    print_image_details(os.path.join(os.getcwd(), "FishTankImages", "test", kw["f1"]))


def print_image_details(a):
    a = cv2.imread(a)
    # convert to grayscale
    a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    # create a binary thresholded image
    a = cv2.GaussianBlur(a,(5,5),0)
    _, a = cv2.threshold(a, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    cv2.imwrite(os.path.join(os.getcwd(), "Images", "GreyImage.png"), a)

    flag = False
    for i in range(0, 255):
        truth = 0
        if flag:
            break
        else:
            for j in range(0, 255):
                if i > 50 and a[i][j] == 255:
                    truth += 1
            if (truth/255) > 0.1:
                image_height = i
                flag = True

    print("Image Height:" + str(image_height))
    crop_img = a[image_height:255, 0:255]
    cv2.imwrite(os.path.join(os.getcwd(), "Images", "CroppedImage.png"), crop_img)

    water_height = 0
    land_height = -1
    image_lower_limit = -1
    for i in range(0, 255 - image_height):
        pixel_match = 0
        for j in range(0, 255):
            if land_height == -1 and crop_img[i][j] == 255:
                land_height = i
            if crop_img[i][j] == 0:
                pixel_match += 1
                image_lower_limit = i
                if j < 20:
                    water_height = i
        # Testing to see if water level has been reached
        if 0.3 < (pixel_match / 255) < 0.6 and water_height < i:
            water_height = i

    print("Image Lower Limit: " + str(image_lower_limit))
    print("Image Water Height: " + str(water_height))
    print("Image Land Height: " + str(land_height))
    diff = water_height - land_height
    print("Land Water Height Difference: " + str(diff))
    print("Scaling Ratio of Height Difference between land and water: " + str(diff/(image_lower_limit)))
    print("Scaling Ratio of Water Height: " + str((image_lower_limit-water_height)/(image_lower_limit)))
    cv2.imshow("GreyImage", a)
    cv2.imshow("Crop", crop_img)
    cv2.waitKey()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Raspberry Pi Water Tank Demo", prog="pi")
    subparsers = parser.add_subparsers()

    capture_parser = subparsers.add_parser("capture", help="Capture Images")
    capture_parser.add_argument("out", help="Image Name")
    capture_parser.set_defaults(func=capture_images)

    compare_parser = subparsers.add_parser("test", help="Test images")
    compare_parser.add_argument("f1", help="First Image")
    compare_parser.set_defaults(func=test_images)

    train_parser = subparsers.add_parser("train", help="Train Images")
    train_parser.set_defaults(func=train_images)

    args = parser.parse_args()
    try:
        args.func(**vars(args))
    except Exception as e:
        print(e)
        parser.print_help()
