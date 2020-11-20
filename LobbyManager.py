from typing import List
from threading import Thread
import random
import setup
import GameSys
import SharedData as SD


def generateKey():
    while True:
        key = ""
        while len(key) < setup.KEY_LEN:
            key += random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if SD.lobby_dict.get(key) is None:
            return key


class LobbyFullError(RuntimeError):

    def __init__(self):
        super(LobbyFullError, self).__init__("lobby is full")


class Lobby(object):
    id: str
    players: List[str]
    game: GameSys.Game
    playtime: int
    fieldsize: int

    def __init__(self):
        self.id = generateKey()
        SD.lobby_dict[self.id] = self
        self.players = []
        self.colours = {}

    def getFreeColours(self):
        colours: List[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for c in self.colours:
            colours.remove(c)
        return colours

    def addClient(self, id):
        if len(self.players) >= 10:
            raise LobbyFullError
        self.players.append(id)

    def delClient(self, id):
        self.players.remove(id)

    def loop(self):
        if self.players.__len__() == 0:
            SD.lobby_dict.pop(self.id)
            return
        # TODO
