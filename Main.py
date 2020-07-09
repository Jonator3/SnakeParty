# Made by Joey Pehlke
# Github: https://github.com/Jonator3
# Projeckt: https://github.com/Jonator3/SnakeParty
# last Update: 06.11.2019
import datetime
import socket
import queue

import pygame
import qrcode

import Window
import ControllerManager as CM
import data
import Game


pygame.init()
wasd = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
arrows = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]


class Color(object):

    def __init__(self, name, RGB):
        self.color = RGB
        self.name = name
        
    def hex(self):
        return '#%02x%02x%02x' % (self.color[0], self.color[1], self.color[2])


class Player(object):

    def __init__(self):
        self.Controller = None
        self.color = None
        self.lastSwitch = datetime.datetime.now()

    def isActive(self):
        if self.Controller is None:
            return False
        else:
            return True

    def getController(self):
        if self.Controller is None:
            self.Controller = CM.getFreeController()
            if self.Controller is not None:
                self.color = Colores.get()
                self.Controller.setColor(self.color.hex())
        else:
            if self.Controller.isClosed():
                self.Controller = None
                Colores.put(self.color)
                self.color = None
                self.getController()

    def getColor(self):
        if self.isActive():
            if not Colores.empty():
                input = self.getInput()
                if input[0]:
                    diff = datetime.datetime.now()-self.lastSwitch
                    if diff.seconds >= 1:
                        Colores.put(self.color)
                        self.color = Colores.get()
                        self.Controller.setColor(self.color.hex())
                        self.lastSwitch = datetime.datetime.now()

    def getInput(self):
        if self.Controller is None:
            self.getController()
            return [False, False, False, False]
        input = self.Controller.getLastInput()
        return input


def setPlayers(players):
    temp = 0
    while temp < data.MAX_PLAYERS:
        players.append(Player())
        temp = temp+1
    

global Players, Colores
Colores = queue.Queue()
Players = []
Colores.put(Color("Blue", [80, 100, 255]))
Colores.put(Color("Orange", [255, 130, 0]))
Colores.put(Color("Lime", [170, 255, 20]))
Colores.put(Color("Red", [255, 20, 20]))
Colores.put(Color("Yellow", [250, 240, 0]))
Colores.put(Color("Mint", [20, 255, 140]))
Colores.put(Color("Pink", [250, 100, 150]))
Colores.put(Color("White", [240, 240, 240]))
Colores.put(Color("Purple", [220, 0, 250]))
Colores.put(Color("Cyan", [0, 255, 200]))
setPlayers(Players)
data.Players = Players

def getAcColores(AccP):
    out = []
    for P in AccP:
        out.append(P.color.color)
    return out


def getInacColores():
    out = []
    x=0
    while x < Colores.qsize():
        x = x+1
        color = Colores.get()
        out.append(color.color)
        Colores.put(color)
    return out


def main():
    global Players
    print("System started!")
    clock = pygame.time.Clock()

    length = data.DEF_LEN
    size = data.DEF_SIZE
    state = 0
    Sys_IP = socket.gethostbyname(socket.gethostname())
    link = "http://"+Sys_IP+"/"
    print(link)
    qr = qrcode.make(link).resize((350, 350)).convert("RGB")
    qrc = pygame.image.frombuffer(qr.tobytes(), qr.size, "RGB")

    while CM.isRunning:
        pygame.time.delay(20)
        clock.tick(15)

        ac = Game.activePlayers()
        input = Window.checkInput()
        if input is not None:
            if input[pygame.K_UP]:
                if state == 0:
                    if length < 15:
                        length = length+1
                elif state == 1:
                    if size < len(data.SIZE_SET)-1:
                        size = size+1
            elif input[pygame.K_DOWN]:
                if state == 0:
                    if length > 1:
                        length = length-1
                elif state == 1:
                    if size > 0:
                        size = size-1
            elif input[pygame.K_LEFT]:
                if state > 0:
                    state = state-1
            elif input[pygame.K_RIGHT]:
                if state < 2:
                    state = state+1
            elif input[13]:  # index 13=Enter
                if state < 2:
                    state = 2
                elif state == 2:
                    if len(ac) > 0:
                        Game.start(data.SIZE_SET[size], length, ac)
                        for P in Players:
                            P.getInput()
                        ac = Game.activePlayers()
                        length = data.DEF_LEN
                        size = data.DEF_SIZE
                        state = 0

        Window.drawMenu(state, length, data.SIZE_SET[size], qrc, link, getAcColores(ac), getInacColores())
        for P in Players:
            P.getController()
            P.getColor()


main()
