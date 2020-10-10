from typing import List
from threading import Thread
import random
import setup
import GameSys


Lobbys = {}


def generateKey():
    while True:
        key = ""
        while len(key) < setup.KEY_LEN:
            key += random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if Lobbys.get(key) is None:
            return key


class Player(object):
    colour: int

    def __init__(self, client, key: str):
        self.client = client
        self.lobby = Lobbys.get(key)
        if not self.lobby:
            client.sendError("Lobby not found! key:"+key)
            return
        if self.lobby.players.__len__() >= setup.MAX_PLAYERS:
            client.sendError("Lobby is full!")
            return
        self.lobby.players.append(self)
        self.colour = self.lobby.freeColours()[0]



class Lobby(object):
    id: str
    players: List[object]
    freeColours: List[int]
    game: GameSys.Game
    playtime: int
    fieldsize: int

    def __init__(self):
        self.id = generateKey()
        Lobbys[self.id] = self
        self.players = []

    def freeColours(self):
        out = range(1, 11)
        for p in self.players:
            out.remove(p.colour)
        return out

    def loop(self):
        if self.players.__len__() == 0:
            Lobbys.pop(self.id)
            return
        for p in self.players:
            if p.client is None:
                self.players.remove(p)

