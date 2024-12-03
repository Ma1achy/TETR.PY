import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font

class Footer:
    def __init__(self, container, height, text, background, border, image = None):
        self.container = container
        self.text = text
        self.background = background
        self.border = border
              
        self.width = self.container.width
        self.height = height
        
        self.rect = align_bottom_edge(self.container, self.width, self.height, 0, 0)

        self.footer_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
    
        self.font = Font('hun2', 30)
        self.render_footer()
        
        if image:
            self.image = load_image(image["path"])
            self.render_image()

    def render_footer(self):
        if self.background['style'] == 'linear_gradient':
            draw_linear_gradient(self.footer_surface, self.background['colours'][0], self.background['colours'][1], self.footer_surface.get_rect())
        elif self.background['style'] == 'solid':
            draw_solid_colour(self.footer_surface, self.background['colour'], self.footer_surface.get_rect())
            
        draw_border(self.footer_surface, self.border, self.footer_surface.get_rect())
        self.font.draw(self.footer_surface, self.text['display_text'], self.text['colour'], 'left', 20, 0)
        
    def render_image(self):
        
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = self.height - 25
        new_width = int(new_height * aspect_ratio)
        
        image = pygame.transform.smoothscale(self.image, (new_width, new_height))
        image_rect = align_centre(self.footer_surface.get_rect(), image.get_width(), image.get_height(), 0, 0)

        self.footer_surface.blit(image, (image_rect.left + self.footer_surface.get_rect().width//2 - new_width - 40, image_rect.top))
        
    def draw(self, surface):
        surface.blit(self.footer_surface, self.rect.topleft)
        
    def handle_window_resize(self):
        self.width = self.container.width
        self.rect = align_bottom_edge(self.container, self.width, self.height, 0, 0)
        
        self.footer_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
        self.render_footer()
        
        if hasattr(self, 'image'):
            self.render_image()