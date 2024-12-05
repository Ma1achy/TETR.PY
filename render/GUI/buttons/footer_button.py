import pygame
from utils import load_image, draw_solid_colour, draw_border, align_centre
from render.GUI.font import Font
from render.GUI.buttons.button import Button
class FooterButton(Button):
    def __init__(self, function, Mouse, surface, container, definition):
        super().__init__(surface, Mouse, function, container, 70, 70, offset = (container.left, container.top), style = 'lighten', maintain_alpha = False)
        
        self.definition = definition

        self.x_start = 70
        self.y_offset = 35
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.right - 90, self.container.bottom - self.x_start, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render(self):
        self.render_button()
        self.render_image()
        
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect())
        
    def render_image(self):
        x_padding = self.definition['image']['padding'][0]
        y_padding = self.definition['image']['padding'][1]
        button_width = self.rect.width - x_padding

        image = load_image(self.definition['image']['path'])     
        
        aspect_ratio = image.get_width() / image.get_height()
        new_height = int(button_width * aspect_ratio)

        image = pygame.transform.smoothscale(image, (button_width, new_height))
        image_rect = align_centre(self.button_surface.get_rect(), image.get_width(), image.get_height(), 0, -self.height//2 + y_padding - 2)
        
        self.button_surface.blit(image, image_rect.topleft)
    
    def handle_window_resize(self):
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
    