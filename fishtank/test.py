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
'''


def blink(pin):
	 GPIO.setmode(GPIO.BOARD)
	 GPIO.setup(pin, GPIO.OUT)
	 GPIO.output(pin, GPIO.HIGH)

def turnOff(pin):
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)

def redOn():
	blink(redPin)

def greenOn():
	blink(greenPin)

def blueOn():
	blink(bluePin)

def yellowOn():
	blink(redPin)
	blink(greenPin)

def cyanOn():
	blink(greenPin)
	blink(bluePin)

def magentaOn():
	blink(redPin)
	blink(bluePin)

def whiteOn():
	blink(redPin)
	blink(greenPin)
	blink(bluePin)

def redOff():
	turnOff(redPin)

def greenOff():
	turnOff(greenPin)

def blueOff():
	turnOff(bluePin)

def yellowOff():
	turnOff(redPin)
	turnOff(greenPin)

def cyanOff():
	turnOff(greenPin)
	turnOff(bluePin)

def magentaOff():
	turnOff(redPin)
	turnOff(bluePin)

def whiteOff():
	turnOff(redPin)
	turnOff(greenPin)
	turnOff(bluePin)

def main():
	while True:
		cmd = raw_input("Choose an option:")
		if cmd == "red on":
			redOn()
		elif cmd == "red off":
				redOff()

		elif cmd == "green on":
			greenOn()

		elif cmd == "green off":
			greenOff()

		elif cmd == "blue on":
			blueOn()

		elif cmd == "blue off":
			blueOff()

		elif cmd == "yellow on":
			yellowOn()

		elif cmd == "yellow off":
			yellowOff()

		elif cmd == "cyan on":
			cyanOn()

		elif cmd == "cyan off":
			cyanOff()

		elif cmd == "magenta on":
			magentaOn()

		elif cmd == "magenta off":
			magentaOff()

		elif cmd == "white on":
			whiteOn()

		elif cmd == "white off":
			whiteOff()

		elif cmd == "exit":
			return

		else:
			print("Not a valid command.")
