import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha
from render.GUI.font import Font
from render.GUI.buttons.button import Button

class ButtonBarSub(Button):
    def __init__(self, function:callable, Mouse, Timing, surface, container, definition, y_position, height, parent, RENDER_SCALE = 1):
        super().__init__(Timing, surface, Mouse, function, container, container.width, height, style = 'lighten', maintain_alpha = False, slider = 'left', parent = parent, RENDER_SCALE = 1)
        """
        A button bar that displays an image, along with big main text and smaller sub text
        
        args:
            function (callable): the function to call when the button is pressed
            Mouse (Mouse): the Mouse object
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the button on
            container (pygame.Rect): the container the button is in
            definition (dict): the definition of the button
            y_position (int): the y position of the button
            height (int): the height of the button
            parent (Object): the parent UI element
        """
        self.RENDER_SCALE = RENDER_SCALE
        
        self.surface = surface
        self.definition = definition
 
        self.default_x_position = self.container.width // 6
        self.hovered_x_position = self.default_x_position - int(50 * self.RENDER_SCALE)
        self.pressed_x_position = self.default_x_position - int(75 * self.RENDER_SCALE)

        self.x_position = self.default_x_position
        
        self.y_position = y_position
        
        self.main_font = Font('hun2', int(35 * self.RENDER_SCALE))
        self.sub_font = Font('hun2', int(18 * self.RENDER_SCALE))
        self.shadow_radius = int(5 * self.RENDER_SCALE)
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
            
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button
        """
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        """
        Render the button and its shadow
        """
        self.render_shadow()
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect(), self.RENDER_SCALE)
        self.render_text()
              
    def render_text(self):
        """
        Render the text on the button
        """
        self.main_font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'left', int(22 * self.RENDER_SCALE), - self.main_font.font.get_ascent() // 2 + int(2 * self.RENDER_SCALE))
        self.sub_font.draw(self.button_surface, self.definition['sub_text']['display_text'], self.definition['sub_text']['colour'], 'left', int(22 * self.RENDER_SCALE), self.main_font.font.get_ascent() // 2 + int(5 * self.RENDER_SCALE))
    
    def render_shadow(self):
        """
        Render the shadow of the button
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height)) # remove the area the button takes up from the shadow
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        