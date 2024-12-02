import os
import pygame
from utils import hex_to_rgb

class Font():
    def __init__(self, type, size:int = 20):
        """
        Fonts used in the game
        
        args:
            size (int): The size of the font
        """
        self.size = size
        self.base_path = 'resources/font'
        self.type = type
    
        if self.type == 'hun2':

            font_path = os.path.join(self.base_path, 'hun2.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'pfw':

            font_path = os.path.join(self.base_path, 'pfw.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'cr':
            font_path = os.path.join(self.base_path, 'cr.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'action_icons':
            font_path = os.path.join(self.base_path, 'action-icons.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        self.height = self.font.get_height()
                
    def draw(self, surface, text, colour, alignment, h_padding = 0, v_padding = 0, draw_background = None):
        self.rendered_text = self.font.render(text, True, hex_to_rgb(colour))

        if alignment == 'center':
            text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, (surface.get_height() //2 - self.font.get_ascent()//2)))
        elif alignment == 'left':
            text_rect = self.rendered_text.get_rect(topleft = (0, (surface.get_height() //2 - self.font.get_ascent()//2)))
        elif alignment == 'right':
            text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() - self.rendered_text.get_width(), (surface.get_height() //2 - self.font.get_ascent()//2)))
            h_padding = -h_padding
        elif alignment == 'left_top':
            text_rect = self.rendered_text.get_rect(topleft = (0, (self.font.get_ascent()//2)))
        elif alignment == 'right_top':
            text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() - self.rendered_text.get_width(), (self.font.get_ascent()//2)))
            h_padding = -h_padding
        elif alignment == 'left_bottom':
            text_rect = self.rendered_text.get_rect(topleft = (0, (surface.get_height() - self.font.get_height())))
            v_padding = -v_padding
        elif alignment == 'right_bottom':
            text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() - self.rendered_text.get_width(), (surface.get_height() - self.font.get_height())))
            h_padding = -h_padding
            v_padding = -v_padding
        elif alignment == 'top':
            text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, 0))
        elif alignment == 'bottom':
            text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, surface.get_height() - self.font.get_height()))
            v_padding = -v_padding
        
        # Adjust positioning with paddings
        text_rect.x += h_padding
        text_rect.y += v_padding
        if draw_background:
            background_surface = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
            background_surface.fill(draw_background)
            surface.blit(background_surface, text_rect.topleft)
            
        surface.blit(self.rendered_text, text_rect)
    
    def get_width(self):
        return self.rendered_text.get_width()