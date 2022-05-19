import json
import pygame
import level_map
import pygame_menu
import os


class MenuTheme(pygame_menu.Theme):
    def __init__(self) -> None:
        super().__init__()
        conf = {
                'font_path': 'assets/fonts/JetBrainsMono-Regular.ttf',
                'button_color' :'#FFFFFF',
                'back_color': "#000000",
                'font_color': "#b884d5",
                'button_color': "#FFFFFF",
                'name_font_size': 90,
                'buttons_font_size': 60
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


class Menu:
    def __init__(self, display) -> None:
        self.display = display
        self.theme = MenuTheme()
        self.menu = pygame_menu.Menu('', 
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
                theme=self.theme
                )
        self.menu.add.vertical_fill()
        #self.menu.add.label("Synthwars", font_size=self.theme.title_font_size)
        self.menu.add.image("assets/logo.png")
        self.menu.add.vertical_fill()
        self.menu.add.button('Levels', self._show_levels)
        self.menu.add.vertical_fill()
        self.menu.add.button('Score', self._show_score)
        self.menu.add.vertical_fill()
        self.menu.add.button('Help', self._show_help)
        self.menu.add.vertical_fill()
        self.menu.add.button('Quit', pygame.QUIT)
        self.menu.add.vertical_margin(260)


    def run(self):
        self.menu.mainloop(self.display)


    def _show_score(self):
        pass

    def _show_help(self):
        pass

    def _show_levels(self):
        level_menu = pygame_menu.Menu('',
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
                theme=self.theme,
                center_content=True
                )
        level_menu.add.button("Back to menu", level_menu.disable)
        for level_folder in [f.path for f in os.scandir("levels") if f.is_dir()]:
            with open(os.path.join(level_folder, "Info.dat")) as level_info:
                level = json.load(level_info)
                level_menu.add.button(level["_songName"] + " - " + level["_songAuthorName"], lambda x=level_folder: self._show_difficulty(x))

        level_menu.mainloop(self.display) 

    def _show_difficulty(self,level):
        difficulty_menu = pygame_menu.Menu('Choose difficulty',
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
            theme=self.theme,
            center_content=True
        ) 
        difficulty_menu.add.button("Back to menu", difficulty_menu.disable)

        with open(os.path.join(level, "Info.dat"), 'r') as info:
            level = json.load(info)
            for beatmapSet in level["_difficultyBeatmapSets"]:
                for beatmap in beatmapSet["_difficultyBeatmaps"]:
                    difficulty_menu.add.button(
                        beatmapSet["_beatmapCharacteristicName"] + " - " + beatmap["_difficulty"], 
                        lambda x=beatmap: level_map.start_level(level, x["_beatmapFilename"])
                    )
        
        difficulty_menu.mainloop(self.display) 

        