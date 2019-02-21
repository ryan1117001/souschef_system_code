from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json

class SimpleEcho(WebSocket):
    
    def handleMessage(self):
        # ingredients = json.loads(self.data) # loads JSON Object into an array
	    # print(ingredients[0]["name"]) # how to access items in the array
        data = {
            "disabled": False,
        }
        self.sendMessage(data)
    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


server = SimpleWebSocketServer('10.1.250.128', 8000, SimpleEcho)
server.serveforever()
