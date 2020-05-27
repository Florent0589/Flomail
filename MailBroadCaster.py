from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import asyncio
import json
import time


class MyBroadCasterProtocol(WebSocketServerProtocol):

    def onConnect(self, response):

        print("Server connected: {0}".format(response.peer))

    def onOpen(self):

        print("WebSocket connection open.")

        self.send_message()

    def onMessage(self, payload, isBinary):

        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
            decode_message = payload.decode('utf8')
            print('success')

    def onClose(self, wasClean, code, reason):

        print("WebSocket connection closed: {0}".format(reason))

    def send_message(self):

        message = {"message": ["Hi grom the server", "to my client"]}
        payload = bytes(json.dumps(message), 'utf-8')
        self.sendMessage(payload)


if __name__ == '__main__':

    factory = WebSocketServerFactory('ws://localhost:1100')
    factory.protocol = MyBroadCasterProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, 'localhost', 1100)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
