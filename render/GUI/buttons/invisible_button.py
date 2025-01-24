from render.GUI.buttons.button import Button
import pygame

class InvisibleButton(Button):
    def __init__(self, width, height, rect, function, Mouse, Timing, surface, container, definition, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, function, container, width, height, style = None, maintain_alpha = False, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = None)
 
        self.RENDER_SCALE = RENDER_SCALE
        self.x_position = rect.x
        self.y_position = container.y
        
        self.width = width
        self.height = height
        self.rect = rect
                  
        self.definition = definition
 
        self.__get_rect_and_surface()
        self.render()
        self.init_tooltip(self.definition)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
     
    def get_local_position(self):
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        if self.width < 1:
            self.width = 1
        
        if self.height < 1:
            self.height = 1
            
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        return
        self.render_button()
    
    def render_button(self):
        pygame.draw.rect(self.button_surface, (255, 0, 0), self.button_surface.get_rect(), 1)

    def draw(self):
        super().draw()