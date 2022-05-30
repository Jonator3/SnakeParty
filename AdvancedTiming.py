from datetime import datetime
import time


class Clock(object):

    def __init__(self):
        self.lastTick = datetime.now()

    def tick(self, ms: int):
        while True:
            diff = datetime.now() - self.lastTick
            if (diff.microseconds // 1000) + diff.seconds * 1000 >= ms:
                self.lastTick = datetime.now()
                return
            time.sleep(0.0001)

