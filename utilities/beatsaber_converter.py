import json
import os.path

import pygame



def get_music_file(level_folder: str):
    with open(os.path.join(level_folder,"Info.dat")) as info_file:
        info = json.load(info_file)
        return info["_songFilename"]


def milliseconds_to_beats(bpm, ms):
    return ms * (bpm/60) / 1000
def beat_to_milliseconds(bpm, beat) -> int: 
    return beat * 1000 / (bpm/60)


#Utils to get the rendering parameters. May change in the future, thus moved to separate functions
#P.S Converting to int due to the way SDL2 handles subpixel rendering (basically it doesn't)
def line_top_coordinate_y(line: int):
    # we will split screen in 4 lines, so, 25%
    screen_height = pygame.display.Info().current_h
    return int(screen_height * 0.25 * line)

def line_height():
    screen_height = pygame.display.Info().current_h
    return int(screen_height * 0.25)

def line_center_coordinate_y(line: int):
    screen_height = pygame.display.Info().current_h
    # we will split screen in 4 lines, so, 25% + 12.5% to move to the center
    return int(screen_height * 0.25 * line + 0.125 * screen_height)

    


