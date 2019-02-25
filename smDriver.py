import RPi.GPIO as GPIO
from time import sleep

DIR = 21 # Direction Pin
STEP = 20 # Step Pin
STEP_CNT = 360

GPIO.setmode(GPIO.BCM)

GPIO.setup(DIR,GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

GPIO.output(DIR, GPIO.LOW)

stepperOne = GPIO.PWM(STEP,200) # 200 ticks per second

# Spin continuously
try:
	while(True):
		stepperOne.start(50) # 50 duty cycle		
except KeyboardInterrupt:
	print("Clean up")
	GPIO.cleanup()
	stepperOne.stop()
