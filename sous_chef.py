# sous_chef.py
# Ryan Hua and Kofi Dinizulu
# Currently only handles one container
# As we continue to prototype the device,
# we will change and optimize the code to handle
# a total of six containers.

import RPi.GPIO as GPIO
import json
import time
import sys
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from time import sleep
from hx711 import HX711

def toZero(number):
    if (number < 0):
        return 0
    else:
        return number
def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    stepperOne.stop()
    print "Bye!"
    sys.exit()

def handleCalibration():
    stepperOne.ChangeDutyCycle(50)
    time.sleep(ONE_PADDLE_DIVET)
    stepperOne.ChangeDutyCycle(0)

    # let crumbs and last bit to fall
    time.sleep(1)

    # get value in grams
    val = hx.get_weight(5)
    print(val, "grams after one revolution")
    # rate at which the ingredient falls.
    # one revolution is one second
    FOOD_RATE_ONE = toZero(val)
    # hx reset
    hx.power_down()
    hx.power_up()

def handleDispense(inputted_grams):
    
    drop_time = inputted_grams / FOOD_RATE_ONE

    # May need to figure out a way to close it
    close_time = drop_time % ONE_PADDLE_DIVET
    
    print(close_time)
    
    # move motor
    stepperOne.ChangeDutyCycle(50)
    time.sleep(drop_time)
    stepperOne.ChangeDutyCycle(0)

    # to close the opening in the paddle
    GPIO.output(DIR, GPIO.HIGH)
    stepperOne.ChangeDutyCycle(50)
    time.sleep(close_time)
    stepperOne.ChangeDutyCycle(0)
    GPIO.output(DIR, GPIO.LOW)

    # let crumbs/ingredient to fall
    time.sleep(1)

class MotorEcho(WebSocket):
    def handleMessage(self):
        # reset the load cell
        hx.tare()

        # if statement to see which button was pressed
        if (self.data == "calibration"):
            handleCalibration()
        else:
            # loads JSON Object into a python array
            ingredients = json.loads(self.data)
            
            # Amount of time needed to sleep
            desired_grams = ingredients[0]['grams']
 
            # current amount on the scale
            # should have been tared to 0
            val = 0

            # previous value on the scale
            prev_val = 0

            # dispenses within a margiin of 10 grams
            # may want to look into this

            while (val < desired_grams - 5):
                handleDispense(desired_grams - val)
    
                # current val to prev_val
                prev_val = val
                print(prev_val, val)
                # get value in grams
                val = toZero(hx.get_weight(5))
                print(val, "grams")

                if (prev_val == val):
                    self.sendMessage("alert")
                    return

            # hx reset
            hx.power_down()
            hx.power_up()
        
        # send packet
        self.sendMessage("completed")

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')
        cleanAndExit()


# HX711 initial pin setup
hx = HX711(14, 15)

# bit order
hx.set_reading_format("MSB", "MSB")

# weight reference
hx.set_reference_unit(3177)

# hx setup
hx.tare()

# motor constants
DIR = 21 # Direction Pin
STEP = 20 # Step Pin

# motor pin setup
GPIO.setmode(GPIO.BCM) # Uses pin names instead of pin location on RPI

GPIO.setup(DIR,GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

GPIO.output(DIR, GPIO.LOW)

# 200 ticks per second = 1 revolution per second
stepperOne = GPIO.PWM(STEP, 200)
stepperOne.start(0)

# Ingredient grams / ONE_PADDLE_DIVET
# This equates to the amount of food that comes out at one paddle divet
FOOD_RATE_ONE = 1

# Time constants for the motor
ONE_PADDLE_DIVET = float(1)/6

# server setup
server = SimpleWebSocketServer('10.1.250.128', 8000, MotorEcho)

try:
    server.serveforever()
except KeyboardInterrupt:
    GPIO.cleanup()
    cleanAndExit()