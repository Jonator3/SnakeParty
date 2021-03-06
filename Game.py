import random

import SoundManager as SM
import ControllerManager as CM
import Window
import data

import pygame


def start(size, length, Players):
    game = Game(size, length, Players)
    game.Run()


class PowerUp(object):
    
    def __init__(self, game):
        self.pos = game.getFreePos()
        self.type = self.getRandomType()
        self.liveTime = random.randint(10*data.CLOCK_SPEED, 20*data.CLOCK_SPEED)
        
    def getRandomType(self):
        X = 0
        R = random.randint(1, 100)
        X=X+10
        if R <= X:
            return "INF_LEN"
        X = X + 20
        if R <= X:
            return "GOLD"
        X = X + 15
        if R <= X:
            return "SHORT"

        return "DEF"

    def getType(self):
        return self.type

    def getColor(self):
        if self.type == "DEF":
            return [0, 160, 0]
        elif self.type == "INF_LEN":
            return [160, 0, 0]
        elif self.type == "GOLD":
            return [150, 130, 0]
        elif self.type == "SHORT":
            return [0, 0, 150]
        else:
            return [0, 160, 0]

    def liveTick(self):
        self.liveTime = self.liveTime-1

    def getLiveTime(self):
        return self.liveTime

    def getPos(self):
        return self.pos


class Block(object):

    def __init__(self, game, color, pos):
        self.game = game
        self.color = color
        self.posX = pos[0]
        self.posY = pos[1]

    def getColor(self):
        return self.color

    def getPos(self):
        return [self.posX, self.posY]

    def isIn(self):
        if self.posX < 0:
            return False
        elif self.posX > self.game.getSize()-1:
            return False
        elif self.posY < 0:
            return False
        elif self.posY > self.game.getSize()-1:
            return False
        else:
            return True


class Snake(object):

    def __init__(self, game, index, player):
        self.player = player
        self.underdog = 1
        self.name = player.color.name
        self.index = index
        self.game = game
        self.color = player.color.color
        self.len = 3
        self.movement = [0, 0]
        self.hasMovement = False
        self.pos = [0, 0]
        self.body = []
        self.score = 0
        self.reset()
        self.resetTag = False

    def getName(self):
        return self.name

    def getPos(self):
        return self.pos

    def isOut(self):
        if self.pos[-2] < 0:
            return True
        elif self.pos[-2] > self.game.getSize()-1:
            return True
        elif self.pos[-1] < 0:
            return True
        elif self.pos[-1] > self.game.getSize()-1:
            return True
        else:
            return False

    def addScore(self, value):
        self.score = self.score + value
        if self.score < 0:
            self.score = 0

    def getScore(self):
        return self.score

    def reset(self):
        self.resetTag = False
        length = len(self.body)
        miss = round((length/2) - 100)
        if miss > 0:
            miss = 0
        self.addScore(miss)
        self.len = 5
        self.movement = [0, 0]
        self.hasMovement = False
        self.body.clear()
        self.pos = self.game.getFreePos()
        self.body.insert(0, Block(self.game, self.color, self.pos))

    def giveInput(self):
        input = []
        try:
            input = self.player.getInput()
        except:
            input = [False, False, False, False]
        if self.hasMovement:
            if self.movement[1] == 0:
                if input[0]:
                    self.movement = [0, -1]
                elif input[2]:
                    self.movement = [0, 1]
            if self.movement[0] == 0:
                if input[1]:
                    self.movement = [-1, 0]
                elif input[3]:
                    self.movement = [1, 0]
        else:
            if input[0]:
                self.movement = [0, -1]
                self.hasMovement = True
            elif input[1]:
                self.movement = [-1, 0]
                self.hasMovement = True
            elif input[2]:
                self.movement = [0, 1]
                self.hasMovement = True
            elif input[3]:
                self.movement = [1, 0]
                self.hasMovement = True

    def move(self):
        if self.resetTag:
            self.reset()
        if self.hasMovement:
            self.pos[0] = self.pos[0]+self.movement[0]
            self.pos[1] = self.pos[1] + self.movement[1]
            self.body.append(Block(self.game, self.color, self.pos))
            for i in self.body[:-1*self.len]:
                self.body.remove(i)

    def addLen(self):
        self.len = self.len+1

    def addLenCount(self, int):
        self.len = self.len+int

    def setLen(self, int):
        self.len = int

    def getColor(self):
        return self.color

    def isMoving(self):
        return self.hasMovement

    def getBody(self):
        return self.body

    def setReset(self):
        SM.play(0)
        self.resetTag = True

    def setUnderdog(self, int):
        self.underdog = int


