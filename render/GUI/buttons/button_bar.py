import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font

class ButtonBar():
    def __init__(self, surface, container, definition, list_index, height):
        self.surface = surface
        self.container = container
        self.definition = definition
        self.width = self.container.width
        self.height = height 
        
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_font = Font('hun2', 50)
        self.sub_font = Font('hun2', 23)
                
        self.y_offset = list_index * (self.height + 20) + 35
        self.start = self.container.width // 5.5
        
        self.render_button()
        self.get_hovered_image()
        self.get_pressed_image()
        
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.rect)
        draw_border(self.button_surface, self.definition['border'], self.rect)
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
        image_rect = align_left_edge(self.rect, image.get_width(), image.get_height(), x_padding, y_padding)
        
        self.button_surface.blit(image, image_rect.topleft)
    
    def render_text(self):
        self.main_font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'left', 275, - self.main_font.font.get_ascent()//2 + 3)
        self.sub_font.draw(self.button_surface, self.definition['sub_text']['display_text'], self.definition['sub_text']['colour'], 'left', 275, self.main_font.font.get_ascent()//2 + 10)
    
    def get_hovered_image(self):
        self.hovered_surface = self.button_surface.copy()
        brightness(self.hovered_surface, 1.2)
    
    def get_pressed_image(self):
        self.pressed_surface = self.button_surface.copy()
        brightness(self.pressed_surface, 1.5)
        
    def draw(self):
        self.surface.blit(self.button_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
        # self.surface.blit(self.hovered_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
        # self.surface.blit(self.pressed_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False
    
    def update(self, surface):
        self.hover = self.check_hover(pygame.mouse.get_pos())
        self.draw(surface)