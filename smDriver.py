import RPi.GPIO as GPIO
from time import sleep

DIR = 21 # Direction Pin
STEP = 20 # Step Pin
STEP_CNT = 360

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR,GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, GPIO.LOW)

try:
	for x in range(360):
		GPIO.output(STEP, GPIO.HIGH)
		sleep(.03)
		GPIO.output(STEP, GPIO.LOW)
		sleep(.03)
except KeyboardInterrupt:
	print("Clean up")
	GPIO.cleanup()
