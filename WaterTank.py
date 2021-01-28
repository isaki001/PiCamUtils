#!/usr/bin/env	python3

# For working with Python Camera: https://medium.com/@petehouston/capture-images-from-raspberry-pi-camera-module-using-picamera-505e9788d609

import picamera
import os
import argparse
import sys

debug = True

def capture_images():
    camera = picamera.PiCamera()
    if not os.path.exists(os.path.join(os.getcwd(), "Images")):
        os.mkdir(os.path.join(os.getcwd(), "Images"))
    images = os.listdir(os.path.join(os.getcwd(), "Images"))
    test_image = "snapshot.jpg"
    count = 0
    if debug: sys.stdout.write("images {}\n".format(images))
    for image in images:
        if ("snapshot" + str(count) + ".jpg") == image:
            if debug: sys.stdout.write("matching image : {}\n".format(image))
            count += 1
        else:
            if debug: sys.stdout.write("not matching image : {}\n".format(image))
    test_image = "snapshot" + str(count) + ".jpg"

    if debug: sys.stdout.write("Writing images to: {}\n".format(os.path.join(os.getcwd(), "Images",test_image)))
    camera.capture(os.path.join(os.getcwd(), "Images",test_image))

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
