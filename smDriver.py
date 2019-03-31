import RPi.GPIO as GPIO
import json
import time
import sys

# will need to work on this part
def handleDispense(ID):
    steppers[ID].ChangeDutyCycle(50)
    GPIO.output(DIRS[ID], GPIO.HIGH)
    time.sleep(.25)
    GPIO.output(DIRS[ID], GPIO.LOW)
    time.sleep(.25)
    steppers[ID].ChangeDutyCycle(0)
    time.sleep (.1)

# clean up the pins
def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    for stepper in steppers:
        stepper.stop()
    print "Bye!"
    sys.exit()

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

# Spin continuously
try:
	while(True):
		for ID in range(6):
			print(ID)
			handleDispense(ID)
			time.sleep(1)		
except KeyboardInterrupt:
	cleanAndExit()
