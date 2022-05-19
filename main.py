
import pygame
from pygame.locals import *
from menu import Menu

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
menu = Menu(screen)
menu.run()