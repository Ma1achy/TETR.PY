import pygame
from app.utils import load_image, align_bottom_left

class Logo():
    def __init__(self, container, definition, RENDER_SCALE):
        """
        A logo element that can be displayed on the menu
        
        args:
            container (pygame.Rect): the container the logo is in
            definition (dict): the definition of the logo
        """
        self.RENDER_SCALE = RENDER_SCALE
        self.container = container
        self.definition = definition
        self.width = self.container.width // 8.5
        
        self.__init_image()
        self.__align_image()
        self.image.set_alpha(self.definition['opacity'])
    
    def __init_image(self):
        """
        Initialise the image
        """
        self.image = load_image(self.definition['image'])  
        
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = int(self.width / aspect_ratio)

        self.image = pygame.transform.smoothscale(self.image, (self.width, new_height))

    def __align_image(self):
        """
        Align the image in the container
        """
        if self.definition['alignment'] == 'bottom_left':
            self.rect = align_bottom_left(self.container, self.image.get_width(), self.image.get_height(), int(self.definition['padding'][0] * self.RENDER_SCALE), int(self.definition['padding'][1] * self.RENDER_SCALE))
    
    def draw(self, surface):
        """
        Draw the logo
        """
        surface.blit(self.image, self.rect.topleft)