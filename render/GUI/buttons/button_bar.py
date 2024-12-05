import pygame
from utils import load_image, draw_solid_colour, draw_border, align_left_edge
from render.GUI.font import Font
from render.GUI.buttons.button import Button

class ButtonBar(Button):
    def __init__(self, function:callable, Mouse, Timing, surface, container, definition, list_index, height):
        super().__init__(surface, Mouse, function, container, container.width, height, offset = (container.left, container.top), style = 'lighten', maintain_alpha = False)
        
        self.Timing = Timing
        
        self.surface = surface
        self.definition = definition
 
        self.main_font = Font('din_bold', 60)
        self.sub_font = Font('hun2', 23)
                
        self.y_offset = list_index * (self.height + 20) + 35
        self.start = self.container.width // 5.5
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()

    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.start, self.y_offset, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect())
        self.render_image()
        self.render_text()
              
    def render_image(self):
           
        x_padding = self.definition['image']['padding'][0]
        y_padding = self.definition['image']['padding'][1]
        button_height = self.rect.height - y_padding
        
        image = load_image(self.definition['image']['path'])     
        
        aspect_ratio = image.get_width() / image.get_height()
        new_width = int(button_height * aspect_ratio)

        image = pygame.transform.smoothscale(image, (new_width, button_height))
        image_rect = align_left_edge(self.button_surface.get_rect(), image.get_width(), image.get_height(), x_padding, y_padding)
        
        self.button_surface.blit(image, image_rect.topleft)
    
    def render_text(self):
        self.main_font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'left', 275, - self.main_font.font.get_ascent()//2 + 7)
        self.sub_font.draw(self.button_surface, self.definition['sub_text']['display_text'], self.definition['sub_text']['colour'], 'left', 275, self.main_font.font.get_ascent()//2 + 2)