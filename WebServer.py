from threading import Thread
import websockets
import asyncio
import queue
import random
import time
import setup
import SharedData as SD


inc_msgs = queue.Queue()
outg_msgs = queue.Queue()
clsg_cons = queue.Queue()
opng_cons = queue.Queue()


class Client(object):

    def __init__(self, id: str):
        self.lastInput = [False, False, False, False, False]
        self.id = id
        SD.client_dict[id] = self

    def getInput(self):
        temp = self.lastInput
        self.lastInput = [False, False, False, False, False]
        return temp

    def setInput(self, value):
        if value == "l":
            self.lastInput = [True, False, False, False, False]
        if value == "d":
            self.lastInput = [False, True, False, False, False]
        if value == "r":
            self.lastInput = [False, False, True, False, False]
        if value == "u":
            self.lastInput = [False, False, False, True, False]
        if value == "e":
            self.lastInput = [False, False, False, False, True]


def websocket_server():

    connections = {}
    buf = queue.Queue()

    async def consumer_handler(ws):
        while True:
            try:
                message = await ws.recv()
                inc_msgs.put((findId(ws), message,))
            except websockets.ConnectionClosed:
                clsg_cons.put(findId(ws))
                connections.pop(findId(ws))
                break

    async def producer_handler(ws):
        while True:

            await loop.run_in_executor(None, producer)
            message = buf.get()
            try:
                await connections[message[0]].send(message[1])
            except Exception:
                print("producer_handler Error!")

    def producer():
        buf.put(outg_msgs.get())

    def findId(search_ws):
        for id, ws in connections.items():
            if ws == search_ws:
                return id


    async def websocket_handler(websocket, path):
        def generateId():
            while True:
                key = ""
                while len(key) < setup.KEY_LEN+1:
                    key += random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
                if connections.get(key) is None:
                    return key
        id = generateId()
        connections[id] = websocket
        opng_cons.put(id)

        consumer_task = asyncio.ensure_future(consumer_handler(websocket))
        producer_task = asyncio.ensure_future(producer_handler(websocket))
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED, )
        for task in pending:
            task.cancel()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = websockets.serve(ws_handler=websocket_handler, port=41800)
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


def on_message(id, msg):
    print(id, ">>", msg)

    if msg.startswith("K:"):
        key = msg[3:]
        if SD.client_lobby_dict.get(id):
            return
        if key == "host":
            key = SD.lobbyCreator(id)
            SD.client_dict.get(id).getInput()
            SD.client_lobby_dict[id] = key
        else:
            try:
                SD.lobby_dict.get(key).addClient(id)
                SD.client_dict.get(id).getInput()
                SD.client_lobby_dict[id] = key
            except Exception:
                SD.client_dict.pop(id)
                SD.client_lobby_dict.pop(id)
                send_message(id, "ERROR")
    else:
        SD.client_dict.get(id).setInput(msg)


def on_connection_open(id):
    print("Someone just connected! id: " + id)
    Client(id)


def on_connection_close(id):
    print("Someone just disconnected! id: " + id)

    lobby = SD.client_lobby_dict.get(id)
    if lobby:
        lobby.delClient(id)
        SD.client_lobby_dict.pop(id)


def S_Loop():
    time.sleep(1)
    while True:
        time.sleep(0.05)
        check_messages()


def start_server():
    s = Thread(target=websocket_server)
    l = Thread(target=S_Loop)
    s.start()
    l.start()


