from render.GUI.buttons.button import Button
import pygame

class InvisibleButton(Button):
    def __init__(self, Timing, surface, Mouse, function, container, parent):
        super().__init__(Timing, surface, Mouse, function, container, width = container.width, height = container.height, style = None, maintain_alpha = False, parent = parent)
        
        self.get_rect_and_surface()
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
    
    def get_local_position(self):
        return self.container.topleft
        