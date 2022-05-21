import json
from hero import Hero, HeroStates
import pygame
from note import Note
from utilities import parallax
from utilities.beatsaber_converter import beat_to_milliseconds, get_music_file, milliseconds_to_beats
import os
from math import inf
from pygame.locals import *

MUSIC_END = pygame.USEREVENT+1

class Level:
    def __init__(self, level_folder: str, beatmap_type: str, beatmap_difficulty: str) -> None:
        self.font = pygame.font.Font("assets/fonts/JetBrainsMonoNL-Bold.ttf", 32)
        self.level_folder = level_folder

        # add background
        self.background = parallax.ParallaxSurface(
            (pygame.display.Info().current_w, pygame.display.Info().current_h),
            pygame.RLEACCEL
        )
        bg_folder = "assets/backgrounds/sunset"
        size = (pygame.display.Info().current_w,
                pygame.display.Info().current_h)
        self.background.add(os.path.join(bg_folder, "bg.png"), inf, size)
        self.background.add(os.path.join(bg_folder, "l0.png"), 7, size)
        self.background.add(os.path.join(bg_folder, "l1.png"), 5, size)
        self.background.add(os.path.join(bg_folder, "l2.png"), 3, size)
        self.background.add(os.path.join(bg_folder, "l3.png"), 1, size)

        # read the level config
        with open(os.path.join(level_folder, "Info.dat")) as info_file:
            info = json.load(info_file)
        self.bpm = info['_beatsPerMinute']
        
        # get the level info from the info file (search for the needed bitset and definition)
        beatset = next(x for x in info["_difficultyBeatmapSets"]
                       if x["_beatmapCharacteristicName"] == beatmap_type)
        level_parameters = next(
            x for x in beatset['_difficultyBeatmaps'] if x['_difficulty'] == beatmap_difficulty)
        
        self.noteJumpMovementSpeed = level_parameters['_noteJumpMovementSpeed']
        self.music = os.path.join(
            self.level_folder, get_music_file(self.level_folder))
        
        # load up the notes
        with open(os.path.join(level_folder, level_parameters['_beatmapFilename'])) as level_definition:
            self.level_definition = json.load(level_definition)
        self.upcoming_notes = self.level_definition['_notes']
        self.upcoming_notes.sort(key=lambda x: x["_time"])

        #group for "enemies"
        self.notes = pygame.sprite.Group()
        #separate group for activated/missed notes to not overwhelm collision detection
        self.dying_notes = pygame.sprite.Group()
        # create a hero!
        self.hero_group = pygame.sprite.GroupSingle()
        self.hero = Hero(max_health=100)
        self.hero_group.add(self.hero)


    def start(self):
        display = pygame.display.get_surface()
        pygame.mouse.set_visible(False)

        run = True
        bg_scroll_speed = 0

        pygame.mixer.music.load(self.music)

        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(MUSIC_END)

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == MUSIC_END:
                    pygame.mixer.music.stop()
                    run = False

            key_pressed = pygame.key.get_pressed()

            if self.hero.state == HeroStates.ATTACKING:
                collided_notes = pygame.sprite.spritecollide(self.hero, self.notes, False, collided=pygame.sprite.collide_rect_ratio(.45))
                for note in collided_notes:
                    #you can get 100 points at max if you kill the note precisely at the target beat. 300ms tolerance, otherwise you get 0 
                    # (realistically, you can't even collide with it farther than 300ms - the note is either already gone or too far away)
                    self.dying_notes.add(note)
                    self.notes.remove(note)

                    rank = int((1 - (beat_to_milliseconds(self.bpm, note.target) - pygame.mixer.music.get_pos())/300) * 100)
                    self.hero.score += max(0, rank)    # type: ignore

            if key_pressed[pygame.K_1]:
                self.hero.move_line(0)
            if key_pressed[pygame.K_2]:
                self.hero.move_line(1)
            if key_pressed[pygame.K_3]:
                self.hero.move_line(2)
            if key_pressed[pygame.K_4]:
                self.hero.move_line(3)

            for note in self.upcoming_notes:
                # level definition has beats in ["_time"] field rather than time. Hence the conversion
                # 150 is the small statc timeout for the sprite to "slide out" from the right corner rather than appearing abruptly
                if note["_time"] <= milliseconds_to_beats(self.bpm, pygame.mixer.music.get_pos()) + self.noteJumpMovementSpeed + 150:
                    self.notes.add(Note(
                        line=note["_lineIndex"], target=note["_time"], jumpspeed=self.noteJumpMovementSpeed, bpm=self.bpm))
                    del self.upcoming_notes[0]
                else:
                    break
            #total and current score
            total_score = self.font.render("Total:" + str(self.hero.score), True, "#b884d5")
            self.notes.update()
            self.hero.update()

            bg_scroll_speed = 4
            # Move the background with the set scroll_speed
            self.background.scroll(bg_scroll_speed)
            self.background.draw(display)
            self.notes.draw(display)
            self.hero_group.draw(display)
            display.blit(total_score, (pygame.display.Info().current_w//2+10, 30))
            pygame.display.flip()
        return self.hero.score
