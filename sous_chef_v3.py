# sous_chef_v3.py
# Ryan Hua and Kofi Dinizulu
# Handles six containers 

# calibrated to 1 gram

import RPi.GPIO as GPIO
import json
import time
import sys
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from time import sleep
from hx711 import HX711

# if the mass less than zero, it should be zero
def toZero(number):
    if (number < 0):
        return 0
    else:
        return number

# clean up the pins
def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    for stepper in steppers:
        stepper.stop()
    print "Bye!"
    sys.exit()

# will need to work on this part
def handleDispense(ID):
    steppers[ID].ChangeDutyCycle(50)
    GPIO.output(DIRS[ID], GPIO.HIGH)
    time.sleep(.25)
    GPIO.output(DIRS[ID], GPIO.LOW)
    time.sleep(.25)
    steppers[ID].ChangeDutyCycle(0)
    time.sleep (.1)

class MotorControl(WebSocket):
    def handleMessage(self):
        # loads JSON Object into a python array
        ingredients = json.loads(self.data)
        for ingredient in ingredients:
            if (ingredient['enable']):
                ID = ingredient['id']
                desired_grams = ingredient['grams']
                cur_grams = 0
                prev_grams = 0
                
                while (cur_grams <= desired_grams):
                    handleDispense(ID)
                    prev_grams = cur_grams
                    cur_grams = toZero(hxs[ID].get_weight(5))
                    if (prev_grams == cur_grams):
                        self.sendMessage("alert")
                        # see what happens if its break instead of return
                        return

                    # hx reset
                    hxs[ID].power_down()
                    hxs[ID].power_up()    

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')
        cleanAndExit()

# HX711 initial pin setup
hx0 = HX711(14,15)
hx1 = HX711(18,23)
hx2 = HX711(24,25)
hx3 = HX711(12,16)
hx4 = HX711(6,13)
hx5 = HX711(19,26)

# hx tuple
hxs = (hx0, hx1, hx2, hx3, hx4, hx5)


for hx in hxs:
    # on how the data is read
    hx.set_reading_format("MSB", "MSB")

    # hx weight reference. Set to 1 gram
    hx.set_reference_unit(3177)

# using pin names instead of pin location on RPI
GPIO.setmode(GPIO.BCM)

# stepper motor pin constants
STEP0 = 20
STEP1 = 11
STEP2 = 10
STEP3 = 22
STEP4 = 17
STEP5 = 2

# stepper tuple
STEPS = (STEP0, STEP1, STEP2, STEP3, STEP4, STEP5)

# direction pin constants
DIR0 = 21
DIR1 = 5
DIR2 = 9
DIR3 = 27
DIR4 = 4
DIR5 = 3

# direction tuple
DIRS = (DIR0, DIR1, DIR2, DIR3, DIR4, DIR5)

for DIR in DIRS:
    # GPIO dircition pin setup
    GPIO.setup(DIR, GPIO.OUT)
    # GPIO initialize
    GPIO.output(DIR, GPIO.LOW)

# GPIO pin setup
for STEP in STEPS:
    GPIO.setup(STEP, GPIO.OUT)

# 200 ticks per second = 1 revolution per second
stepper0 = GPIO.PWM(STEP0, 200)
stepper1 = GPIO.PWM(STEP1, 200)
stepper2 = GPIO.PWM(STEP2, 200)
stepper3 = GPIO.PWM(STEP3, 200)
stepper4 = GPIO.PWM(STEP4, 200)
stepper5 = GPIO.PWM(STEP5, 200)

# stepper motor tuple
steppers = (stepper0, stepper1, stepper2, stepper3, stepper4, stepper5)

# initiate stepper motors
for stepper in steppers:
    stepper.start(0)


# server setup
server = SimpleWebSocketServer('10.1.250.128', 8000, MotorControl)

try:
    server.serveforever()
except KeyboardInterrupt, SystemError:
    GPIO.cleanup()
    cleanAndExit()