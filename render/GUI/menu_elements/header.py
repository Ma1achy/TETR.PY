import pygame
from utils import draw_linear_gradient, draw_solid_colour, draw_border, align_top_edge, apply_gaussian_blur_with_alpha
from render.GUI.font import Font

class Header:
    def __init__(self, container, height, text, background, border):
        self.container = container
        self.height = height
        self.text = text
        self.background = background
        self.border = border

        self.font = Font('hun2', 40)
        
        self.shadow_radius = 5
        
        self.__get_rect_and_surface()
        self.render()
    
    def __get_rect_and_surface(self):
        self.width = self.container.width
        
        self.rect = align_top_edge(self.container, self.width, self.height, 0, 0)
        self.header_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
        
        self.shadow_rect = pygame.Rect(self.rect.left - self.shadow_radius * 2, self.rect.top - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
         
    def render(self):
        self.__render_shadow()
        self.__render_background()
        self.__render_border()
        self.__render_text()
        
    def __render_background(self):
        if self.background['style'] == 'linear_gradient':
            draw_linear_gradient(self.header_surface, self.background['colours'][0], self.background['colours'][1], self.header_surface.get_rect())
        elif self.background['style'] == 'solid':
            draw_solid_colour(self.header_surface, self.background['colour'], self.header_surface.get_rect())
    
    def __render_border(self):
        draw_border(self.header_surface, self.border, self.rect)
    
    def __render_text(self):
        self.font.draw(self.header_surface, self.text['display_text'], self.text['colour'], 'left', 20, 0)
    
    def __render_shadow(self):
        
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.rect.width, self.rect.height))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
    
    def draw(self, surface):
        surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        surface.blit(self.header_surface, self.rect.topleft)
    
    def handle_window_resize(self):
        self.__get_rect_and_surface()
        self.render()