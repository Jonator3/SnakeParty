from typing import List
from threading import Thread
import random
import setup
import GameSys
import WebServer
import time
import queue
import SharedData as SD
from Logger import logged_print as print


menu_shift_dict = {
    "lc0": "c0",
    "rc0": "c1",
    "dc0": "c5",
    "uc0": "c0",
    "lc1": "c0",
    "rc1": "c2",
    "dc1": "c6",
    "uc1": "c1",
    "lc2": "c1",
    "rc2": "c3",
    "dc2": "c7",
    "uc2": "c2",
    "lc3": "c2",
    "rc3": "c4",
    "dc3": "c8",
    "uc3": "c3",
    "lc4": "c3",
    "rc4": "c4",
    "dc4": "c9",
    "uc4": "c4",
    "lc5": "c5",
    "rc5": "c6",
    "dc5": "m0",
    "uc5": "c0",
    "lc6": "c5",
    "rc6": "c7",
    "dc6": "m0",
    "uc6": "c1",
    "lc7": "c6",
    "rc7": "c8",
    "dc7": "m0",
    "uc7": "c2",
    "lc8": "c7",
    "rc8": "c9",
    "dc8": "m0",
    "uc8": "c3",
    "lc9": "c8",
    "rc9": "c9",
    "dc9": "m0",
    "uc9": "c4",
    "lm0": "m0",
    "rm0": "m1",
    "dm0": "m0",
    "um0": "c5",
    "lm1": "m0",
    "rm1": "m2",
    "dm1": "m1",
    "um1": "c5",
    "lm2": "m1",
    "rm2": "m2",
    "dm2": "m2",
    "um2": "c5"
}


def generateKey():
    while True:
        key = ""
        while len(key) < setup.KEY_LEN:
            key += random.choice("123456789abcdefghjklmnpqrstuvwxyz")
        if SD.lobby_dict.get(key) is None:
            return key


def lobbyCreator(host):
    return Lobby(host).id


SD.lobbyCreator = lobbyCreator


class LobbyFullError(RuntimeError):

    def __init__(self):
        super(LobbyFullError, self).__init__("lobby is full")


class Lobby(object):

    def __init__(self, host):
        self.mouseInput = queue.Queue(10)
        self.id = generateKey()
        print(self.id, "lobby opened")
        SD.lobby_dict[self.id] = self
        self.fieldsize = setup.DEF_SIZE
        self.playtime = setup.DEF_LEN
        self.players = []
        self.colours = {}
        self.thread = Thread(target=self.loop)
        self.cursors = {}
        self.addClient(host)
        self.thread.start()

    def getFreeColours(self):
        colours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for id in self.players:
            c = self.colours.get(id)
            colours.remove(c)
        return colours

    def addClient(self, id):
        if len(self.players) >= 10:
            raise LobbyFullError
        self.cursors[id] = "c0"
        colour = self.getFreeColours()[0]
        self.colours[id] = colour
        WebServer.send_message(id, "C:" + hex(colour)[2:])
        WebServer.send_message(id, "K:" + self.id)
        self.players.append(id)
        print(self.id, "player joined", id)

    def delClient(self, id):
        self.players.remove(id)
        self.colours.pop(id)
        self.cursors.pop(id)
        print(self.id, "player left", id)

    def clientMouseInput(self, player, pos):
        print("received")
        self.mouseInput.put_nowait((player, pos))

    def loop(self):
        while 1:
            if self.players.__len__() == 0:
                SD.lobby_dict.pop(self.id)
                print(self.id, "lobby closed")
                return
            for C in self.players:
                inp = SD.client_dict.get(C).getInput()
                input = ""
                if inp[0]:
                    input = "l"
                if inp[1]:
                    input = "d"
                if inp[2]:
                    input = "r"
                if inp[3]:
                    input = "u"
                if inp[4]:
                    input = "e"
                if input == "e":
                    pos = self.cursors.get(C)
                    if pos.startswith("c"):
                        c = int(pos[1], 10)
                        if self.getFreeColours().__contains__(c):
                            self.colours[C] = c
                            WebServer.send_message(C, "C:" + hex(c)[2:])
                    elif pos == "m0" and C == self.players[0]:
                        self.playtime += 1
                        if self.playtime > setup.MAX_LEN:
                            self.playtime = 1
                    elif pos == "m1" and C == self.players[0]:
                        self.fieldsize += 1
                        if self.fieldsize >= len(setup.SIZE_SET):
                            self.fieldsize = 0
                    elif pos == "m2" and C == self.players[0]:
                        GameSys.Game(setup.SIZE_SET[self.fieldsize], self.playtime, self.players, self).Run()
                        while self.mouseInput.qsize() > 0:
                            self.mouseInput.get_nowait()
                        for id in self.players:
                            self.cursors[id] = "c0"
                elif input != "":
                    key = input + self.cursors.get(C)
                    self.cursors[C] = menu_shift_dict.get(key)
                GameSys.sendMenuScreen(self)
            while self.mouseInput.qsize() > 0:
                player, pos = self.mouseInput.get_nowait()
                print("parsing", player, pos)
                if player is None:
                    break
                self.cursors[player] = pos
                if pos.startswith("c"):
                    c = int(pos[1], 10)
                    if self.getFreeColours().__contains__(c):
                        self.colours[C] = c
                        WebServer.send_message(C, "C:" + hex(c)[2:])
                elif pos == "m0" and C == self.players[0]:
                    self.playtime += 1
                    if self.playtime > setup.MAX_LEN:
                        self.playtime = 1
                elif pos == "m1" and C == self.players[0]:
                    self.fieldsize += 1
                    if self.fieldsize >= len(setup.SIZE_SET):
                        self.fieldsize = 0
                elif pos == "m2" and C == self.players[0]:
                    GameSys.Game(setup.SIZE_SET[self.fieldsize], self.playtime, self.players, self).Run()
                    while self.mouseInput.qsize() > 0:
                        self.mouseInput.get_nowait()
                    for id in self.players:
                        self.cursors[id] = "c0"
            time.sleep(0.2)
