from utils import brightness_maintain_alpha, brightness, smoothstep
import pygame
class Button:
    def __init__(self, Timing, surface, Mouse, function, container, width, height, offset = (0, 0), style = 'lighten', maintain_alpha = False):
        
        self.Timing = Timing
        self.surface = surface
        
        self.Mouse = Mouse
        
        self.function = function
        self.container = container
        self.width = width
        self.height = height
        self.offset = offset
        
        self.style = style
        self.maintain_alpha = maintain_alpha
        
        self.state = None
        self.previous_state = None
        
        self.hover_surface_transition_time = 0.25
        self.pressed_surface_transition_time = 0.1
        
        self.hover_timer = 0
        self.pressed_timer = 0
        
        self.hover_surface_alpha = 0
        self.pressed_surface_alpha = 0
    
    def get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def draw(self):
        self.surface.blit(self.button_surface, self.rect.topleft)
        self.animate_hover_surface_transition()
        self.animate_pressed_surface_transition()
        
    def animate_hover_surface_transition(self):
        if self.style is None:
            return
        
        self.hover_surface_alpha = min(255, smoothstep(self.hover_timer / self.hover_surface_transition_time) * 255) 
   
        if self.hover_timer == 0:
            return
        
        if self.hover_surface_alpha == 0:
            return
        
        self.hover_surface.set_alpha(self.hover_surface_alpha)
        self.surface.blit(self.hover_surface, self.rect.topleft)
    
    def animate_pressed_surface_transition(self):
        if self.style is None:
            return
        
        self.pressed_surface_alpha = min(255, smoothstep(self.pressed_timer / self.pressed_surface_transition_time) * 255)
        
        if self.pressed_timer == 0:
            return
        
        if self.pressed_surface_alpha == 0:
            return
        
        self.pressed_surface.set_alpha(self.pressed_surface_alpha)
        self.surface.blit(self.pressed_surface, self.rect.topleft)
            
    def check_hover(self):
        x, y = self.Mouse.position
        x -= self.offset[0]
        y -= self.offset[1]
        
        if self.rect.collidepoint((x, y)):
            if self.state == 'pressed':
                return
            self.state = 'hovered'
        else:
            self.state = None
    
    def check_events(self):
        events_to_remove = []
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button == 'scrollwheel':
                    return
                
                event_x, event_y = info['pos']
                event_x -= self.offset[0]
                event_y -= self.offset[1]
                
                mouse_x, mouse_y = self.Mouse.position
                mouse_x -= self.offset[0]
                mouse_y -= self.offset[1]
                
                if button == 'mb1' and info['down'] and self.rect.collidepoint((event_x, event_y)) and self.rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button == 'mb1' and info['up'] and self.rect.collidepoint((event_x, event_y)) and self.rect.collidepoint((mouse_x, mouse_y)) and self.state == 'pressed':
                    self.state = None
                    events_to_remove.append(event)
                    self.click()
        
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def click(self):
        self.function()
        
    def update(self):
        self.check_hover()
        self.check_events()
        
        if self.state == 'hovered':
            self.handle_hover_start_events()
        
        elif self.state is None and self.previous_state == 'hovered':
            self.handle_hover_end_events()
        
        elif self.state == 'pressed':
            self.handle_pressed_start_events()
        
        elif self.previous_state == 'pressed' and self.state != 'pressed':
            self.handle_pressed_end_events()
    
    def handle_hover_start_events(self):
        self.draw()
        self.hover_timer += self.Timing.frame_delta_time
        
        if self.hover_timer >= self.hover_surface_transition_time:
            self.hover_timer = self.hover_surface_transition_time
            
        self.previous_state = 'hovered'
    
    def handle_hover_end_events(self):
        self.draw()
        self.hover_timer -= self.Timing.frame_delta_time
        
        if self.hover_timer <= 0:
            self.hover_timer = 0
            self.hover_surface_alpha = 0
            self.previous_state = None
    
    def handle_pressed_start_events(self):
        self.draw()
        self.pressed_timer += self.Timing.frame_delta_time
        
        if self.pressed_timer >= self.pressed_surface_transition_time:
            self.pressed_timer = self.pressed_surface_transition_time
            
        self.previous_state = 'pressed'
    
    def handle_pressed_end_events(self):
        self.draw()
        self.pressed_timer -= self.Timing.frame_delta_time
        self.hover_timer -= self.Timing.frame_delta_time
        
        if self.pressed_timer <= 0:
            self.pressed_timer = 0
            self.pressed_surface_alpha = 0
            self.previous_state = None
            self.hover_timer = 0
            self.hover_surface_alpha = 0
                
    def get_overlays(self):
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        self.__get_darken_overlay()
        
    def __get_lighten_overlay(self):
        if self.style != 'lighten':
            return
        
        if self.maintain_alpha:
            self.hover_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.hover_surface, 1.2)

            self.pressed_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.pressed_surface, 1.5)
        else:
            self.hover_surface = self.button_surface.copy()
            brightness(self.hover_surface, 1.2)

            self.pressed_surface = self.button_surface.copy()
            brightness(self.pressed_surface, 1.5)
        
    def __get_darken_overlay(self):
        if self.style != 'darken':
            return
        
        if self.maintain_alpha:
            self.hover_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.hover_surface, 0.8)

            self.pressed_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.pressed_surface, 0.5)
        else:
            self.hover_surface = self.button_surface.copy()
            brightness(self.hover_surface, 0.8)

            self.pressed_surface = self.button_surface.copy()
            brightness(self.pressed_surface, 0.5)
            
    def reset_state(self):
        self.hover_timer = 0
        self.pressed_timer = 0
        self.hover_surface_alpha = 0
        self.pressed_surface_alpha = 0
        self.state = None
