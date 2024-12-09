import pygame
from utils import load_image, draw_solid_colour, draw_border, align_centre, apply_gaussian_blur_with_alpha
from render.GUI.buttons.button import Button
class FooterButton(Button):
    def __init__(self, Timing, function, Mouse, surface, container, definition):
        super().__init__(Timing, surface, Mouse, function, container, 70, 100, offset = (container.left, container.top), style = 'lighten', maintain_alpha = False, slider = 'up')
        
        self.definition = definition

        self.x_offset = -90
        self.y_offset = -5
        
        
        self.default_y_position =  70
        self.hovered_y_position = 60
        self.pressed_y_position = 50
        
        self.x_position = self.container.right + self.x_offset
        self.default_x_position = self.x_position, self.container.bottom
        self.y_position = self.default_y_position
        
        self.shadow_radius = 5
     
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.x_position, self.container.bottom - self.y_position, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect =  pygame.Rect(self.container.right + self.x_offset - self.shadow_radius * 2, self.container.bottom - self.y_position - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render(self):
        self.render_shadow()
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
        self.x_position = self.container.right + self.x_offset
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
    
    def render_shadow(self):
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(+self.shadow_radius * 2, +self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)

    