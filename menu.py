import json
from typing import Optional
import pygame
import level
import pygame_menu
import os

# Constants and global variables
ABOUT = [f'pygame-menu {pygame_menu.__version__}',
         f'Author: {pygame_menu.__author__}',
         f'Email: {pygame_menu.__email__}']
FPS = 60

#this is intended to be more of a persistent storage for the Main Menu and helper functions for it
#because python files are evaluated only once upon import it makes sense to initialize the menu within the body of the module

clock: Optional['pygame.time.Clock'] = None
main_menu: Optional['pygame_menu.Menu'] = None 
surface: Optional['pygame.Surface'] = None
class MenuTheme(pygame_menu.Theme):
    def __init__(self) -> None:
        super().__init__()
        conf = {
                'font_path': 'assets/fonts/JetBrainsMono-Regular.ttf',
                'button_color' :'#FFFFFF',
                'back_color': "#000000",
                'font_color': "#b884d5",
                'button_color': "#FFFFFF",
                'name_font_size': 60,
                'buttons_font_size': 45
                }
        self.background_color = conf['back_color']
        self.widget_font = conf['font_path']
        self.widget_font_color = conf['font_color']
        self.widget_border_color = conf['button_color']
        self.title_font_size = conf['name_font_size']
        self.title_font = conf['font_path']
        self.title_font_color = conf['font_color']
        self.widget_font_size = conf['buttons_font_size']
        #to make it look modern and sleek
        self.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE


def menu_init():
        global main_menu
        menu = pygame_menu.Menu('', 
           pygame.display.Info().current_w,
           pygame.display.Info().current_h,
           theme=MenuTheme(),
           center_content=True,
           )
        menu.add.vertical_fill()
        menu.add.image("assets/logo.png")
        menu.add.vertical_fill()
        menu.add.button('Levels', _levels(_difficulty))
        menu.add.vertical_fill()
        menu.add.button('Score', _levels(_score))
        menu.add.vertical_fill()
        menu.add.button('Help', _help())
        menu.add.vertical_fill()
        menu.add.button('Quit', pygame.QUIT)
        menu.add.vertical_margin(260)
        return menu


def _score(level_folder: str):
    try: 
        with open(os.path.join(level_folder, "scores.json"), "r") as scores_file:
            scores = json.load(scores_file)
    except:
        scores = {}
        info_menu = pygame_menu.Menu("No records yet! Wanna be first?",
        pygame.display.Info().current_w,
        pygame.display.Info().current_h,
        theme=MenuTheme(),
        center_content=True
        )
        return info_menu
    score_menu = pygame_menu.Menu("Scores:",
        pygame.display.Info().current_w,
        pygame.display.Info().current_h,
        theme=MenuTheme(),
        center_content=True
        )
    score_table = score_menu.add.table()   
    for key, value in scores.items():
        score_table.add_row([key, value], cell_align=pygame_menu.locals.ALIGN_LEFT, cell_padding=30)
    return score_menu

def _help():

        theme = MenuTheme()
        help_menu = pygame_menu.Menu('',
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
                theme=theme,
                center_content=False
                )
        help_menu.add.button("Back to menu", pygame_menu.events.BACK)
        help_menu.add.label("Hit the note when it's in front of you! \nYou can get up to 100 points for each note\n")
        table = help_menu.add.table()
        table.add_row(["1, 2, 3, 4", "Attack on line 1/2/3/4"], cell_align=pygame_menu.locals.ALIGN_LEFT, cell_padding=150)
        return help_menu

def _levels(function_on_level):
    level_menu = pygame_menu.Menu('',
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
            center_content=True,
            theme=MenuTheme(),
            )
    level_menu.add.button("Back to menu", pygame_menu.events.BACK)
    for level_folder in [f.path for f in os.scandir("levels") if f.is_dir()]:
        with open(os.path.join(level_folder, "Info.dat")) as level_info:
            level = json.load(level_info)
            level_menu.add.button(level["_songName"] + " - " + level["_songAuthorName"], function_on_level(level_folder))

    return level_menu

def _difficulty(level_folder):
    difficulty_menu = pygame_menu.Menu('Choose difficulty',
        pygame.display.Info().current_w,
        pygame.display.Info().current_h,
        theme=MenuTheme(),
        center_content=True
    ) 
    difficulty_menu.add.button("Back to menu", pygame_menu.events.BACK)

    with open(os.path.join(level_folder, "Info.dat"), 'r') as info:
        level_info = json.load(info)
        for beatmapSet in level_info["_difficultyBeatmapSets"]:
            for beatmap in beatmapSet["_difficultyBeatmaps"]:
                difficulty_menu.add.button(
                    beatmapSet["_beatmapCharacteristicName"] + " - " + beatmap["_difficulty"], 
                    lambda x=beatmap, y=beatmapSet: play(level_folder, level.Level(level_folder, y["_beatmapCharacteristicName"], x["_difficulty"] )))
    
    return difficulty_menu

def _score_saving(title: str):
    name = None
    score_saving_menu = pygame_menu.Menu(title,
        pygame.display.Info().current_w,
        pygame.display.Info().current_h,
        theme=MenuTheme(),
        center_content=True
    ) 
    def name_callback(name_string: str):
        nonlocal name
        name = name_string
    score_saving_menu.add.text_input("Name: ", onchange= name_callback, maxchar=15)
    score_saving_menu.add.vertical_fill()
    score_saving_menu.add.button("Confirm", score_saving_menu.disable)
    score_saving_menu.add.vertical_margin(30)
    score_saving_menu.mainloop(pygame.display.get_surface())
    return name


def play(level_folder: str, level: level.Level):
    main_menu.disable()
    score = level.start()
    with open(os.path.join(level_folder, "scores.json"), "w+") as scores_file:
        try:
            scores = json.load(scores_file)
        #file's empty or doesn't exist. Don't worry, everything happens at some point!
        except json.JSONDecodeError:
            scores = {}
        if score > max(scores.keys(),default=0):
            name = _score_saving("WOAH, THAT'S A RECORD! You should share it...")
        else: name = _score_saving("Mind sharing your results with other players?")
        scores.update({name: score})
        json.dump(scores, scores_file)
    main_menu.enable()


        