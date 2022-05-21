
from typing import Optional
import pygame
from pygame.locals import *
import pygame_menu
import menu

pygame.init()
pygame.mixer.init()

display = pygame.display.set_mode((1440,900))
menu.main_menu = menu.menu_init()

menu.main_menu.mainloop(display)