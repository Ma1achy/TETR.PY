from render.GUI.buttons.button import Button
import pygame
from utils import hex_to_rgb, align_left_edge, align_right_edge, align_centre, brightness, brightness_maintain_alpha
from render.GUI.font import Font

class DialogButton(Button):
    def __init__(self, Timing, surface, Mouse, RenderStruct, text, function, width, height, colour, text_colour, style, container, dialog_rect, alignment, padding, border_radius, parent, RENDER_SCALE = 1):
        super().__init__(Timing, surface, Mouse, function, container, width, height, style = style, maintain_alpha = True, parent = parent, RENDER_SCALE = 1)
        """
        A button for a dialog box
        
        args:
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the button on
            Mouse (Mouse): the Mouse object
            RenderStruct (RenderStruct): the RenderStruct object
            text (str): the text to display on the button
            function (callable): the function to call when the button is pressed
            width (int): the width of the button
            height (int): the height of the button
            colour (str): the colour of the button
            text_colour (str): the colour of the text
            style (str): the style of the button
            container (pygame.Rect): the container the button is in
            dialog_rect (pygame.Rect): the rect of the dialog box
            alignment (str): the alignment of the button
            padding (tuple): the padding of the button
            border_radius (int): the border radius of the button
            parent (Object): the parent UI element
        """
        self.RenderStruct = RenderStruct
        self.RENDER_SCALE = RENDER_SCALE
        
        self.text = text
        self.text_colour = text_colour
        self.colour = colour
        self.style = style
        self.alignment = alignment
        
        self.dialog_rect = dialog_rect
        
        self.y_position = self.container.top + padding[1]
        
        self.main_font = Font('hun2', int(25 * self.RENDER_SCALE))
        self.x_padding, self.y_padding = padding
        self.border_radius = border_radius
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
            
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button
        """
        self.__get_alignment(self.alignment)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA | pygame.HWSURFACE)
        
    def __get_alignment(self, alignment):
        """
        Align the button within the container
        """
        if alignment == 'left':
            self.rect = align_left_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        elif alignment == 'right':
            self.rect = align_right_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        else:
            self.rect = align_centre(self.container, self.width, self.height, self.x_padding, self.y_padding)

    def render(self):
        """
        Render the button
        """
        pygame.draw.rect(self.button_surface, hex_to_rgb(self.colour), (0, 0, self.width, self.height), border_radius = self.border_radius)
        self.main_font.draw(self.button_surface, self.text, self.text_colour, 'centre', 0, 0)
        
    def get_overlays(self):
        """
        Render the hover and pressed overlays for the button
        """
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        self.__get_darken_overlay()
        
    def __get_lighten_overlay(self):
        """
        Render the lighten overlay style for the button
        """
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
        """
        Render the darken overlay style for the button
        """
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
    
    
