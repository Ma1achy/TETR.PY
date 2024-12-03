import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font

class BackButton():
    def __init__(self, surface, container, definition):
        self.surface = surface
        self.container = container
        self.definition = definition
        self.width = 300
        self.height = 60
        
        self.x_start = 150
        self.font = Font('hun2', 33)
        
        self.__get_rect_and_surface()
        self.render_button()
        self.get_hovered_image()
        self.get_pressed_image()
        
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.rect)
        draw_border(self.button_surface, self.definition['border'], self.rect)
        self.render_text()
    
    def get_hovered_image(self):
        self.hovered_surface = self.button_surface.copy()
        brightness(self.hovered_surface, 1.2)
    
    def get_pressed_image(self):
        self.pressed_surface = self.button_surface.copy()
        brightness(self.pressed_surface, 1.5)
    
    def render_text(self):
        self.font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'right', 20, 0)
        
    def draw(self):
        self.surface.blit(self.button_surface, (self.rect.left - self.x_start , self.rect.top + 15))
        # self.surface.blit(self.hovered_surface, (self.rect.left - self.x_start, self.rect.top + 15))
        # self.surface.blit(self.pressed_surface, (self.rect.left - self.x_start, self.rect.top + 15))
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False