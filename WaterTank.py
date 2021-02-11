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
from PIL import Image, ImageOps
import cv2
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt

debug = True

def capture_images(**kw):
    camera = picamera.PiCamera()
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
    if debug: sys.stdout.write("Writing images to: {}\n".format(os.path.join(os.getcwd(), "Images", test_image)))
    camera.capture(os.path.join(os.getcwd(), "Images",test_image))
    camera.stop_preview()

def convert_to_greyscale(**kw):
    im1 = Image.open(os.path.join(os.getcwd(), "Images", kw["f"]))
    im2 = ImageOps.grayscale(im1)
    im2.save(os.path.join(os.getcwd(), "Images", "greyscale" + ".jpg"))

def compare_two_images(**kw):
    try:
        original =  cv2.imread(os.path.join(os.getcwd(), "Images", kw["f1"]))
        duplicate =  cv2.imread(os.path.join(os.getcwd(), "Images", kw["f2"]))

        if original.shape == duplicate.shape:
            if debug: sys.stdout.write("Color images have same size and channels\n")

        difference = cv2.subtract(original, duplicate)

        b, g, r = cv2.split(difference)
        if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
            if debug: sys.stdout.write("Color images are completely Equal")
        else:
            if debug: sys.stdout.write("blue difference: {}\n".format(cv2.countNonZero(b)))
            if debug: sys.stdout.write("green difference: {}\n".format(cv2.countNonZero(g)))
            if debug: sys.stdout.write("red difference: {}\n".format(cv2.countNonZero(r)))
    except Exception as e:
        sys.stderr.write("compare_two_images: " + str(e))

def find_image_contours(**kw):
    print(os.path.join(os.getcwd(), "Images", kw["f"]))
    image = cv2.imread(os.path.join(os.getcwd(), "Images", kw["f"]))
    # convert to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # create a binary thresholded image
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    # show it
    plt.imshow(binary, cmap="gray")
    plt.show()
    '''
    # find the contours from the thresholded image
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # draw all contours
    image = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    # show the image with the drawn contours
    plt.imshow(image)
    plt.show()
    '''

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Raspberry Pi Water Tank Demo", prog="pi")
    subparsers = parser.add_subparsers()

    capture_parser = subparsers.add_parser("capture", help="Capture Images")
    capture_parser.add_argument("out", help="Image Name")
    capture_parser.set_defaults(func=capture_images)

    grey_parser = subparsers.add_parser("grey", help="Convert images to greyscale")
    grey_parser.add_argument("--f", metavar="", default="snapshot.jpg", help="Image to covert to greyscale")
    grey_parser.set_defaults(func=convert_to_greyscale)

    contour_parser = subparsers.add_parser("cont", help="Find Image Contour")
    contour_parser.add_argument("--f", metavar="", default="snapshot.jpg", help="Image to covert to greyscale")
    contour_parser.set_defaults(func=find_image_contours)

    compare_parser = subparsers.add_parser("compare", help="Convert two images")
    compare_parser.add_argument("f1", help="First Image")
    compare_parser.add_argument("f2", help="Second Image")
    compare_parser.set_defaults(func=compare_two_images)

    args = parser.parse_args()
    try:
        args.func(**vars(args))
    except Exception as e:
        print(e)
        parser.print_help()
