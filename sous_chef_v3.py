# sous_chef_v3.py
# Ryan Hua and Kofi Dinizulu
# Handles six containers

# calibrated to 1 gram

import RPi.GPIO as GPIO
import json
import time
import sys
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from hx711 import HX711

# if the mass less than zero, it should be zero
def toZero(number):
    if (number < 0):
        return 0
    else:
        return number

# clean up the pins
def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()
    for stepper in steppers:
        stepper.stop()
    print("Bye!")
    sys.exit()

# spins the paddle in either clockwise or counterclockwise
def handleDispense(ID, TC, CW):
    steppers[ID].ChangeDutyCycle(50)
    GPIO.output(DIRS[ID], CW)
    time.sleep(TC)
    steppers[ID].ChangeDutyCycle(0)
    time.sleep(.1)

class MotorControl(WebSocket):
    def handleMessage(self):
        # loads JSON Object into a python array
        # {msg: "...", data: {id: ..., grams: ... }}
        msg = json.loads(self.data)
        if (msg["type"] == "dispense"):
            
            # set variables
            ingredient = msg["data"]
            ID = ingredient['id']
            desired_grams = ingredient['grams']
            cur_grams = 0
            prev_grams = 0
            stall = 0
            isCW = True
            
            # tare the load cell, value read will be zero
            hxs[ID].tare()

            # Loop until under two grams of desired or more
            while (desired_grams - cur_grams > 2):
                # spin clockwise or counterclockwise
                if (isCW):
                    handleDispense(ID, TIMECONST[ID], isCW)
                else:
                    handleDispense(ID, TIMECONST[ID], isCW)

                # save the previous weight and retrieve current weight
                prev_grams = cur_grams
                cur_grams = toZero(hxs[ID].get_weight(5))
                print(cur_grams)

                # ingredients tend to get stuck, so to fix it,
                # we give a greater push at the end to try one more time
                if (cur_grams - prev_grams < 2):
                    stall = stall + 1
                    if (stall == 4):
                        if (isCW):
                            handleDispense(ID, TIMECONST[ID] + .2, isCW)
                        else:
                            handleDispense(ID, TIMECONST[ID] + .2, isCW)
                        cur_grams = toZero(hxs[ID].get_weight(5))

                        # if it is still stalled or empty, send a lert message
                        if (cur_grams - prev_grams < 2):
                            alert = json.dumps(
                                {
                                    "type": "alert",
                                    "data": {
                                        "id": ID, "grams": cur_grams}
                                })
                            self.sendMessage(alert)
                            return
                        else:
                            stall = 0
                else:
                    stall = 0
                isCW = not isCW
            # if it gets to this point, the device has sent enough of the ingredient
            completed = json.dumps(
                {"type": "completed",
                 "data": {
                     "id": ID, "grams": cur_grams}
                 })
            self.sendMessage(completed)
            hxs[ID].power_down()
            hxs[ID].power_up()
        else:
            # Can added more message types here
            print("else statement")

    def handleConnected(self):
        # print the address that connected to it
        print(self.address, 'connected')

    def handleClose(self):
        # close and clean up the pins
        print(self.address, 'closed')
        cleanAndExit()


# Time Constants
SPK = 2.25
Nuts = .15
GummyBear = 2.5
Crackers = 1.75
Dates = .75
Raisins = 2.5

# Time constant tuple
TIMECONST = (SPK, Nuts, GummyBear, Crackers, Dates, Raisins)

# HX711 initial pin setup
hx0 = HX711(14, 15)
hx1 = HX711(18, 23)
hx2 = HX711(24, 25)
hx3 = HX711(12, 16)
hx4 = HX711(6, 13)
hx5 = HX711(19, 26)

# valus for ref unit. Should be set to ~200 g
REF0 = -3160.5  # 200.3
REF1 = -3240.0  # 200.5
REF2 = -3318.0  # 200.2
REF3 = -3140.75 # 200.2
REF4 = -3080.25 # 200.5
REF5 = -3185.0  # 200.9

# ref_unit tuple
ref_unit = (REF0, REF1, REF2, REF3, REF4, REF5)

# hx tuple
hxs = (hx0, hx1, hx2, hx3, hx4, hx5)

for x in range(6):
    hxs[x].set_reading_format("MSB", "MSB")

    hxs[x].set_reference_unit(ref_unit[x])

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
server = SimpleWebSocketServer('10.24.0.96', 8000, MotorControl)

try:
    server.serveforever()
except KeyboardInterrupt, SystemError:
    cleanAndExit()
