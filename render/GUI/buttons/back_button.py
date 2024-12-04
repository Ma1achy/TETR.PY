import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font

class BackButton():
    def __init__(self, function, Mouse, Keyboard, Timing, surface, container, definition):
        
        self.function = function
        self.Mouse = Mouse
        self.Keyboard = Keyboard
        self.Timing = Timing
        
        self.surface = surface
        self.container = container
        self.definition = definition
        self.width = 300
        self.height = 60
        
        self.x_start = 150
        self.font = Font('hun2', 33)
        
        self.previous_state = None
        self.state = None
        
        self.__get_rect_and_surface()
        self.render_button()
        self.get_hovered_image()
        self.get_pressed_image()
        
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.left - self.x_start, 15, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect())
        self.render_text()
    
    def get_hovered_image(self):
        self.hovered_surface = self.button_surface.copy()
        brightness(self.hovered_surface, 1.2)
    
    def get_pressed_image(self):
        self.pressed_surface = self.button_surface.copy()
        brightness(self.pressed_surface, 1.5)
    
    def render_text(self):
        self.font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'right', 20, 0)
        
    def draw(self):
        if self.state is None:
            self.surface.blit(self.button_surface, (self.rect.left, self.rect.top))
        elif self.state == 'hovered':
            self.surface.blit(self.hovered_surface, (self.rect.left, self.rect.top))
        elif self.state == 'pressed':
            self.surface.blit(self.pressed_surface, (self.rect.left, self.rect.top))
    
    def check_hover(self):
    
        x, y = self.Mouse.position 
        x -= self.container.left
        y -= self.container.top
        
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
                event_x -= self.container.left
                event_y -= self.container.top
                
                mouse_x, mouse_y = self.Mouse.position
                mouse_x -= self.container.left
                mouse_y -= self.container.top
                
                if button == 'mb1' and info['down'] and self.rect.collidepoint((event_x, event_y)) and self.rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button == 'mb1' and info['up'] and self.rect.collidepoint((event_x, event_y)) and self.rect.collidepoint((mouse_x, mouse_y)):
                    self.state = None
                    events_to_remove.append(event)
                    self.function()
        
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
               
    def update(self):
        self.check_hover()
        self.check_events()

        if self.state != self.previous_state:
            self.draw()
        
        self.previous_state = self.state