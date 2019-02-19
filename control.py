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

class SimpleEcho(WebSocket):
    
    def handleMessage(self):
        ingredients = json.loads(self.data) # loads JSON Object into an array
        print(ingredients[0]["name"]) # how to access items in the array
        eW=150000
        mW=0
        while eW-mW>5:
            try:
                # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
                # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
                # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment the three lines to see what it prints.
                #np_arr8_string = hx.get_np_arr8_string()
                #binary_string = hx.get_binary_string()
                #print binary_string + " " + np_arr8_string
                # Spin continuously
                try:
                    stepperOne.start(50) # 50 duty cycle        
                except KeyboardInterrupt:
                    print("Clean up")
                    GPIO.cleanup()
                    stepperOne.stop()
                # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
                # val = hx.get_weight(5)
                val=0
                for i in range(5):
                    val += hx.read_long()
                mW = val/5
                print mW

                # To get weight from both channels (if you have load cells hooked up 
                # to both channel A and B), do something like this
                #val_A = hx.get_weight_A(5)
                #val_B = hx.get_weight_B(5)
                #print "A: %s  B: %s" % ( val_A, val_B )

                hx.power_down()
                hx.power_up()
                time.sleep(0.1)
            except(KeyboardInterrupt, SystemExit):
                cleanAndExit()
        mess={
        "name":"Bitchass Ryan",
        "City":"HoCentral"
        }
        packed=json.dumps(mess)
        try:
            self.sendMessage(packed)
        except:
            print('L')
        #cleanAndExit()


    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')
        cleanAndExit()


hx = HX711(14, 15)

#bit order
hx.set_reading_format("MSB", "MSB")

#weight reference
#hx.set_reference_unit(113)
hx.set_reference_unit(1)

#hx setup
hx.reset()
#hx.tare()

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

#motor constants
DIR = 21 # Direction Pin
STEP = 20 # Step Pin
STEP_CNT = 360

#motor pin  setup
GPIO.setmode(GPIO.BCM)

GPIO.setup(DIR,GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

GPIO.output(DIR, GPIO.LOW)

stepperOne = GPIO.PWM(STEP,200) # 200 ticks per second





# Spin continuously
try:
    stepperOne.start(50) # 50 duty cycle        
except KeyboardInterrupt:
    print("Clean up")
    GPIO.cleanup()
    stepperOne.stop()

server = SimpleWebSocketServer('10.1.250.128', 8000, SimpleEcho)
server.serveforever()


