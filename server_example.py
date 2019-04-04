from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import time 
import sys
import json
import Queue
class SimpleEcho(WebSocket):

    def handleMessage(self):
        # echo message back to client
        msg = json.loads(self.data)
        if (msg["type"] == "calibration"):
            print("calibrating")
        elif (msg["type"] == "dispense"):
            ingredients = msg["data"]
            time.sleep(3)
            gram_list = []
            for g in range(5):
                gram_list.append("g")
            dispensed = json.dumps(
                {
                    "type": "completed",
                    "data": gram_list
                }
            )
            self.sendMessage(dispensed)
        elif (msg["type"] == "alert"):
            print("alerting")
            alert = json.dumps({"type": "alert", "data": { 'disabled': False, 'validNum': True, 'text': 'Tap to Dispense' }})
            self.sendMessage(alert)
        elif (msg["type"] == "stop"):
            print('stop')
        else:
            time.sleep(3)
            self.sendMessage("completed")

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')

server = SimpleWebSocketServer('10.1.69.142', 8000, SimpleEcho)
# server = SimpleWebSocketServer('172.16.16.56', 8000, SimpleEcho)
server.serveforever()