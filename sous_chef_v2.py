# sous_chef_v2.py
# Ryan Hua and Kofi Dinizulu
# Currently only handles one container
# As we continue to prototype the device,
# we will change and optimize the code to handle
# a total of six containers.

# no need for calibration

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

    


    # calibrate for 5 seconds
    # instead of letting out a divet's worth of 
    # ingredients, we will "shake" the container instead
    timeout = 5 # amount of seconds
    stepperOne.ChangeDutyCycle(50)
    timeout_start = time.time()
    while (time.time() < timeout_start + timeout):
        GPIO.output(DIR,GPIO.HIGH)
        time.sleep(.5)
        GPIO.output(DIR,GPIO.LOW)
        time.sleep(.5)

    stepperOne.ChangeDutyCycle(0)

    # let crumbs and last bit to fall
    time.sleep(1)

    # get value in grams
    val = hx.get_weight(5)
    print(val, "grams after 5 seconds")
    # rate at which the ingredient falls.
    FOOD_RATE_ONE = toZero(val) / float(5)
    # hx reset
    hx.power_down()
    hx.power_up()

def handleDispense():
    
    stepperOne.ChangeDutyCycle(50)
    GPIO.output(DIR,GPIO.HIGH)
    time.sleep(.25)
    GPIO.output(DIR,GPIO.LOW)
    time.sleep(.25)
    stepperOne.ChangeDutyCycle(0)
    time.sleep(.2)

class MotorEcho(WebSocket):
    def handleMessage(self):
        # reset the load cell
        hx.tare()

        # loads JSON Object into a python array
        ingredients = json.loads(self.data)
            
        # Amount of time needed to sleep
        desired_grams = ingredients[0]['grams']

        # current amount on the scale
        # should have been tared to 0
        val = 0
        prev_val = 0

        while (val + 5 < desired_grams)
            handleDispense()
            prev_val = val
            val = toZero(hx.get_weight(5))
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
ONE_PADDLE_DIVET = float(1)/8

# server setup
server = SimpleWebSocketServer('10.1.250.128', 8000, MotorEcho)

try:
    server.serveforever()
except KeyboardInterrupt:
    GPIO.cleanup()
    cleanAndExit()