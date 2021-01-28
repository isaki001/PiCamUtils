#!/usr/bin/env	python3

# For working with Python Camera: https://medium.com/@petehouston/capture-images-from-raspberry-pi-camera-module-using-picamera-505e9788d609

import picamera
import os
import argparse
import sys
import re
import time
from PIL import Image, ImageOps
import cv2
import numpy as np
from skimage.measure import structural_similarity as ssim

debug = True

def capture_images():
    camera = picamera.PiCamera()
    if not os.path.exists(os.path.join(os.getcwd(), "Images")):
        os.mkdir(os.path.join(os.getcwd(), "Images"))
    images = os.listdir(os.path.join(os.getcwd(), "Images"))
    if debug: sys.stdout.write("images {}\n".format(images))
    count = 0
    for image in images:
        match = re.findall(r'\d+', image)
        if debug: sys.stdout.write("digit from image: {}\n".format(match))
        if match and int(match[0]) >= count:
            count = int(match[0]) + 1

    test_image = "snapshot" + str(count) + ".jpg"

    camera.start_preview()
    time.sleep(2)
    if debug: sys.stdout.write("Writing images to: {}\n".format(os.path.join(os.getcwd(), "Images", test_image)))
    camera.capture(os.path.join(os.getcwd(), "Images",test_image))
    camera.stop_preview()

def convert_to_greyscale():
    images = os.listdir(os.path.join(os.getcwd(), "Images"))
    for image in images:
        im1 = Image.open(os.path.join(os.getcwd(), "Images", image))
        # applying greyscale method
        im2 = ImageOps.grayscale(im1)
        im2.show()
        match = re.findall(r'\d+', image)
        if match:
            im2.save(os.path.join(os.getcwd(), "Images", "greyscale" + match[0] + ".jpg"))
        else:
            im2.save(os.path.join(os.getcwd(), "Images", "greyscale" + ".jpg"))

def compare_two_images():
    original =  cv2.imread(os.path.join(os.getcwd(), "Images", "snapshot3.jpg"))
    duplicate =  cv2.imread(os.path.join(os.getcwd(), "Images", "snapshot4.jpg"))

    grey_original =  cv2.imread(os.path.join(os.getcwd(), "Images", "greyscale3.jpg"))
    grey_duplicate =  cv2.imread(os.path.join(os.getcwd(), "Images", "greyscale4.jpg"))

    if original.shape == duplicate.shape:
        if debug: sys.stdout.write("Color images have same size and channels\n")
    if grey_original.shape == grey_duplicate.shape:
        if debug: sys.stdout.write("Greyscale images have same size and channels\n")

    difference = cv2.subtract(original, duplicate)
    difference_grey = cv2.subtract(grey_original, grey_duplicate)

    b, g, r = cv2.split(difference)
    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
        if debug: sys.stdout.write("Color images are completely Equal")
    else:
        if debug: sys.stdout.write("Color blue difference: {}\n".format(cv2.countNonZero(b)))
        if debug: sys.stdout.write("Color green difference: {}\n".format(cv2.countNonZero(g)))
        if debug: sys.stdout.write("Color red difference: {}\n".format(cv2.countNonZero(r)))

    b, g, r = cv2.split(difference_grey)
    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
        if debug: sys.stdout.write("Greyscale images are completely Equal")
    else:
        if debug: sys.stdout.write("Greyscale blue difference: {}\n".format(cv2.countNonZero(b)))
        if debug: sys.stdout.write("Greyscale green difference: {}\n".format(cv2.countNonZero(g)))
        if debug: sys.stdout.write("Greyscale red difference: {}\n".format(cv2.countNonZero(r)))

'''
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Raspberry Pi Water Tank Demo", prog="pi")
    subparsers = parser.add_subparsers()

    deleted_parser = subparsers.add_parser("capture", help="Capture Images")
    deleted_parser.set_defaults(func=capture_images)

    args = parser.parse_args()
    try:
        args.func(**vars(args))
    except Exception as e:
        print(e)
        parser.print_help()
'''

# capture_images()
# convert_to_greyscale()
compare_two_images()
