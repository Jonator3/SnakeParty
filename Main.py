
from Logger import logged_print as print
from datetime import datetime
import psutil
import asyncio
import websockets
import LobbyManager


def resource_str():
    msg = "CPU:<br><br>"
    msg += "  cores:      " + str(psutil.cpu_count(False)) + "<br>"
    msg += "  usage:      " + str(round(psutil.cpu_percent(1))) + "%<br>"
    msg += "  frequency:  " + str(round(psutil.cpu_freq().current/1000, 1)) + "GHz<br><br>"
    msg += "RAM:<br><br>"
    ram = psutil.virtual_memory()
    msg += "  usage:      " + str(round(ram.percent)) + "%<br>"
    msg += "  total:      " + str(round(ram.total/(1024**2))) + "MB"
    return msg


async def handler(websocket, path):
    try:
        while 1:
            await websocket.send(resource_str())
            await asyncio.sleep(4)
    except websockets.ConnectionClosed:
        return

psutil.cpu_percent()  # needed to ignore the initial 0.0 return

print("SnakeParty Server started", datetime.now().strftime("%x"))
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
server = websockets.serve(ws_handler=handler, port=41801)
loop.run_until_complete(server)
loop.run_forever()


