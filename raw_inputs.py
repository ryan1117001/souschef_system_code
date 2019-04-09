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
hx = HX711(14,15) # container 1
# hx = HX711(18,23) # container 2
# hx = HX711(24,25) # container 3
# hx = HX711(12,16) # container 4
# hx = HX711(6,13) # container 5
# hx = HX711(19,26) # container 6

weight = 0

# on how the data is read
hx.set_reading_format("MSB", "MSB")

# hx weight reference. Set to 1 gram
hx.set_reference_unit(-3160.5 )
hx.reset()
hx.tare()
print "Tare done! Add weight now..."

while True:
    try:
        val = hx.get_weight(5)
        print val
        hx.power_down()
        hx.power_up()
        time.sleep(.01)
    except KeyboardInterrupt, SystemError:
        cleanAndExit()