import random
import string
import datetime
import sys
import time
import os
import asyncio
import threading
import queue

from aiohttp import web
import websockets


inc_msgs = queue.Queue()
outg_msgs = queue.Queue()
clsg_cons = queue.Queue()
opng_cons = queue.Queue()
file = open("WebController.html", "r")
global html , isRunning, Controllers, freeControllers
Controllers = []
freeControllers = queue.Queue()
html = file.read()
file.close()
isRunning = True


class Controller(object):

    def __init__(self, id):
        self.id = id
        self.input = [False, False, False, False]
        self.closed = False
        self.color = "#555555"
        self.test = threading.Thread(target=self.checker)
        self.test.start()
        self.time = datetime.datetime.now()

    def ping(self):
        self.time = datetime.datetime.now()
        self.send("ping")

    def setColor(self, color):
        self.color = color
        self.send("C:"+self.color)

    def send(self, msg):
        send_message(self.id, msg)

    def isClosed(self):
        return self.closed

    def close(self):
        self.closed = True

    def getId(self):
        return self.id

    def setInput(self, input):
        if input == "pong":
            ping = self.time-datetime.datetime.now()
            ping = ping.microseconds
            self.send("T:"+str(ping))
            return
        if len(input)== 2:
            if input.startswith("0"):
                if input[1] == "u":
                    self.input = [True, False, False, False]
                elif input[1] == "l":
                    self.input = [False, True, False, False]
                elif input[1] == "d":
                    self.input = [False, False, True, False]
                elif input[1] == "r":
                    self.input = [False, False, False, True]
            if input.startswith("1"):
                if input[1] == "u":
                    self.input = [True, False, False, False]
                elif input[1] == "l":
                    self.input = [False, True, False, False]
                elif input[1] == "d":
                    self.input = [False, False, True, False]
                elif input[1] == "r":
                    self.input = [False, False, False, True]

    def checker(self):
        print("New sender for:"+self.id)
        while not self.closed:
            if not isRunning:
                break
            self.ping()
            time.sleep(2)

    def getLastInput(self):
        lastInput = self.input
        self.input = [False, False, False, False]
        return lastInput


def getControllerById(id):
    for C in Controllers:
        if C.getId()==id:
            return C


def aiohttp_server():
    global html

    async def http_handler(request):
        return web.Response(text=html, content_type="text/html")

    http_app = web.Application()
    http_app.add_routes([web.get('/', http_handler)])
    return http_app


def websocket_server():

    connections = {}
    buf = queue.Queue()

    async def consumer_handler(ws):
        global isRunning
        while isRunning:
            try:
                message = await ws.recv()
                inc_msgs.put((findId(ws), message,))
            except websockets.ConnectionClosed:
                clsg_cons.put(findId(ws))
                connections.pop(findId(ws))
                break

    async def producer_handler(ws):
        global isRunning
        while isRunning:

            await loop.run_in_executor(None, producer)
            message = buf.get()
            try:
                await connections[message[0]].send(message[1])
            except Exception:
                print("Handler Error")

    def producer():
        buf.put(outg_msgs.get())

    def findId(search_ws):
        for id, ws in connections.items():
            if ws == search_ws:
                return id


    async def websocket_handler(websocket, path):
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
        connections[id] = websocket
        opng_cons.put(id)

        consumer_task = asyncio.ensure_future(consumer_handler(websocket))
        producer_task = asyncio.ensure_future(producer_handler(websocket))
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED, )
        for task in pending:
            task.cancel()
        if not isRunning:
            sys.exit()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = websockets.serve(ws_handler=websocket_handler, port=81)
    loop.run_until_complete(server)
    loop.run_forever()


def check_messages():
    while not opng_cons.empty():
        on_connection_open(opng_cons.get())

    while not inc_msgs.empty():
        message = inc_msgs.get()
        on_message(message[0], message[1])

    while not clsg_cons.empty():
        on_connection_close(clsg_cons.get())


def send_message(id, str):
    outg_msgs.put((id, str))


def run_server(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(web.run_app(app, port=80))
    loop.run_forever()


def start_server():
    u = threading.Thread(target=websocket_server)
    u.start()
    t = threading.Thread(target=run_server, args=(aiohttp_server(),))
    t.start()


def on_message(id, msg):

    Con = getControllerById(id)
    T = threading.Thread(target=Con.setInput(msg))
    T.start()


def on_connection_open(id):
    print("Someone just connected! id: " + id)

    Con = Controller(id)
    Controllers.append(Con)
    freeControllers.put(Con)


def on_connection_close(id):
    print("Someone just disconnected! id: " + id)
    con = getControllerById(id)
    con.close()
    Controllers.remove(con)

def getFreeController():
    if freeControllers.empty():
       return None
    Con = freeControllers.get()
    if Con.isClosed():
        return getFreeController()
    else:
        return Con


def S_Loop():
    global isRunning
    while isRunning:
        check_messages()


def start():
    time.sleep(2)
    start_server()
    ServerLoop = threading.Thread(target=S_Loop)
    ServerLoop.start()
    time.sleep(5)


def stop():
    global isRunning
    isRunning = False
    for C in Controllers:
        C.close()
    os._exit(0)


start()
