from enum import Enum
import pygame
from utilities.spritesheet import SpriteSheet
from utilities.beatsaber_converter import line_height, line_top_coordinate_y

#animation interval
IMAGE_INTERVAL = 50

class HeroStates(Enum):
    RUNNING = 0
    ATTACKING = 1
    GETTING_HIT = 2
    DYING = 3
    

class Hero(pygame.sprite.Sprite):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.max_health = kwargs['max_health']
        self.health = self.max_health
        self.score = 0
        #animation stuff
        self.last_update = 0
        self.frame = 0
        self.attack = [
            #create a square sprite that will be exactly a line tall
            pygame.transform.scale(img, (line_height(),line_height())) 
            for img in SpriteSheet("assets/sprites/Punk/Punk_punch.png").load_strip((0,0,48,48), 4, colorkey=-1)
        ]
        self.run = [
            pygame.transform.scale(img, (line_height(),line_height())) 
            for img in SpriteSheet("assets/sprites/Punk/Punk_run.png").load_strip((0,0,48,48), 6, colorkey=-1)
        ]
        self.animation_mapping = {HeroStates.ATTACKING: self.attack, HeroStates.RUNNING: self.run}

        self.image = self.run[0] 
        self.rect = self.image.get_rect(topleft=(0,0))
        self.state = HeroStates.RUNNING


    def do_attack(self):
        #to disable a glitch when you can constantly attack and freeze on the 0th frame of animation, crushing every note.
        if self.state != HeroStates.ATTACKING:
            self.frame = 0
            self.state = HeroStates.ATTACKING

    def move_line(self, line_number: int):
        self.rect.y = line_top_coordinate_y(line_number)
        self.do_attack()

    def get_damage(self, damage: int) -> None:
        self.health -= damage
        if self.health <= 0:
            self.kill()


    def up_score(self, score):
        self.score += score

    def update_sprite(self):
        if pygame.time.get_ticks() - self.last_update > IMAGE_INTERVAL:
            self.last_update = pygame.time.get_ticks()
            if self.frame < len(self.animation_mapping[self.state]) - 1:
                self.frame += 1
            else:
                self.frame = 0
            self.image = self.animation_mapping[self.state][self.frame]

    def death(self):
        # it was too hard to play this game with deaths so I rolled back into zen mode (with no health and damage)
        pass
    
    def update_state(self):
        if self.frame == len(self.animation_mapping[self.state]) - 1:
            if self.state == HeroStates.DYING:
                self.death()
            else: self.state = HeroStates.RUNNING

    def update(self) -> None:
            self.update_state()
            self.update_sprite()

    # def shoot(self) -> Bullet:
    #     if time.time() > self.current_weapon.last_reload_time + self.current_weapon.reload_time: 
    #         self.current_weapon.reloading = False
    #     bullet = self.current_weapon.fire(self)
    #     self.current_weapon.reloading = True
    #     return bullet
    pass