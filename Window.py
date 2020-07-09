import sys
import ctypes
import math

import data
import ControllerManager as CM

import pygame


myappid = 'SnakeParty' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

pygame.init()
pygame.mouse.set_visible(False)
icon = pygame.image.load(data.ICON)
pygame.display.set_icon(icon)
Screen: pygame.Surface = pygame.Surface((800, 600))
Window: pygame.Surface = pygame.display.set_mode(pygame.display.list_modes()[0], pygame.FULLSCREEN | pygame.NOFRAME)
pygame.display.set_caption("Snake Party")
LineSize = 50
Font = pygame.font.Font(data.FONT, 40)
MiniFont = pygame.font.Font(data.FONT, 27)

Screen.fill([60, 60, 60])
text = Font.render("LOADING", True, [200, 200, 200])
Screen.blit(text, (((800 - text.get_width()) / 2), (600 - text.get_height()) / 2))


def update():
    h = Window.get_height()
    w = math.floor(Screen.get_width() * (h / Screen.get_height()))
    screen_resize = pygame.transform.scale(Screen, (w, h))
    Window.fill((0, 0, 0))
    Window.blit(screen_resize, (Window.get_width()//2 - (w // 2), 0))
    pygame.display.update()

update()


def drawGameFrame(game):
    pixRes = 600/game.getSize()

    Screen.fill([60, 60, 60])
    pygame.draw.rect(Screen, [40, 40, 40], (600, 0, 200, 600))

    for P in game.getPowerUps():
        snack = P.getPos()
        x = (snack[0] * pixRes) + (pixRes / 2)
        y = (snack[1] * pixRes) + (pixRes / 2)
        w1 = 34
        w2 = 20
        if pixRes == 40:
            w1 = 34
            w2 = 20
        elif pixRes == 30:
            w1 = 26
            w2 = 16
        elif pixRes == 24:
            w1 = 20
            w2 = 12
        elif pixRes == 20:
            w1 = 16
            w2 = 10

        pygame.draw.rect(Screen, P.getColor(), (x - (w1 / 2), y - (w1 / 2), w1, w1))
        pygame.draw.rect(Screen, [0, 255, 0], (x - (w2 / 2), y - (w2 / 2), w2, w2))

    for S in game.getSnakes():
        for B in S.getBody():
            if B.isIn():
                pos = B.getPos()
                color = B.getColor()
                pygame.draw.rect(Screen, color, (pos[0] * pixRes, pos[1] * pixRes, pixRes, pixRes))

    clock = Font.render(game.time(), True, [255, 255, 255])
    Screen.blit(clock, (750 - clock.get_width(), 5))

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
    
    step = 100
    for S in snakes:
        text = Font.render(str(S.getScore()), True, S.getColor())
        Screen.blit(text, (795 - text.get_width(), step))
        step = step+LineSize

    update()


def drawWaitScreen(time):
    Screen.fill([60, 60, 60])

    text = Font.render(str(time), True, [200, 200, 200])
    Screen.blit(text, (((800 - text.get_width()) / 2), 280))

    text = MiniFont.render("Game starts in:", True, [200, 200, 200])
    Screen.blit(text, (((800 - text.get_width()) / 2), 200))

    update()


def drawMenu(state, length, size, qr, link, acc, inacc):
    Screen.fill([60, 60, 60])

    textLen = Font.render(str(length)+"min", True, [255, 255, 255])
    textSize = Font.render(str(size), True, [255, 255, 255])
    textStart = Font.render("Start", True, [255, 255, 255])

    if len(acc) < 1:
        textStart = Font.render("Start", True, [170, 170, 170])

    pygame.draw.rect(Screen, [240, 130, 20], ((state*200)+100, 140, 200, LineSize+20))

    Screen.blit(textLen, (((200-textLen.get_width())/2)+100, 150))
    Screen.blit(textSize, (((200 - textSize.get_width()) / 2) + 300, 150))
    Screen.blit(textStart, (((200 - textStart.get_width()) / 2) + 500, 150))
    Screen.blit(qr, (0, 600-qr.get_height()))

    set = qr.get_width() + 20

    text = MiniFont.render("Used Colores:", True, [180, 180, 180])
    Screen.blit(text, (set, 250))

    step = set
    for C in acc:
        pygame.draw.rect(Screen, C, (step, 280, 35, 35))
        step = step + 40

    text = MiniFont.render("Free Colores:", True, [180, 180, 180])
    Screen.blit(text, (set, 330))

    step = set
    for C in inacc:
        pygame.draw.rect(Screen, C, (step, 360, 35, 35))
        step = step + 40

    text = MiniFont.render("Length", True, [180, 180, 180])
    Screen.blit(text, (((200-text.get_width())/2)+100, 95))

    text = MiniFont.render("Map Size", True, [180, 180, 180])
    Screen.blit(text, (((200 - text.get_width()) / 2) + 300, 95))

    text = MiniFont.render(link, True, [180, 180, 180])
    Screen.blit(text, (360, 600-text.get_height()))

    update()


def drawEndScreen(game, Player):
    Screen.fill([60, 60, 60])
    pygame.draw.rect(Screen, [40, 40, 40], (600, 0, 200, 600))

    step = (600-((len(Player)+1)*LineSize))/2
    for S in Player:
        text = Font.render(S.getName(), True, S.getColor())
        Screen.blit(text, ((600 - text.get_width())/2, step))
        step = step + LineSize

    text = Font.render("Won!", True, [255, 255, 255])
    Screen.blit(text, ((600 - text.get_width()) / 2, step))

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

    step = 100
    for S in snakes:
        text = Font.render(str(S.getScore()), True, S.getColor())
        Screen.blit(text, (795 - text.get_width(), step))
        step = step + LineSize

    update()
        

def checkInput():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            CM.stop()
            sys.exit(0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_END]:
            pygame.quit()
            CM.stop()
            sys.exit(0)
        return keys
