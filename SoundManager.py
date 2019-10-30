import pygame

pygame.init()
pygame.mixer.init(22100, -16, 2, 8)

global Sounds, isEnabled
Sounds = []
isEnabled = False


def addSound(sound):
    global Sounds, isEnabled
    Sounds.append(pygame.mixer.Sound(sound))


def play(index):
    global Sounds, isEnabled
    if isEnabled:
        Sounds[index].play(0)


def enable(state):
    global Sounds, isEnabled
    isEnabled = state


addSound("sounds/reset.wav")
addSound("sounds/score.wav")

