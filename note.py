from enum import Enum
import pygame
from utilities.beatsaber_converter import beat_to_milliseconds, line_center_coordinate_y, line_height, line_top_coordinate_y, milliseconds_to_beats
from utilities.spritesheet import SpriteSheet

#animation interval
IMAGE_INTERVAL = 50

class NoteStates(Enum):
    NORMAL = 0
    ACTIVATED = 1
    MISSED = 2

class Note(pygame.sprite.Sprite):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.images = []
        
        #note properties. There are plenty, but because in some advanced levels jumpspeed and bpm can be variable,
        #for future releases it would be advisable to pass those. So I do.
        self.target = kwargs["target"]
        self.line = kwargs["line"]
        self.jumpspeed = kwargs["jumpspeed"]
        self.bpm = kwargs["bpm"]

        #animations
        self.state = NoteStates.NORMAL
        self.last_update = 0
        self.frame = 0
        self.normal = [
            #create a square sprite that will be exactly a line tall
            pygame.transform.scale(img, (line_height()/2,line_height()/2)) 
            for img in SpriteSheet("assets/sprites/Note/normal.png").load_strip((0,0,17,17), 4, colorkey=-1)
        ]
        self.missed = [
            pygame.transform.scale(img, (line_height()/2,line_height()/2)) 
            for img in SpriteSheet("assets/sprites/Note/missed.png").load_strip((0,0,17,17), 4, colorkey=-1)
        ]
        self.animation_mapping = {NoteStates.NORMAL: self.normal, NoteStates.MISSED: self.missed}
        self.image = self.normal[0] 
        # centered so that it looks nice, x = current_w (so the picture is hidden), y = the top coordinate of the note line
        self.rect = self.image.get_rect(center=(pygame.display.Info().current_w+0.5*self.image.get_width(), line_center_coordinate_y(self.line)))


    def update_sprite(self):
        if pygame.time.get_ticks() - self.last_update > IMAGE_INTERVAL:
            self.last_update = pygame.time.get_ticks()
            if self.frame < len(self.animation_mapping[self.state]) - 1:
                self.frame += 1
            else:
                self.frame = 0
            self.image = self.animation_mapping[self.state][self.frame]
    
    def update_state(self):
        # all animations except normal mode should only be played once
        if self.frame == len(self.animation_mapping[self.state]) - 1:
            if self.state == NoteStates.MISSED:
                self.kill()

    def update(self) -> None:
        #using line_height halved because character is always line_height() wide, and we may still hit a note while it comes through us
        #this will be officially the perfect timing to beat a note and get max score
        #some tolerance will be provided, too
        total_distance = pygame.display.Info().current_w 
        speed = total_distance / beat_to_milliseconds(self.bpm, self.jumpspeed) # px/ms

        # We have to calculate the exact position rather than (static) velocity due to timing issues
        # We can't trust FPS or Clock or main loop to be called within same periods of time, so I can only use calculations based on 
        # song position and reset the position of the note every time. Works pretty well though
        current_position_x = speed * (beat_to_milliseconds(self.bpm, self.target) - pygame.mixer.music.get_pos())

        if self.state == NoteStates.NORMAL:
            self.rect.x = current_position_x
        if self.rect.x <= 10: 
            self.state = NoteStates.MISSED
            self.frames = 0
        self.update_state()
        self.update_sprite() 

    pass