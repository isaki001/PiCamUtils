#!/usr/bin/env	python3

# For working with Python Camera: https://medium.com/@petehouston/capture-images-from-raspberry-pi-camera-module-using-picamera-505e9788d609

import picamera
import os
import argparse
import sys
import re
import time
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

capture_images()
