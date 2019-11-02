# Made by Joey Pehlke
# Github: https://github.com/Jonator3
# Projeckt: https://github.com/Jonator3/SnakeParty
# last Update: 02.12.2019
# Version: Beta 0.6

import Window
import pygame
import Game
import qrcode
import socket
import ControllerManager as CM
import data
import queue


pygame.init()
wasd = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
arrows = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]

class Color(object):

    def __init__(self, name, RGB):
        self.color = RGB
        self.name = name
        
    def hex(self):

        output = '#%02x%02x%02x' % (self.color[0], self.color[1], self.color[2])

        return output


class Player(object):

    def __init__(self):
        self.Controller = None
        self.color = None

    def isActive(self):
        if self.Controller is None:
            return False
        else:
            return True

    def getController(self):
        if self.Controller is None:
            self.Controller = CM.getFreeController()
            if not self.Controller is None:
                self.color = Colores.get()
                self.Controller.setColor(self.color.hex())
        else:
            if self.Controller.isClosed():
                self.Controller = None
                Colores.put(self.color)
                self.color = None

    def getColor(self):
        if self.isActive():
            if not Colores.empty():
                input = self.getInput()
                if input[0]:
                    Colores.put(self.color)
                    self.color = Colores.get()
                    self.Controller.setColor(self.color.hex())

    def getInput(self):
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
Colores.put(Color("Pink", [230, 40, 150]))
Colores.put(Color("Red", [255, 40, 20]))
Colores.put(Color("Yellow", [220, 200, 20]))
Colores.put(Color("Cyan", [30, 255, 170]))
Colores.put(Color("Light-Blue", [120, 200, 255]))
Colores.put(Color("White", [240, 240, 240]))
Colores.put(Color("Purple", [200, 10, 250]))
Colores.put(Color("Light-Pink", [255, 120, 130]))
setPlayers(Players)
data.Players = Players


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

    CM.S.join()
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
                    state = state+1
                elif state == 2:
                    if len(ac) > 0:
                        Game.start(data.SIZE_SET[size], length, ac)
                        ac = Game.activePlayers()
                        length = data.DEF_LEN
                        size = data.DEF_SIZE
                        state = 0

        Window.drawMenu(state, length, data.SIZE_SET[size], qrc, link, len(ac))
        for P in Players:
            P.getController()
            P.getColor()


main()