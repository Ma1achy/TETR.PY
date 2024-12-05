import pygame
from utils import draw_solid_colour, draw_border
from render.GUI.font import Font
from render.GUI.buttons.button import Button

class BackButton(Button):
    def __init__(self, function, Mouse, Timing, surface, container, definition):
        super().__init__(surface, Mouse, function, container, 300, 60, offset = (container.left, container.top), style = 'lighten', maintain_alpha = False)
    
        self.Timing = Timing
    
        self.definition = definition

        self.x_start = 150
        self.font = Font('hun2', 33)
        
        self.__get_rect_and_surface()
        self.render_button()
        self.get_overlays()
        
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.left - self.x_start, 15, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect())
        self.render_text()
    
    def render_text(self):
        self.font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'right', 20, 0)