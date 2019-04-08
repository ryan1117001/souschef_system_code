from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import time 
import sys
import json

class SimpleEcho(WebSocket):

    def handleMessage(self):
        # echo message back to client
        msg = json.loads(self.data)
        print(msg)
        if (msg["type"] == "dispense"):
            ingredient = msg["data"]
            ID = ingredient['id']
            desired_grams = ingredient['grams']
            cur_grams = 0
            prev_grams = 0
            time.sleep(3)
            while (desired_grams - cur_grams > 3):
                prev_grams = cur_grams
                cur_grams = cur_grams + 4
                if (prev_grams == cur_grams):
                    alert = json.dumps({"type": "alert", "data": ID})
                    self.sendMessage(alert)
                    break
            completed = json.dumps({"type": "completed", "data": {"id": ID, "grams": cur_grams}})
            self.sendMessage(completed)
        else:
            # add calibration code if time permits
            pass

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')

server = SimpleWebSocketServer('10.1.69.149', 8000, SimpleEcho)

server.serveforever()