from datetime import datetime
import os


time = datetime.now()
os.mkdir("Logs")
os.mkdir(time.strftime("Logs/%b-%y"))
LogFile = open(time.strftime("Logs/%b-%y/%d-%a.log"), "w+")


def logged_print(*args):
    s = datetime.now().strftime("%X| ")
    for arg in args:
        s += str(arg)
    LogFile.write(s)
    print(s)
