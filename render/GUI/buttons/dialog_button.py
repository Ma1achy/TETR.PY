from render.GUI.buttons.button import Button
import pygame
from utils import hex_to_rgb, align_left_edge, align_right_edge, align_centre, brightness, brightness_maintain_alpha
from render.GUI.font import Font

class DialogButton(Button):
    def __init__(self, Timing, surface, Mouse, RenderStruct, text, function, width, height, colour, text_colour, style, container, dialog_rect, alignment, padding, border_radius):
        super().__init__(Timing, surface, Mouse, function, container, width, height, offset = (dialog_rect.left, dialog_rect.top), style = style, maintain_alpha = True)
        
        self.RenderStruct = RenderStruct
        self.y_position = self.container.top + padding[1]
        self.text = text
        self.text_colour = text_colour
        self.colour = colour
        self.style = style
        self.alignment = alignment
        self.border_radius = border_radius
        self.x_padding, self.y_padding = padding
        self.dialog_rect = dialog_rect
        
        self.main_font = Font('hun2', 25)
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
    def render(self):
        pygame.draw.rect(self.button_surface, hex_to_rgb(self.colour), (0, 0, self.width, self.height), border_radius = self.border_radius)
        self.main_font.draw(self.button_surface, self.text, self.text_colour, 'centre', 0, 0)
    
    def __get_rect_and_surface(self):
        self.__get_alignment(self.alignment)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA | pygame.HWSURFACE)
    
    def __get_alignment(self, alignment):
        if alignment == 'left':
            self.rect = align_left_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        elif alignment == 'right':
            self.rect = align_right_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        else:
            self.rect = align_centre(self.container, self.width, self.height, self.x_padding, self.y_padding)
    
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
            brightness_maintain_alpha(self.hover_surface, 1.5)

            self.pressed_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.pressed_surface, 2.0)
        else:
            self.hover_surface = self.button_surface.copy()
            brightness(self.hover_surface, 1.5)

            self.pressed_surface = self.button_surface.copy()
            brightness(self.pressed_surface, 2.0)
        
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
