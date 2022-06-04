import threading
from threading import Thread
import setup
import GameSys
import WebServer
import time
import queue
import SharedData as SD
from Logger import logged_print as print
import eel


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
    "uc5": "c0",
    "lc6": "c5",
    "rc6": "c7",
    "uc6": "c1",
    "lc7": "c6",
    "rc7": "c8",
    "uc7": "c2",
    "lc8": "c7",
    "rc8": "c9",
    "uc8": "c3",
    "lc9": "c8",
    "rc9": "c9",
    "uc9": "c4",
}


class LobbyFullError(RuntimeError):

    def __init__(self):
        super(LobbyFullError, self).__init__("lobby is full")


class Lobby(object):

    def __init__(self):
        self.mouseInput = queue.Queue(10)
        self.id = "lobby"
        print(self.id, "lobby opened")
        self.fieldsize = setup.DEF_SIZE
        self.playtime = setup.DEF_LEN
        self.players = []
        self.colours = {}
        self.thread = Thread(target=self.loop)
        self.cursors = {}
        self.should_run = False
        self.thread.daemon = True
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
        self.mouseInput.put_nowait((player, pos))

    def change_time(self, diff):
        self.playtime += diff
        if self.playtime > setup.MAX_LEN:
            self.playtime = setup.MAX_LEN
        elif self.playtime < 1:
            self.playtime = 1

    def change_size(self, diff):
        self.fieldsize += diff
        if self.fieldsize >= len(setup.SIZE_SET):
            self.fieldsize = len(setup.SIZE_SET)-1
        elif self.fieldsize < 0:
            self.fieldsize = 0

    def run_game(self):
        GameSys.Game(setup.SIZE_SET[self.fieldsize], self.playtime, self.players, self).Run()
        while self.mouseInput.qsize() > 0:
            self.mouseInput.get_nowait()
        for id in self.players:
            self.cursors[id] = "c0"

    def handelEnter(self, player, pos):
        if pos.startswith("c"):
            c = int(pos[1], 10)
            if self.getFreeColours().__contains__(c):
                self.colours[player] = c
                WebServer.send_message(player, "C:" + hex(c)[2:])

    def loop(self):
        time.sleep(5)  # boot delay
        while 1:
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
                    self.handelEnter(C, pos)
                elif input != "":
                    key = input + self.cursors.get(C)
                    self.cursors[C] = menu_shift_dict.get(key)
            while self.mouseInput.qsize() > 0:
                player, pos = self.mouseInput.get_nowait()
                if player is None:
                    break
                self.cursors[player] = pos
                self.handelEnter(player, pos)
            if self.should_run:
                self.run_game()
                self.should_run = False
            GameSys.sendMenuScreen(self)
            time.sleep(0.2)


SD.lobby = Lobby()


@eel.expose
def time_down():
    SD.lobby.change_time(-1)


@eel.expose
def time_up():
    SD.lobby.change_time(1)


@eel.expose
def size_down():
    SD.lobby.change_size(-1)


@eel.expose
def size_up():
    SD.lobby.change_size(1)


@eel.expose
def start_game():
    if len(SD.lobby.players) > 0:
        SD.lobby.should_run = True

