import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha
from render.GUI.font import Font
from render.GUI.buttons.button import Button

class BackButton(Button):
    def __init__(self, function, Mouse, Timing, surface, container, definition, parent):
        super().__init__(Timing, surface, Mouse, function, container, 300, 60, style = 'lighten', maintain_alpha = False, slider = 'right', parent = parent)
        
        self.definition = definition

        self.default_x_position = 150
        self.hovered_x_position = 170
        self.pressed_x_position = 185
        
        self.x_position = self.default_x_position
        self.y_position = 15
        
        self.font = Font('hun2', 33)
        self.shadow_radius = 5
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
          
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.left - self.x_position, self.y_position, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.container.left - self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        self.render_shadow()
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect())
        self.render_text()
    
    def render_text(self):
        self.font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'right', 20, 0)
    
    def render_shadow(self):
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height))
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)

        