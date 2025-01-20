from render.GUI.buttons.button import Button
import pygame
from app.input.mouse.mouse import MouseEvents

class SliderBarButton(Button):
    def __init__(self, width, height, rect, function, Mouse, Timing, surface, container, definition, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, function, container, width, height, style = None, maintain_alpha = False, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips)
       
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
    
    def check_events(self):
        """
        Check for input events.
        """
        events_to_remove = []
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button is MouseEvents.SCROLLWHEEL:
                    return
                
                event_x, event_y = info['pos']
                mouse_x, mouse_y = self.Mouse.position

                if button is MouseEvents.MOUSEBUTTON1 and info['down'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button is MouseEvents.MOUSEBUTTON1 and info['up'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)) and self.state == 'pressed':
                    events_to_remove.append(event)
                    self.click(mouse_x)
        
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def click(self, mouse_x):
        """
        Execute the button's function.
        """
        if self.ToolTips:
            self.ToolTips.tooltip_timer = 0
            
        if self.function is None:
            return
         
        self.function(mouse_x)