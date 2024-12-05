from render.render_new import StructRender
import pygame
from utils import hex_to_rgb, align_left_edge, align_right_edge, align_centre, brightness_maintain_alpha
from render.GUI.font import Font

class DialogButton():
    def __init__(self, Mouse, RenderStruct:StructRender, text, function, width, height, colour, text_colour, style, container, dialog_rect, alignment, padding, border_radius):
        
        self.Mouse = Mouse
        self.RenderStruct = RenderStruct
        
        self.function = function
        
        self.container = container
        self.dialog_rect = dialog_rect
        
        self.width = width
        self.height = height
        self.x_padding, self.y_padding = padding
        self.border_radius = border_radius
        self.alignment = alignment
        
        self.colour = colour
        self.style = style
    
        self.text = text
        self.text_colour = text_colour
        self.main_font = Font('hun2', 25)
        
        self.state = None
        self.previous_state = None
        
        self.__get_rect_and_surface()
        self.render()
        self.__get_lighten_overlay()
        self.__get_darken_overlay()
    
    def render(self):
        pygame.draw.rect(self.button_surface, hex_to_rgb(self.colour), (0, 0, self.width, self.height), border_radius = self.border_radius)
        
        self.main_font.draw(
            self.button_surface,
            self.text,
            self.text_colour,
            'centre',
            0,
            0,
        )   
    
    def __get_rect_and_surface(self):
        self.__get_alignment(self.alignment)
        self.button_surface = pygame.Surface((self.button_rect.width, self.button_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
    
    def __get_alignment(self, alignment):
        if alignment == 'left':
            self.button_rect = align_left_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        elif alignment == 'right':
            self.button_rect = align_right_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        else:
            self.button_rect = align_centre(self.container, self.width, self.height, self.x_padding, self.y_padding)
        
    def __get_lighten_overlay(self):
        if self.style != 'lighten':
            return
        
        self.hover_surface = self.button_surface.copy()
        brightness_maintain_alpha(self.hover_surface, 1.5)

        self.pressed_surface = self.button_surface.copy()
        brightness_maintain_alpha(self.pressed_surface, 2.0)
        
    def __get_darken_overlay(self):
        if self.style != 'darken':
            return
        
        self.hover_surface = self.button_surface.copy()
        brightness_maintain_alpha(self.hover_surface, 0.8)

        self.pressed_surface = self.button_surface.copy()
        brightness_maintain_alpha(self.pressed_surface, 0.5)
    
    def draw(self, surface):
        if self.state is None:
            surface.blit(self.button_surface, self.button_rect.topleft)
        if self.state == 'hovered':
            surface.blit(self.hover_surface, self.button_rect.topleft)
        elif self.state == 'pressed':
            surface.blit(self.pressed_surface, self.button_rect.topleft)
        
    def check_hover(self):
        x, y = self.Mouse.position 
        x -= self.dialog_rect.left
        y -= self.dialog_rect.top
        
        if self.button_rect.collidepoint((x, y)):
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
                event_x -=  self.dialog_rect.left
                event_y -= self.dialog_rect.top
                
                mouse_x, mouse_y = self.Mouse.position
                mouse_x -= self.dialog_rect.left
                mouse_y -= self.dialog_rect.top
                
                if button == 'mb1' and info['down'] and self.button_rect.collidepoint((event_x, event_y)) and self.button_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button == 'mb1' and info['up'] and self.button_rect.collidepoint((event_x, event_y)) and self.button_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = None
                    events_to_remove.append(event)
                    self.function()

        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def update(self):
        self.check_hover()
        self.check_events()
        
        if self.state != self.previous_state:
            self.render()
        
        self.previous_state = self.state


        