import pygame
from utils import load_image, align_bottom_left

class Logo():
    def __init__(self, container, definition):
        self.container = container
        self.definition = definition
        self.width = self.container.width // 8.5
        
        self.__init_image()
        self.__align_image()
        self.image.set_alpha(self.definition['opacity'])
    
    def __init_image(self):
        self.image = load_image(self.definition['image'])  
        
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = int(self.width / aspect_ratio)

        self.image = pygame.transform.smoothscale(self.image, (self.width, new_height))

    def __align_image(self):
        if self.definition['alignment'] == 'bottom_left':
            self.rect = align_bottom_left(self.container, self.image.get_width(), self.image.get_height(), self.definition['padding'][0], self.definition['padding'][1])
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)