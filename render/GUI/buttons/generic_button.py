from render.GUI.buttons.button import Button
from render.GUI.font import Font
import pygame
from utils import draw_border, draw_solid_colour, align_element

class GenericButton(Button):
    def __init__(self, Timing, Mouse, surface, container, definition, function, parent):
        super().__init__(Timing, surface, Mouse, function, container, definition['size']['width'], definition['size']['height'], style = 'lighten', maintain_alpha = False, slider = None, parent = parent)
        
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        
        self.definition = definition
        
        self.width = definition['size']['width']
        self.height = definition['size']['height']
        
        self.x_position = definition['position']['x']
        self.y_position = definition['position']['y']
        
        self.font = Font('hun2', 23)
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()

        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
    
    def __get_rect_and_surface(self):

        if 'alignment' in self.definition:
            self.rect = align_element(self.container, self.width, self.height, self.x_position, self.y_position, self.definition['alignment'])
        else:
            self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
            
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render(self):
        self.render_button()
        self.render_text()
    
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect())
    
    def render_text(self):
        self.font.draw(self.button_surface, self.definition['text']['display_text'], self.definition['text']['colour'], 'center', 0, 0)
    
    def update(self, in_dialog):
        self.disable_layer_below()
        super().update(in_dialog)
        
    def disable_layer_below(self):
  
        if self.state is not None:
            self.parent.ignore_events = True
            self.parent.reset_state()
        else:
            self.parent.ignore_events = False
           
        
    

     
        
        