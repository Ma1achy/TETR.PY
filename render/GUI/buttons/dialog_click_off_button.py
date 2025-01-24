from render.GUI.buttons.button import Button
import pygame

class DialogClickOffButton(Button):
    def __init__(self, Timing, surface, Mouse, Sound, function, container, parent, RENDER_SCALE, ToolTips = None, definition = None):
        super().__init__(Timing, surface, Mouse, function, container, width = container.width, height = container.height, style = None, maintain_alpha = False, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
        """
        A button that is used to close a dialog box, when the user clicks off the dialog box
        
        args:
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the button on
            Mouse (Mouse): the Mouse object
            function (callable): the function to call when the button is pressed
            container (pygame.Rect): the container the button is in
            parent (Object): the parent UI element
        """
        self.definition = definition       
        self.init_tooltip(self.definition)
        
        self.get_rect_and_surface()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))

        self.hover_sound = None
         
    def get_local_position(self):
        """
        Get the position of the button relative to the container it is in for collision detection
        """
        return self.container.topleft
    
    # def draw(self):
    #     pygame.draw.rect(self.surface, (255, 0, 0), self.collision_rect, 1)