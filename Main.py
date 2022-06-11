
import os
import socketserver
import sys
import socket
from argparse import ArgumentParser

import eel
import qrcode

import setup
argpar = ArgumentParser()
argpar.add_argument("configfile", required=False, default="default.ini", help="path of configfile to be used")
args = argpar.parse_args(sys.argv)
if args.configfile != "":
    setup.load_conf(args.configfile)
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


def get_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        worker_port = s.server_address[1]
    return worker_port


def start_eel():
    eel.start("resources.html", mode='custom', host=sys_ip, port=eel_port, block=True, cmdline_args=['echo', 'hello world'])


eel_port = setup.eel_port
sys_ip = get_ip()
link = 'http://'+str(sys_ip)+':'+str(eel_port)+'/game.html'
qr = qrcode.make(link).resize((350, 350)).convert("RGB")
qr.save("web/qr.png", format="png")
print(link)

eel.init('web')

start_eel()


os.kill(os.getpid(), 9)  # exit the hard way