class Game(object):

    def __init__(self, size, length, Players):
        self.players = Players
        self.size = size
        self.length = length
        self.time_sec = 0
        self.time_min = 0
        self.power_ups = []
        self.snakes = []

        i = 0
        for P in Players:
            self.snakes.append(Snake(self, i, P))
            i = i+1

    def tick(self):
        self.time_sec = self.time_sec + 1
        if self.time_sec > 59:
            self.time_sec = 0
            self.time_min = self.time_min + 1

    def time(self):
        if self.time_sec < 10:
            return str(self.time_min) + ":0" + str(self.time_sec)
        else:
            return str(self.time_min) + ":" + str(self.time_sec)

    def getFreePos(self):
        flag = True

        while flag:
            flag = False
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)

            for P in self.power_ups:
                if P.getPos() == [x, y]:
                    flag = True

            if not flag:
                for P in self.snakes:
                    for b in P.getBody():
                        if b.getPos() == [x, y]:
                            flag = True

        return [x, y]

    def setPowerUp(self):
        R = random.randint(1, 100)
        trigger = 0
        if len(self.power_ups) <= len(self.snakes)/2:
            trigger = 100
        elif len(self.power_ups) > (len(self.snakes) * 1.7):
            trigger = 0
        else:
            trigger = round(100 / ((len(self.power_ups) * 10)/(len(self.snakes)/2)) )

        if R <= trigger:
            self.power_ups.append(PowerUp(self))

    def getSnakes(self):
        return self.snakes

    def getPowerUps(self):
        return self.power_ups

    def getSize(self):
        return self.size

    def giveInput(self):
        for P in self.snakes:
            P.giveInput()

    def move(self):

        for P in self.power_ups:
            P.liveTick()
            if P.getLiveTime() <= 0:
                self.power_ups.remove(P)

        self.setPowerUp()

        for P in self.snakes:
            P.move()

        for P in self.snakes:
            if P.isOut():
                print("Reset: Hit Boarder")
                P.setReset()
                for S in self.snakes:
                    if S != P:
                        S.addScore(25)
            if P.isMoving():
                pos = P.getPos()
                for p in self.snakes:
                    if p == P:
                        for i in p.getBody()[:-2]:
                            if i.getPos() == pos:
                                print("Reset: Hit Himself")
                                P.setReset()
                                for S in self.snakes:
                                    if S != P:
                                        S.addScore(25)
                    else:
                        for i in p.getBody():
                            if i.getPos() == P.getPos():
                                print("Reset: Hit Other Player")
                                P.setReset()
                                for S in self.snakes:
                                    if S != P:
                                        if S == p:
                                            S.addScore(100)
                                        else:
                                            S.addScore(25)

        snakes = self.getSnakes().copy()
        x = 0
        while x < len(snakes):
            y = 1
            while y < len(snakes):
                if snakes[y].getScore() > snakes[y - 1].getScore():
                    temp = snakes[y - 1]
                    snakes[y - 1] = snakes[y]
                    snakes[y] = temp
                y = y + 1
            x = x + 1

        HighScore = snakes[0].getScore()
        for S in snakes:
            diff = HighScore-S.getScore()
            mult = 1
            if diff > 500:
                mult = diff/500
            for P in self.power_ups:
                if S.getBody()[-1].getPos() == P.getPos():
                    self.power_ups.remove(P)
                    SM.play(1)
                    type = P.getType()
                    if type == "DEF":
                        S.addScore(round(100*mult))
                        S.addLen()
                    if type == "GOLD":
                        S.addScore(round(150*mult))
                        S.addLenCount(2)
                    if type == "SHORT":
                        S.addScore(round(50*mult))
                        S.addScore(round((len(S.getBody())-3)*10*mult))
                        S.setLen(3)
                    if type == "INF_LEN":
                        S.addScore(round(60*mult))
                        S.setLen(1000)

    def shouldRun(self):
        if not CM.isRunning:
            return False
        if self.time_min >= self.length:
            print("Game ended by Time")
            return False
        else:
            return True

    def Run(self):
        isRunning = True
        clock = pygame.time.Clock()
        tick = 0
        sec = 5

        # waits 10sec before Game start (with a timer on Screen)
        while sec > 0:
            pygame.time.delay(20)
            clock.tick(1)
            Window.checkInput()
            Window.drawWaitScreen(sec)
            sec = sec-1

        # Clears Input before Game start
        for P in self.players:
            P.getInput()

        # Main Game loop
        while isRunning:
            pygame.time.delay(20)
            clock.tick(data.CLOCK_SPEED)
            if tick >= data.CLOCK_SPEED: # Time system for the Game Clock
                self.tick()
                tick = 0
            else:
                tick = tick+1

            # checking key input
            input = Window.checkInput()
            if input is not None:
                if input[pygame.K_SPACE]:
                    print("Game ended by pressing 'Space'")
                    break
            self.giveInput() # checks input of the Players
            self.move()  # moves the snakes
            Window.drawGameFrame(self) # sets screen
            SM.enable(True)
            isRunning = self.shouldRun() # checks if game time is over

        SM.enable(False)
        winner = []
        winner.append(self.snakes[0])
        for P in self.snakes[1:]:
            if P.getScore() > winner[0].getScore():
                winner.clear()
                winner.append(P)
            elif P.getScore() == winner[0].getScore():
                winner.append(P)

        while CM.isRunning:
            pygame.time.delay(20)
            clock.tick(data.CLOCK_SPEED)
            Window.drawEndScreen(self, winner)
            input = Window.checkInput()
            Players = data.Players
            for P in Players:
                P.getController()
            if input is not None:
                if input[13]:  # index 13=Enter
                    start(self.size, self.length, activePlayers())
                    break
                elif input[pygame.K_SPACE]:
                    break

def activePlayers():
    Players = data.Players
    Aplayers = []
    for P in Players:
        if P.isActive():
            Aplayers.append(P)

    return Aplayers
