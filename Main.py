
from Logger import logged_print as print
from datetime import datetime
import psutil
import asyncio
import websockets
import LobbyManager


def resource_str():
    msg = datetime.now().strftime('<span style="font-size: 20px">%c:<br><br>CPU:</span><br>')
    msg += '<span style="color: #FFFFFF">..</span>cores:<span style="color: #AAAAAA">.......</span>' + str(psutil.cpu_count(False)) + '<br>'
    msg += '<span style="color: #FFFFFF">..</span>usage:<span style="color: #AAAAAA">.......</span>' + str(round(psutil.cpu_percent(1))) + '%<br>'
    msg += '<span style="font-size: 20px"><br>RAM:</span><br>'
    ram = psutil.virtual_memory()
    msg += '<span style="color: #FFFFFF">..</span>usage:<span style="color: #AAAAAA">.......</span>' + str(round(ram.percent)) + '%<br>'
    msg += '<span style="color: #FFFFFF">..</span>total:<span style="color: #AAAAAA">.......</span>' + str(round(ram.total/(1024**2))) + 'MB'
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


