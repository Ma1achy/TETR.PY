import pygame
from utils import draw_linear_gradient, draw_solid_colour, draw_border, align_top_edge, apply_gaussian_blur_with_alpha, load_image, align_center_left
from render.GUI.font import Font
import math

class Header:
    def __init__(self, container, height, definition, image = None):
        """
        A header that can be used at the top of a menu
        
        args:
            container (pygame.Rect): the container the header is in
            height (int): the height of the header
            definition (dict): the definition of the header
            image (dict): the image to display on the header
        """
        self.container = container
        self.height = height
        self.definition = definition
        
        self.image = image
        
        self.border_image = None  
        self.get_header_style()
        self.border_image_repeats = self.calculate_repeat()
        
        self.text = self.get_text()
        self.background = self.get_background()
        self.border = self.get_border()

        self.font = Font('hun2', 40)
        
        self.shadow_radius = 5
        
        self.__load_image()
        self.__get_rect_and_surface()
        self.render()
    
    def __load_image(self):
        """
        Load the image for the header
        """
        if self.image:
            self.image = load_image(self.image["path"])
        else:
            self.image = None
            
    def get_header_style(self):
        """
        Get the style of the header
        """
        if 'style' not in self.definition:
            return
        
        if self.definition['style'] == 'image':
            self.border_image = load_image('resources/GUI/header.png')
            
    def calculate_repeat(self):
        """
        Calculate the number of times the border image should be repeated
        """
        if self.border_image is None:
            return 0
        
        return math.ceil(self.container.width / self.border_image.get_width())
    
    def get_text(self):
        """
        Get the text of the header
        """
        if 'text' in self.definition:
            return self.definition['text']
    
    def get_background(self):
        """
        Get the background of the header
        """
        if 'background' in self.definition:
            return self.definition['background']

    def get_border(self):
        """
        Get the border of the header
        """
        if 'border' in self.definition:
            return self.definition['border']
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the header
        """
        self.width = self.container.width
        
        self.rect = align_top_edge(self.container, self.width, self.height, 0, 0)
        self.header_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
        
        self.shadow_rect = pygame.Rect(self.rect.left - self.shadow_radius * 2, self.rect.top - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
         
    def render(self):
        """
        Render the header and its shadow
        """
        self.__render_shadow()
        self.__render_background()
        self.__render_border()
        self.__render_text()
        self.__render_border_image()
        self.__render_image()
        
    def __render_background(self):
        """
        Render the background of the header
        """
        if 'background' not in self.definition:
            return
        
        if self.background['style'] == 'linear_gradient':
            draw_linear_gradient(self.header_surface, self.background['colours'][0], self.background['colours'][1], self.header_surface.get_rect())
        elif self.background['style'] == 'solid':
            draw_solid_colour(self.header_surface, self.background['colour'], self.header_surface.get_rect())
    
    def __render_border(self):
        """
        Render the border of the header
        """
        if 'border' not in self.definition:
            return
        
        draw_border(self.header_surface, self.border, self.rect)
    
    def __render_text(self):
        """
        Render the text of the header
        """
        if 'text' not in self.definition:
            return
        
        self.font.draw(self.header_surface, self.text['display_text'], self.text['colour'], 'left', 20, 0)
    
    def __render_shadow(self):
        """
        Render the shadow of the header
        """
        if 'no_shadow' in self.definition:
            return
        
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.rect.width, self.rect.height))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
    
    def __render_border_image(self):
        """
        Render the border image of the header
        """
        if self.border_image is None:
            return
        
        for i in range(self.border_image_repeats):
            self.header_surface.blit(self.border_image, (i * self.border_image.get_width(), self.rect.bottom - self.border_image.get_height()))
    
    def __render_image(self):
        """
        Render the image on the header
        """
        if self.image is None:
            return
        
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = self.height - 25
        new_width = int(new_height * aspect_ratio)
        
        image = pygame.transform.smoothscale(self.image, (new_width, new_height))
        image_rect = align_center_left(self.header_surface.get_rect(), image.get_width(), image.get_height(), 20, 5)

        self.header_surface.blit(image, (image_rect.left, image_rect.top))
             
    def draw(self, surface):
        """
        Draw the header
        """
        if 'no_shadow' not in self.definition:
            surface.blit(self.shadow_surface, self.shadow_rect.topleft)
            
        surface.blit(self.header_surface, self.rect.topleft)
    
    def handle_window_resize(self):
        """
        Handle the window being resized
        """
        self.__get_rect_and_surface()
        self.border_image_repeats = self.calculate_repeat()
        self.render()