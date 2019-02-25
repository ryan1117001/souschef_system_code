# calibration.py
# Ryan Hua and Kofi Dinizulu
# Will attempt to get only one set of dispenser, motor, and load cell to work
# others will be made later

import RPi.GPIO as GPIO
import json
import time
import sys
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from time import sleep
from hx711 import HX711


def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()


hx = HX711(14, 15)


class MotorEcho(WebSocket):
    def handleMessage(self):
        # loads JSON Object into a python array
        ingredients = json.loads(self.data)
        print(ingredients)

        # move motor
        stepperOne.start(50)
        time.sleep(3)
        stepperOne.stop()

        # get value in grams
        val = hx.get_weight(5)
        print(val)

        # hx reset
        hx.power_down()
        hx.power_up()

        # send packet
        self.sendMessage("Completed")

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')
        cleanAndExit()


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

# server setup
server = SimpleWebSocketServer('10.1.250.128', 8000, MotorEcho)

try:
    server.serveforever()
except KeyboardInterrupt:
    GPIO.cleanup()
    cleanAndExit()