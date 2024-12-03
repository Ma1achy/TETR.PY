import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font
from render.GUI.buttons.button_bar import ButtonBar
from render.GUI.buttons.back_button import BackButton

class MainBody():
    def __init__(self, width, height, topleft, definition):
        
        self.definition = definition
        
        self.width = width
        self.height = height
        self.topleft = topleft
              
        self.body_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_body_container = self.body_surface.get_rect()
        self.render_body()
    
    def render_body(self):
        if 'logo' in self.definition:
            self.logo = Logo(self.main_body_container, self.definition['logo'])
            self.logo.draw(self.body_surface)
        
        if 'menu' in self.definition:
            for idx, element in enumerate(self.definition['menu']['elements']):
                if element['type'] == 'bar_button':
                    button = ButtonBar(self.body_surface, self.main_body_container, element, idx, height = 120)
                    button.draw()
        
        if 'back_button' in self.definition:
            self.back_button = BackButton(self.body_surface, self.main_body_container, self.definition['back_button'])
            self.back_button.draw()
        
    def draw(self, surface):
        surface.blit(self.body_surface, self.topleft)
    
    def handle_window_resize(self):
        self.body_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_body_container = self.body_surface.get_rect()
        
        if 'logo' in self.definition:
            self.logo = Logo(self.main_body_container, self.definition['logo'])
            self.logo.draw(self.body_surface)
        
        if 'menu' in self.definition:
            for idx, element in enumerate(self.definition['menu']['elements']):
                if element['type'] == 'bar_button':
                    button = ButtonBar(self.body_surface, self.main_body_container, element, idx, height = 120)
                    button.draw()
                    button.get_hovered_image()
                    button.get_pressed_image()
        
        if 'back_button' in self.definition:
            self.back_button = BackButton(self.body_surface, self.main_body_container, self.definition['back_button'])
            self.back_button.draw()
            self.back_button.get_hovered_image()
            self.back_button.get_pressed_image()
        
        self.render_body()

class Logo():
    def __init__(self, container, definition):
        
        self.container = container
        self.definition = definition
        self.image = load_image(self.definition['image'])  
        self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width() * self.definition['scale']), int(self.image.get_height() * self.definition['scale'])))
        
        if self.definition['alignment'] == 'bottom_left':
            self.rect = align_bottom_left(self.container, self.image.get_width(), self.image.get_height(), self.definition['padding'][0], self.definition['padding'][1])
            
        self.image.set_alpha(self.definition['opacity'])
        
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)