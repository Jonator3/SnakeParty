
import os
import subprocess
import threading
import socket
import time

import eel
import qrcode

import LobbyManager


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


eel_port = 8080
sys_ip = get_ip()
link = 'http://'+str(sys_ip)+':'+str(eel_port)+'/game.html'
qr = qrcode.make(link).resize((350, 350)).convert("RGB")
qr.save("web/qr.png", format="png")
print(link)

eel.init('web')


def start_eel():
    eel.start("resources.html", mode='custom', host=sys_ip, port=eel_port, block=True, cmdline_args=['echo', 'hello world'])


server_thread = threading.Thread(target=start_eel)
server_thread.daemon = True
server_thread.start()

subprocess.call([os.path.realpath("chromium/chrome"), '--app=http://'+str(sys_ip)+':'+str(eel_port)+'/menu.html', '--no-sandbox'])


# ensure program end
def kill():
    time.sleep(1)
    os.kill(os.getpid(), 9)


tk = threading.Thread(target=kill)
tk.daemon = True
tk.start()

exit(0)
