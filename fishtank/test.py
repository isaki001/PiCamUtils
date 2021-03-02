#!/usr/bin/env	python3
from gpiozero import LED
import time
from watertank import test_images_function

redPin   = LED(4)
yellowPin = LED(17)
greenPin  = LED(22)

option = 1


redPin.on()
yellowPin.on()
greenPin.on()
print("LED Done")
time.sleep(3)
redPin.off()
yellowPin.on()
greenPin.on()

'''
led = ["green", "yellow", "red"]

print("Image Name   ::  Predicted ::  Actual")
for i in range(1, 22):
	if i != 15 and i != 16:
		filler = str(i)
		image_name = "testImage" + filler + ".jpg"
		level = test_images_function({'debug': False, 'f1': image_name})
		if i < 6:
			led_light = "green"
		elif i < 13:
			led_light = "yellow"
		else:
			led_light = "red"

		print("Image: " + str(image_name) +  "  :: " + level["led"] + " :: "+ led_light)
