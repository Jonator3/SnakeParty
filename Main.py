# Made by Joey Pehlke
# Github: https://github.com/Jonator3
# last Update: 31.10.2019

import Window
import pygame
import Game
import qrcode
import socket
import random
import ControllerManager as CM
import data


pygame.init()
wasd = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
arrows = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]


class Player(object):

    def __init__(self, name, color, hexC):
        self.Controller = None
        self.name = name
        self.color = color
        self.hexC = hexC

    def isActive(self):
        if self.Controller is None:
            return False
        else:
            return True

    def getController(self):
        if self.Controller is None:
            self.Controller = CM.getFreeController()
            if not self.Controller is None:
                self.Controller.setColor(self.hexC)
        else:
            if self.Controller.isClosed():
                self.Controller = None

    def getInput(self):
        input = self.Controller.getLastInput()
        return input


global Players
Players = []
Players.append(Player("Blue", [80, 100, 255], "#5064FF"))
Players.append(Player("Orange", [255, 130, 0], "#FF8200"))
Players.append(Player("Pink", [230, 40, 150], "#E62896"))
Players.append(Player("Red", [255, 40, 20], "#FF2814"))
Players.append(Player("Yellow", [220, 200, 20], "#DCC814"))
Players.append(Player("Cyan", [30, 255, 170], "#1EFFAA"))
Players.append(Player("Light-Blue", [120, 200, 255], "#78C8FF"))
Players.append(Player("White", [240, 240, 240], "#F0F0F0"))
Players.append(Player("Purple", [200, 10, 250], "#C80AFA"))
Players.append(Player("Light-Pink", [255, 120, 130], "#FF7882"))
random.shuffle(Players)
data.Players = Players


def main():
    global Players
    print("System started!")
    clock = pygame.time.Clock()
    input = None

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

        random.shuffle(Players)
        ac = Game.activePlayers()
        input = Window.checkInput()
        if input is None:
            input = []
        else:
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


main()
