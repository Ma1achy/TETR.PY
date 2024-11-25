import pygame
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import pygame_gui as gui
from utils import hex_to_rgb
import json
from render.GUI.menu import Menu

class Render():
    def __init__(self, Config, Timing, Debug, GameInstances):
        """
        args:
            self.window (pygame.Surface): the window to render the game onto
        """
        
        self.Config = Config
        self.Timing = Timing
        self.Debug = Debug
        self.RenderStruct =  StructRender()
        self.GameInstances = GameInstances
        
        self.icon = pygame.image.load('resources/icon.png')
        self.window = self.__init_window()
        
        self.image_path = 'resources/background/b1.jpg'
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT))
        
        self.darken_overlay_layer = pygame.Surface((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.SRCALPHA)
        self.darken_overlay_layer_alpha = 200
        
        # self.play_multi_button = Button(
        #     type = 'button',
        #     tl_pos_x = self.RenderStruct.WINDOW_WIDTH // 4,
        #     tl_pos_y = 50,
        #     width = self.RenderStruct.WINDOW_WIDTH,
        #     height = 100,
        #     display_text = '',
        #     object_id = 'play_multi',
        #     background_colour = '#34222d',
        #     left_border = (3, '#3c2734'),
        #     right_border = (3, '#3c2734'),
        #     top_border = (3, '#472d3c'),
        #     bottom_border = (3, '#271b22'),
        #     Timing = self.Timing
        # )
        
        # self.play_solo_button = Button(
        #     type = 'button',
        #     tl_pos_x = self.RenderStruct.WINDOW_WIDTH // 4,
        #     tl_pos_y = 160,
        #     width = self.RenderStruct.WINDOW_WIDTH,
        #     height = 100,
        #     display_text = '',
        #     object_id = 'play_solo',
        #     background_colour = '#1e1d2d',
        #     left_border = (3, '#272639'),
        #     right_border = (3, '#272639'),
        #     top_border = (3, '#2e2d42'),
        #     bottom_border = (3, '#12111b'),
        #     Timing = self.Timing
        # )
        
        # self.channel_button = Button(
        #     type = 'button',
        #     tl_pos_x = 0,
        #     tl_pos_y = 0,
        #     width = self.RenderStruct.WINDOW_WIDTH,
        #     height = 75,
        #     display_text = '',
        #     object_id = 'channel',
        #     background_colour = '#1c3e2a',
        #     left_border = (3, '#1e4822'),
        #     right_border = (3, '#1e4822'),
        #     top_border = (3, '#1d6429'),
        #     bottom_border = (3, '#0e130f'),
        #     Timing = self.Timing
        # )

        # self.config_button = Button(
        #     type = 'button',
        #     tl_pos_x = self.RenderStruct.WINDOW_WIDTH // 4,
        #     tl_pos_y = 380,
        #     width = self.RenderStruct.WINDOW_WIDTH,
        #     height = 100,
        #     display_text = '',
        #     object_id = 'config',
        #     background_colour = '#1c263e',
        #     left_border = (3, '#1e2a48'),
        #     right_border = (3, '#1e2a48'),
        #     top_border = (3, '#1d3164'),
        #     bottom_border = (3, '#0e0f13'),
        #     Timing = self.Timing
        # )
           
        # self.about_button = Button(
        #     type = 'button',
        #     tl_pos_x = self.RenderStruct.WINDOW_WIDTH // 4,
        #     tl_pos_y = 490,
        #     width = self.RenderStruct.WINDOW_WIDTH,
        #     height = 100,
        #     display_text = '',
        #     object_id = 'about',
        #     background_colour = '#2a2a2a',
        #     left_border = (3, '#262626'),
        #     right_border = (3, '#262626'),
        #     top_border = (3, '#2a2a2a'),
        #     bottom_border = (3, '#131313'),
        #     Timing = self.Timing
        # )     
        
        self.main_menu = Menu(self.window, self.Config, self.Timing)

    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption(self.RenderStruct.CAPTION)
        return pygame.display.set_mode((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)

    def draw_frame(self):
        
        if self.Timing.frame_delta_time <= 0:
            self.dt = 1 / self.Config.FPS
        else:
            self.dt = self.Timing.frame_delta_time
                    
        self.window.blit(self.image, (0, 0))
        self.darken_overlay_layer.fill((0, 0, 0, self.darken_overlay_layer_alpha))
        self.window.blit(self.darken_overlay_layer, (0, 0))
        # self.play_multi_button.update(self.window)
        # self.play_solo_button.update(self.window)
        # self.channel_button.update(self.window)
        # self.config_button.update(self.window)
        # self.about_button.update(self.window)
        self.main_menu.draw()
        pygame.display.flip()

import pygame

# class Button:
#     def __init__(self, type, tl_pos_x, tl_pos_y, width, height, display_text, object_id, background_colour, left_border, right_border, top_border, bottom_border, Timing):
#         self.type = type       
#         self.rect = pygame.Rect(tl_pos_x, tl_pos_y, width, height)
#         self.display_text = display_text
#         self.object_id = object_id
        
#         self.background_colour = background_colour
#         self.left_border_width, self.left_colour = left_border
#         self.right_border_width, self.right_colour = right_border
#         self.top_border_width, self.top_colour = top_border
#         self.bottom_border_width, self.bottom_colour = bottom_border
        
#         self.Timing = Timing
#         self.hover = False
        
#     def draw(self, surface):
        
#         pygame.draw.rect(surface, hex_to_rgb(self.background_colour), (self.rect.x, self.rect.y, self.rect.width, self.rect.height))
#         pygame.draw.line(surface, hex_to_rgb(self.left_colour), (self.rect.x + self.left_border_width // 2, self.rect.y), (self.rect.x + self.left_border_width // 2, self.rect.y + self.rect.height), self.left_border_width)
#         pygame.draw.line(surface, hex_to_rgb(self.right_colour), (self.rect.x + self.rect.width - self.right_border_width // 2, self.rect.y), (self.rect.x + self.rect.width - self.right_border_width // 2, self.rect.y + self.rect.height), self.right_border_width)
#         pygame.draw.line(surface, hex_to_rgb(self.top_colour), (self.rect.x, self.rect.y + self.top_border_width // 2), (self.rect.x + self.rect.width, self.rect.y + self.top_border_width // 2), self.top_border_width)
#         pygame.draw.line(surface, hex_to_rgb(self.bottom_colour), (self.rect.x, self.rect.y + self.rect.height - self.bottom_border_width // 2), (self.rect.x + self.rect.width, self.rect.y + self.rect.height - self.bottom_border_width // 2), self.bottom_border_width)

#     def update_image(self, surface):
#         self.draw(surface)
      
#     def get_relative_rect(self):
#         return self.rect
    
#     def check_hover(self, mouse_pos):
#         if self.rect.collidepoint(mouse_pos):
#             return True
#         return False
    
#     def update(self, surface):
#         self.hover = self.check_hover(pygame.mouse.get_pos())
#         self.update_image(surface)

class MenuTest():
    def __init__(self, Config, Timing):
        self.Config = Config
        self.Timing = Timing
        
        self.definition = {
            'menu_header': {
                    'background': {
                    'style': 'linear_gradient', 
                    'colours': ('#272931', '#17191d')
                },
                'border': {
                    'bottom': (2, '#343642'),
                },
                'text': {
                    'colour': '#898fa2', 
                    'display_text': 'HOME'
                },
                },
            'menu_body': {
                'container': {
                    'type': 'list', 'elements': [
                        {
                            'type': 'bar_main_menu',
                            'function': 'go_to_multi',
                            'main_text': {
                                'colour': '#e9bed9',
                                'display_text': 'MULTIPLAYER'
                            },
                            'sub_text': {
                                'colour': '#c09ab3',
                                'display_text':'Play with friends and foes'
                            },
                            'image': 'resources/buttons/play_multi.png',
                            'background': {
                                'style': 'solid',
                                'colour': '#34222d',
                            },
                            'border': {
                                'left': (3, '#3c2734'),
                                'top': (3, '#472d3c'),
                                'bottom': (3, '#271b22')
                            }
                        },
                        {
                            'type': 'bar_main_menu',
                            'function': 'go_to_solo',
                            'main_text': {
                                'colour': '#bab8dc',
                                'display_text': 'SOLO'
                            },
                            'sub_text': {
                                'colour': '#8b88bc',
                                'display_text': 'Challenge yourself and top the leaderboards'
                            },
                            'image': 'resources/buttons/play_solo.png',
                            'background': {
                                'style': 'solid',
                                'colour': '#1e1d2d',
                            },
                            'border': {
                                'left': (3, '#272639'),
                                'top': (3, '#2e2d42'),
                                'bottom': (3, '#12111b')
                            }
                        },
                        {
                            'type': 'bar_main_menu',
                            'function': 'go_to_channel',
                            'main_text': {
                                'colour': '#a6fca3',
                                'display_text': 'RECORDS'
                            },
                            'sub_text': {
                                'colour': '#70be6d',
                                'display_text': 'Leaderboards, Replays and more'
                                },
                            'image': 'resources/buttons/records.png',
                            'background': {
                                'style': 'solid',
                                'colour': '#1c3e2a',
                            },
                            'border': {
                                'left': (3, '#1e4822'),
                                'top': (3, '#1d6429'),
                                'bottom': (3, '#0e130f')
                            }
                        },
                        {
                            'type': 'bar_main_menu',
                            'function': 'go_to_config',
                            'main_text': {
                                'colour': '#90aef9',
                                'display_text': 'CONFIG'
                            },
                            'sub_text': {
                                'colour': '#5668ba',
                                'display_text': 'Tweak your TETR.PY experience'
                            },
                            'image': 'resources/buttons/config.png',
                            'background': {
                                'style': 'solid',
                                'colour': '#1c263e',
                            },
                            'border': {
                                'left': (3, '#1e2a48'),
                                'top': (3, '#1d3164'),
                                'bottom': (3, '#0e0f13')
                            }
                        },
                        {
                            'type': 'bar_main_menu',
                            'function': 'go_to_about',
                            'main_text': {
                                'colour': '#c0c0c0',
                                'display_text': 'ABOUT'
                            },
                            'sub_text': {
                                'colour': '#a0a0a0',
                                'display_text': 'All about TETR.PY'
                            },
                            'image': 'resources/buttons/about.png',
                            'background': {
                                'style': 'solid',
                                'colour': '#2a2a2a',
                            },
                            'border': {
                                'left': (3, '#262626'),
                                'top': (3, '#2a2a2a'),
                                'bottom': (3, '#131313')
                            }
                        },
                    ]
                },
                'container': {
                'type': 'fixed', 'elements': [
                    {
                        'type': 'exit_game',
                        'function': 'exit_game',
                        'main_text': {
                            'colour': '#c9c9c9',
                            'display_text': 'EXIT'
                        },
                        'background': {
                            'style': 'solid',
                            'colour': '#242424',
                        },
                        'border': {
                            'right': (3, '#181818'),
                            'top': (3, '#3d3d3d'),
                            'bottom': (3, '#0e0e0e')
                        }
                    },
                ]
            },      
            'menu_footer': {
                'background': {
                    'style': 'linear_gradient', 
                    'colours': ('#272931', '#17191d')
                },
                'border': {
                    'top': (2, '#343642'),
                },
                'text': {
                    'colour': '#898fa2', 
                    'display_text': 'WELCOME TO TETR.PY'
                },
            }
        }
    }
        
    def create_menu(self):
        pass
        
        
    
        
    
@dataclass
class StructRender():
    CAPTION = 'TETR.PY'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900

