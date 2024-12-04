import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font

class FooterButton():
    def __init__(self, Mouse, surface, container, definition):
        
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        self.definition = definition
        self.width = 70
        self.height = 70
        self.x_start = 70
        self.y_offset = 35
        
        self.__get_rect_and_surface()
        self.render_button()
        self.render_image()
        self.get_hovered_image()
        self.get_pressed_image()
    
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.rect)
        draw_border(self.button_surface, self.definition['border'], self.rect)
    
    def render_image(self):
        x_padding = self.definition['image']['padding'][0]
        y_padding = self.definition['image']['padding'][1]
        button_width = self.rect.width - x_padding

        image = load_image(self.definition['image']['path'])     
        
        aspect_ratio = image.get_width() / image.get_height()
        new_height = int(button_width * aspect_ratio)

        image = pygame.transform.smoothscale(image, (button_width, new_height))
        image_rect = align_centre(self.rect, image.get_width(), image.get_height(), 0, -self.height//2 + y_padding - 2)
        
        self.button_surface.blit(image, image_rect.topleft)
    
    def get_hovered_image(self):
        self.hovered_surface = self.button_surface.copy()
        brightness(self.hovered_surface, 1.2)
    
    def get_pressed_image(self):
        self.pressed_surface = self.button_surface.copy()
        brightness(self.pressed_surface, 1.5)
        
    def draw(self):
        self.surface.blit(self.button_surface, (self.container.right - 20 - self.width, self.container.bottom - self.x_start))
        # self.surface.blit(self.hovered_surface, (self.container.right - 20 - self.width, self.container.bottom - self.height + self.y_offset + self.x_start))
        # self.surface.blit(self.pressed_surface, (self.container.right - 20 - self.width, self.container.bottom - self.height + self.y_offset + self.x_start))
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False
    
    def handle_window_resize(self):
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button()
        self.render_image()
        self.get_hovered_image()
        self.get_pressed_image()