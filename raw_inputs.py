# raw_inputs.py
# Ryan Hua and Kofi Dinizulu
# List six raw inputs
# to read the calibration values.

import time
import sys

EMULATE_HX711=False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print "Cleaning..."

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print "Bye!"
    sys.exit()

# HX711 initial pin setup
hx0 = HX711(14,15)
hx1 = HX711(18,23)
hx2 = HX711(24,25)
hx3 = HX711(12,16)
hx4 = HX711(6,13)
hx5 = HX711(19,26)

# hx tuple
hxs = (hx0, hx1, hx2, hx3, hx4, hx5)
weights = [0,0,0,0,0,0]

testing = 2
# on how the data is read
hxs[testing].set_reading_format("MSB", "MSB")

# hx weight reference. Set to 1 gram
hxs[testing].set_reference_unit(1)
hxs[testing].reset()
hxs[testing].tare()
print "Tare done! Add weight now..."

while True:
    try:
        time.sleep(5)
        val = hxs[testing].read_average(30)
        print val
        hxs[testing].power_down()
        hxs[testing].power_up()
        time.sleep(.01)
    except KeyboardInterrupt, SystemError:
        cleanAndExit()