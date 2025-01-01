from render.GUI.buttons.button import Button
import pygame

class InvisibleButton(Button):
    def __init__(self, Timing, surface, Mouse, function, container, parent, RENDER_SCALE = 1):
        super().__init__(Timing, surface, Mouse, function, container, width = container.width, height = container.height, style = None, maintain_alpha = False, parent = parent, RENDER_SCALE = RENDER_SCALE)
        """
        An invisible button that can be used for any purpose
        
        args:
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the button on
            Mouse (Mouse): the Mouse object
            function (callable): the function to call when the button is pressed
            container (pygame.Rect): the container the button is in
            parent (Object): the parent UI element
        """
        self.get_rect_and_surface()
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
    
    def get_local_position(self):
        """
        Get the position of the button relative to the container it is in for collision detection
        """
        return self.container.topleft
        