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
                
        self.main_menu = Menu(self.window, self.Config, self.Timing, menu_definition = 'render/GUI/menus/home_menu.json')

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


    
        
    
@dataclass
class StructRender():
    CAPTION = 'TETR.PY'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900

