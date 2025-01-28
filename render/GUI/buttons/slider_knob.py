from render.GUI.buttons.button import Button
import pygame
from utils import draw_border, draw_solid_colour, apply_gaussian_blur_with_alpha
from app.input.mouse.mouse import MouseEvents
from app.core.sound.sfx import SFX
class SliderKnob(Button):
    def __init__(self, width, height, rect, function, Mouse, Timing, Sound, surface, container, definition, parent, RENDER_SCALE = 1, ToolTips = None, slider = None):
        super().__init__(Timing, surface, Mouse, function, container, width, height, style = 'lighten', maintain_alpha = False, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
        
        self.RENDER_SCALE = RENDER_SCALE
        self.slider = slider
        
        self.x_position = rect.x
        self.y_position = rect.y
        
        self.surface = surface
        self.container = container
        
        self.width = width
        self.height = height
        self.rect = rect
        
        self.definition = definition
        
        self.shadow_radius = int(3 * self.RENDER_SCALE)
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        self.init_tooltip(self.definition)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        
        self.hover_sound = SFX.MenuTap
        
    def get_local_position(self):
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        self.render_knob()
        self.render_shadow()
        
    def render_knob(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect(), self.RENDER_SCALE)
    
    def render_shadow(self):
        """
        Render the shadow of the button
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height)) # remove the area the button takes up from the shadow
        
    def update(self):
        if self.state is None:
            self.slider.ignore_events = False
        else:
            self.slider.ignore_events = True
            
        super().update()
        
    def update_position(self, x_position):
        self.x_position = x_position
        self.rect.x = x_position
        self.shadow_rect.x = x_position - self.shadow_radius * 2
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        
    def check_hover(self):
        """
        Check if the mouse is hovering over the button.
        """
        if self.state == 'pressed':
            return
        
        x, y = self.Mouse.position
        
        self.collision_rect.topleft = self.get_screen_position()
        
        if self.collision_rect.collidepoint((x, y)):
            if self.state == 'pressed':
                return
            self.state = 'hovered'
            self.play_hover_sound()
        else:
            self.state = None
    
    def check_events(self):
        """
        Check for input events.
        """
        events_to_remove = []
        mouse_x, mouse_y = self.Mouse.position
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button is MouseEvents.SCROLLWHEEL:
                    return
                
                event_x, event_y = info['pos']

                if button is MouseEvents.MOUSEBUTTON1 and info['down'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    self.Mouse.slider_interaction_event = True
                    self.being_dragged = True
                    events_to_remove.append(event)
                
                if button is MouseEvents.MOUSEBUTTON1 and info['up'] and self.being_dragged and self.Mouse.slider_interaction_event:
                    events_to_remove.append(event)
                    self.Mouse.slider_interaction_event = False
                    self.being_dragged = False
                    self.state = None
                    
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)