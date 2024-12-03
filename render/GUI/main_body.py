import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font
from render.GUI.buttons.button_bar import ButtonBar
from render.GUI.buttons.back_button import BackButton

class MainBody():
    def __init__(self, rect, definition):
        
        self.definition = definition
        self.rect = rect
        self.menu_elements = []

        self.body_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_body_container = self.body_surface.get_rect()
        self.__init_elements()
        self.render()
    
    def __init_elements(self):
        self.__init_menu_elements()
        self.__init_back_button()
        self.__init_logo()
    
    def __init_menu_elements(self):
        if 'menu' not in self.definition:
            return
        
        for idx, element in enumerate(self.definition['menu']['elements']):
            if element['type'] == 'bar_button':
                button = ButtonBar(self.body_surface, self.main_body_container, element, idx, height = 120)
                self.menu_elements.append(button)
    
    def __init_back_button(self):
        if 'back_button' not in self.definition:
            return
        
        self.back_button = BackButton(self.body_surface, self.main_body_container, self.definition['back_button'])
    
    def __init_logo(self):
        if 'logo' not in self.definition:
            return
        
        self.logo = Logo(self.main_body_container, self.definition['logo'])
        
    def render(self):
        self.render_logo()
        self.render_menu()
        self.render_back_button()
        
    def render_logo(self):
        if 'logo' not in self.definition:
            return
    
        self.logo.draw(self.body_surface)
    
    def render_menu(self):
        if 'menu' not in self.definition:
            return
        
        for element in self.menu_elements:
            element.draw()
    
    def render_back_button(self):
        if 'back_button' not in self.definition:
            return
        
        self.back_button.draw()
    
    def draw(self, surface):
        surface.blit(self.body_surface, self.rect.topleft)
    
    def handle_window_resize(self):
        self.body_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_body_container = self.body_surface.get_rect()
        
        self.__init_elements()
        self.render()

class Logo():
    def __init__(self, container, definition):
        
        self.container = container
        self.definition = definition
        self.__init_image()
        self.__align_image()
        self.image.set_alpha(self.definition['opacity'])
    
    def __init_image(self):
        self.image = load_image(self.definition['image'])  
        self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width() * self.definition['scale']), int(self.image.get_height() * self.definition['scale'])))
    
    def __align_image(self):
        if self.definition['alignment'] == 'bottom_left':
            self.rect = align_bottom_left(self.container, self.image.get_width(), self.image.get_height(), self.definition['padding'][0], self.definition['padding'][1])
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)