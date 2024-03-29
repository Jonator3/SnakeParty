import random

import eel

import setup
from AdvancedTiming import Clock
import time
import SharedData as SD
import WebServer
from Logger import logged_print as print


games = []


class PowerUp(object):
    
    def __init__(self, game):
        self.pos = game.getFreePos()
        self.type = self.getRandomType()
        self.liveTime = random.randint(10000 // setup.FRAME_TIME, 20000 // setup.FRAME_TIME)
        
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
        if self.type == "INF_LEN":
            return "c"
        elif self.type == "GOLD":
            return "b"
        elif self.type == "SHORT":
            return "d"
        else:
            return "a"

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

    def __init__(self, game, index, player, colour):
        self.player = player
        self.underdog = 1
        self.index = index
        self.game = game
        self.color = colour
        self.len = 3
        self.movement = [0, 0]
        self.hasMovement = False
        self.pos = [0, 0]
        self.body = []
        self.score = 0
        self.reset()
        self.resetTag = False

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
                    self.movement = [1, 0]
                elif input[3]:
                    self.movement = [-1, 0]
        else:
            if input[0]:
                self.movement = [0, -1]
                self.hasMovement = True
            elif input[1]:
                self.movement = [1, 0]
                self.hasMovement = True
            elif input[2]:
                self.movement = [0, 1]
                self.hasMovement = True
            elif input[3]:
                self.movement = [-1, 0]
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
        self.resetTag = True

    def setUnderdog(self, int):
        self.underdog = int


class Game(object):

    def __init__(self, size, length, Players, Lobby):
        self.lobby = Lobby
        self.players = Players
        self.size = size
        self.length = length
        self.time_sec = 0
        self.power_ups = []
        self.snakes = []
        self.clock = Clock()
        self.end = False

        i = 0
        for P in Players:
            self.snakes.append(Snake(self, i, SD.client_dict.get(P), Lobby.colours.get(P)))
            i = i+1

    def tick(self):
        self.time_sec = self.time_sec + 1

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
                                P.setReset()
                                for S in self.snakes:
                                    if S != P:
                                        S.addScore(25)
                    else:
                        for i in p.getBody():
                            if i.getPos() == P.getPos():
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
        if self.end:
            self.end = False
            return False
        if self.time_sec >= self.length * 60:
            print(self.lobby.id, "Game ended")
            return False
        else:
            return True

    def Run(self):
        self.end = False
        games.append(self)
        print(self.lobby.id, "Game started")
        tick = 0
        sec = 5

        # waits before Game start
        while sec > 0:
            sendWaitScreen(self, sec)
            sec = sec-1
            self.clock.tick(1000)

        # Clears Input before Game start
        for P in self.players:
            SD.client_dict.get(P).getInput()

        # Main Game loop
        while self.shouldRun():  # ends when time is over
            self.clock.tick(setup.FRAME_TIME)
            # Time system for the Game Clock
            if tick >= 1000:
                self.tick()
                tick -= 1000
            tick += setup.FRAME_TIME

            self.giveInput()    # checks input of the Players
            self.move()         # moves the snakes
            sendGameScreen(self)
            if len(self.lobby.players) == 0:
                return

        winner = [self.snakes[0]]
        for P in self.snakes[1:]:
            if P.getScore() > winner[0].getScore():
                winner.clear()
                winner.append(P)
            elif P.getScore() == winner[0].getScore():
                winner.append(P)

        self.clock.tick(setup.FRAME_TIME)
        for i in range(5):
            sendEndScreen(self, winner)
            time.sleep(1)
        # Clears Input on Game end
        for P in self.players:
            SD.client_dict.get(P).getInput()
        games.remove(self)


def sendGameScreen(game: Game):
    size = hex(game.getSize())[2:]
    time = hex((game.length * 60) - (game.time_sec + 1))[2:]
    msg = ""
    for S in game.getSnakes():
        assembly = []
        for B in S.getBody():
            pos = B.getPos()
            if(pos[0] < 0 or pos[1] < 0 or pos[0] >= game.getSize() or pos[1] >= game.getSize()):
                continue
            if len(assembly) == 0:
                assembly.append([B.getColor(), pos[1], pos[0], 1, 1])
            elif assembly[-1][1] == pos[1] and assembly[-1][4] == 1:
                assembly[-1] = [B.getColor(), pos[1], min(pos[0], assembly[-1][2]), assembly[-1][3]+1, 1]
            elif assembly[-1][2] == pos[0] and assembly[-1][3] == 1:
                assembly[-1] = [B.getColor(), min(pos[1], assembly[-1][1]), pos[0], 1, assembly[-1][4]+1]
            else:
                assembly.append([B.getColor(), pos[1], pos[0], 1, 1])
        for ass in assembly:
            msg += "," + hex(ass[0])[2:] + "." + hex(ass[1])[2:] + "." + hex(ass[2])[2:] + "." + hex(ass[3])[2:] + "." + hex(ass[4])[2:]
    msg = msg[1:]
    for item in game.getPowerUps():
        pos = item.getPos()
        sprite = item.getColor()
        msg += "," + sprite + "." + hex(pos[1])[2:] + "." + hex(pos[0])[2:]
    snakes = game.getSnakes().copy()
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

    board = ""
    for S in snakes:
        board += ";" + hex(S.getColor())[2:] + "," + hex(S.getScore())[2:]
    eel.drawGame(game.getSize(), (game.length * 60) - (game.time_sec + 1), msg.split(","), board[1:].split(";"))
    for C in game.players:
        WebServer.send_message(C, "G:" + msg + ";" + size + ";" + time + board)
        WebServer.send_message(C, "")


def sendWaitScreen(game: Game, sec: int):
    eel.drawWaitGame(sec)
    for C in game.players:
        WebServer.send_message(C, "W:" + hex(sec)[2:])
        WebServer.send_message(C,"")


def sendEndScreen(game: Game, winner):
    col = winner[0].getColor()
    msg = hex(col)[2:]
    eel.drawEndGame(col)
    for C in game.players:
        WebServer.send_message(C, "E:" + msg)
        WebServer.send_message(C,"")


def sendMenuScreen(lobby):
    freeColours = lobby.getFreeColours()
    size = setup.SIZE_SET[lobby.fieldsize]
    time = lobby.playtime
    eel.draw_menu(freeColours, size, time)
    if len(lobby.players) <= 0:
        return
    msg = "M:"
    for c in freeColours:
        msg += hex(c)[2:]
    msg += ";" + str(time) + ";" + str(size) + ";"
    for C in lobby.players:
        pos = lobby.cursors.get(C)
        if pos is None:
            pos = "c0"
            lobby.cursors[C] = "c0"
            print("Why is it None?")
        h = "0"
        WebServer.send_message(C, msg + h + ";" + pos)
        WebServer.send_message(C, "")


@eel.expose
def close_game():
    for game in games:
        game.end = True
