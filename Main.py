
import os
import subprocess
import threading

import eel

import LobbyManager

eel.init('web')
eel_port = 8080


def start_eel():
    eel.start("resources.html", mode='custom', host='localhost', port=eel_port, block=True, cmdline_args=['echo', 'hello world'])


server_thread = threading.Thread(target=start_eel)
server_thread.daemon = True
server_thread.start()

subprocess.call([os.path.realpath("chromium/chrome"), '--app=http://localhost:'+str(eel_port), '--no-sandbox'])

