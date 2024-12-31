import pygame
from utils import load_image, draw_linear_gradient, draw_solid_colour, draw_border, align_bottom_edge, align_centre, apply_gaussian_blur_with_alpha
from render.GUI.font import Font
import math

class Footer:
    def __init__(self, container, height, definition, image = None):
        """
        A footer that can be used at the bottom of a menu
        
        args:
            container (pygame.Rect): the container the footer is in
            height (int): the height of the footer
            definition (dict): the definition of the footer
            image (dict): the image to display on the footer
        """
        self.container = container
        self.height = height
        self.definition = definition

        self.border_image = None  
        self.get_footer_style()
        self.border_image_repeats = self.calculate_repeat()

        self.text = self.get_text()
        self.background = self.get_background()
        self.border = self.get_border()

        self.font = Font('hun2', 30)
        self.image = image

        self.shadow_radius = 5

        self.__get_rect_and_surface()
        self.__load_image()
        self.render()
        
    def get_footer_style(self):
        """
        Get the style of the footer
        """
        if 'style' not in self.definition:
            return

        if self.definition['style'] == 'image':
            self.border_image = load_image('resources/GUI/footer.png')
            
    def calculate_repeat(self):
        """
        Calculate the number of times the border image should be repeated
        """
        if self.border_image is None:
            return 0
        
        return math.ceil(self.container.width / self.border_image.get_width())
        
    def get_text(self):
        """
        Get the text of the footer
        """
        if 'text' in self.definition:
            return self.definition['text']
    
    def get_background(self):
        """
        Get the background of the footer
        """
        if 'background' in self.definition:
            return self.definition['background']
    
    def get_border(self):
        """
        Get the border of the footer
        """
        if 'border' in self.definition:
            return self.definition['border']
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the footer
        """
        self.width = self.container.width
        
        self.rect = align_bottom_edge(self.container, self.width, self.height, 0, 0)
        self.footer_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
        
        self.shadow_rect = pygame.Rect(self.rect.left - self.shadow_radius * 2, self.rect.top - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        """
        Render the footer
        """
        self.__render_shadow()
        self.__render_background()
        self.__render_border()
        self.__render_text()
        self.__render_image()
        self.__render_border_image()
    
    def __load_image(self):
        """
        Load the image for the footer
        """
        if self.image:
            self.image = load_image(self.image["path"])
        else:
            self.image = None
    
    def __render_background(self):
        """
        Render the background of the footer
        """
        if 'background' not in self.definition:
            return
            
        if self.background['style'] == 'linear_gradient':
            draw_linear_gradient(self.footer_surface, self.background['colours'][0], self.background['colours'][1], self.footer_surface.get_rect())
        elif self.background['style'] == 'solid':
            draw_solid_colour(self.footer_surface, self.background['colour'], self.footer_surface.get_rect())
            
    def __render_border(self):
        """
        Render the border of the footer
        """
        if 'border' not in self.definition:
            return
        
        draw_border(self.footer_surface, self.border, self.footer_surface.get_rect())
    
    def __render_text(self):
        """
        Render the text on the footer
        """
        if 'text' not in self.definition:
            return
        
        self.font.draw(self.footer_surface, self.text['display_text'], self.text['colour'], 'left', 20, 0)
         
    def __render_image(self):
        """
        Render the image on the footer
        """
        if self.image is None:
            return
        
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = self.height - 25
        new_width = int(new_height * aspect_ratio)
        
        image = pygame.transform.smoothscale(self.image, (new_width, new_height))
        image_rect = align_centre(self.footer_surface.get_rect(), image.get_width(), image.get_height(), 0, 0)

        self.footer_surface.blit(image, (image_rect.left + self.footer_surface.get_rect().width//2 - new_width - 45, image_rect.top))
    
    def __render_shadow(self):
        """
        Render the shadow of the footer
        """
        if 'no_shadow' in self.definition:
            return
        
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
    
    def __render_border_image(self):
        """
        Render the border image of the footer
        """
        if self.border_image is None:
            return
        
        for i in range(self.border_image_repeats):
            self.footer_surface.blit(self.border_image, (i * self.border_image.get_width(), 0))
              
    def draw(self, surface):
        """
        Draw the footer
        """
        if 'no_shadow' not in self.definition: 
            surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        surface.blit(self.footer_surface, self.rect.topleft)
        
    def handle_window_resize(self):
        """
        Handle the window being resized
        """
        self.__get_rect_and_surface()
        self.border_image_repeats = self.calculate_repeat()
        self.render()