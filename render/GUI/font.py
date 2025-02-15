import os
import pygame
from utils import hex_to_rgb

class Font():
    def __init__(self, type, size:int = 20, styles = None):
        """
        Fonts used in the game
        
        args:
            size (int): The size of the font
        """
        self.size = size
        self.base_path = 'resources/font'
        self.type = type
        self.styles = styles
    
        if self.type == 'hun2':

            font_path = os.path.join(self.base_path, 'hun2.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'pfw':

            font_path = os.path.join(self.base_path, 'pfw.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'cr':
            font_path = os.path.join(self.base_path, 'cr.ttf')
            self.font = pygame.font.Font(font_path, self.size)
            
        elif self.type == 'd_din_bold':
            font_path = os.path.join(self.base_path, 'D-DIN-Bold.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'action_icons':
            font_path = os.path.join(self.base_path, 'action_icons.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        if self.styles is not None:
            self.__apply_styles()
        
        self.height = self.font.get_height()
  
    def draw(self, surface, text, colour, alignment, h_padding = 0, v_padding = 0, draw_background = None, alpha = 1):
        """
        Draw the text on the surface
        
        args:
            surface (pygame.Surface): The surface to draw the text on
            text (str): The text to draw
            colour (str): The colour of the text
            alignment (str): The alignment of the text
            h_padding (int): The horizontal padding of the text
            v_padding (int): The vertical padding of the text
            draw_background (str): The colour of the background
        """
        self.__get_padding(h_padding, v_padding)        
        self.render_text(text, colour)
        self.get_alignment(alignment, surface)
        self.__apply_padding()
        self.__draw_background(surface, colour, draw_background)
        
        alpha = max(0, min(255, alpha * 255))
        self.rendered_text.set_alpha(alpha) if alpha != 255 else None
        surface.blit(self.rendered_text, self.text_rect)
    
    def __get_padding(self, h_padding, v_padding):
        """
        Get the padding for the text
        """
        self.h_padding = h_padding
        self.v_padding = v_padding
        
    def render_text(self, text, colour):
        """
        Render the text

        args:
            text (str): The text to render
            colour (str): The colour of the text
        """
        self.rendered_text = self.font.render(text, True, hex_to_rgb(colour))
        
    def get_alignment(self, alignment, surface):
        """
        Get the alignment of the text
        
        args:
            alignment (str): The alignment of the text
            surface (pygame.Surface): The surface to draw the text on
        """
        match alignment:
            case 'center':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, (surface.get_height() //2 - self.font.get_ascent()//2)))
            case 'left':
                self.text_rect = self.rendered_text.get_rect(topleft = (0, (surface.get_height() //2 - self.font.get_ascent()//2)))
            case 'right':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() - self.rendered_text.get_width(), (surface.get_height() //2 - self.font.get_ascent()//2)))
                self.h_padding = -self.h_padding
            case 'top':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, 0))
            case'bottom':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, surface.get_height() - self.font.get_height()))
                self.v_padding = -self.v_padding    
            case 'center_top':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, 0))
            case 'center_bottom':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, surface.get_height() - self.font.get_height()))
                self.v_padding = -self.v_padding
            case 'left_top':
                self.text_rect = self.rendered_text.get_rect(topleft = (0, (self.font.get_ascent()//2)))
            case 'right_top':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() - self.rendered_text.get_width(), (self.font.get_ascent()//2)))
                self.h_padding = -self.h_padding
            case 'left_bottom':
                self.text_rect = self.rendered_text.get_rect(topleft = (0, (surface.get_height() - self.font.get_height())))
                self.v_padding = -self.v_padding
            case 'right_bottom':
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() - self.rendered_text.get_width(), (surface.get_height() - self.font.get_height())))
                self.h_padding = -self.h_padding
                self.v_padding = -self.v_padding
            case _:
                self.text_rect = self.rendered_text.get_rect(topleft = (surface.get_width() // 2 - self.rendered_text.get_width() // 2, (surface.get_height() //2 - self.font.get_ascent()//2)))
                
    def __apply_padding(self):
        """
        Apply the padding to the text
        """
        self.text_rect.x += self.h_padding
        self.text_rect.y += self.v_padding
    
    def __draw_background(self, surface, colour, draw_background = None):
        """
        Draw the background of the text
        
        args:
            surface (pygame.Surface): The surface to draw the text on
            colour (str): The colour of the text
            draw_background (str): The colour of the background
        """
        if not draw_background:
            return
        
        self.background_surface = pygame.Surface((self.text_rect.width, self.text_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        self.background_surface.fill(draw_background)
        surface.blit(self.background_surface, self.text_rect.topleft)
        
    def get_width(self):
        """
        Get the width of the rendered text
        """
        return self.rendered_text.get_width()

    def __apply_styles(self):
        """
        Apply the styles to the font
        """
        for style in self.styles:
            if style == 'bold':
                self.font.set_bold(True)
            elif style == 'italic':
                self.font.set_italic(True)
            elif style == 'underline':
                self.font.set_underline(True)