import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font

class Header:
    def __init__(self, container, height, text, background, border):
        self.container = container
        self.height = height
        self.text = text
        self.background = background
        self.border = border

        self.font = Font('hun2', 40)
        
        self.__get_rect_and_surface()
        self.render()
    
    def __get_rect_and_surface(self):
        self.width = self.container.width
        
        self.rect = align_top_edge(self.container, self.width, self.height, 0, 0)
        self.header_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
         
    def render(self):
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
    
    def draw(self, surface):
        surface.blit(self.header_surface, self.rect.topleft)
    
    def handle_window_resize(self):
        self.__get_rect_and_surface()
        self.render()