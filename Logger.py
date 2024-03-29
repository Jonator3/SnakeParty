from datetime import datetime
import os

LogFile = None


def start():
    global LogFile
    time = datetime.now()
    os.mkdir("Logs")
    os.mkdir(time.strftime("Logs/%b-%y"))
    LogFile = open(time.strftime("Logs/%b-%y/%d-%a.log"), "w+")


def logged_print(*args):
    s = datetime.now().strftime("%X | ")
    s += " ".join([str(arg) for arg in args])
    if LogFile:
        LogFile.write(s)
    print(s)
