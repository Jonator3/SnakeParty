from datetime import datetime
LogFile = open(datetime.now().strftime("Logs/%b-%y/%d-%a.log"), "w+")

def logged_print(*args):
    s = datetime.now().strftime("%X| ")
    for arg in args:
        s += str(arg)
    LogFile.write(s)
    print(s)
