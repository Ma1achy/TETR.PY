import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha
from render.GUI.font import Font
from render.GUI.buttons.button import Button

class BackButton(Button):
    def __init__(self, function, Mouse, Timing, surface, container, definition, parent):
        super().__init__(Timing, surface, Mouse, function, container, 300, 60, style = 'lighten', maintain_alpha = False, slider = 'right', parent = parent)
        """
        Back button for a menu
        
        args:
            function (callable): the function to call when the button is pressed
            Mouse (Mouse): the Mouse object
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the button on
            container (pygame.Rect): the container the button is in
            definition (dict): the definition of the button
            parent (Object): the parent UI element
        """
        self.definition = definition

        self.default_x_position = 150
        self.hovered_x_position = 170
        self.pressed_x_position = 185
        
        self.x_position = self.default_x_position
        
        self.y_position = 15
        
        self.font = Font('hun2', 33)
        self.shadow_radius = 5
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
          
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button
        """
        self.rect = pygame.Rect(self.container.left - self.x_position, self.y_position, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.container.left - self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        """
        Render the button and its shadow
        """
        self.render_shadow()
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect())
        self.render_text()
    
    def render_text(self):
        """
        Render the text on the button
        """
        self.font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'right', 20, 0)
    
    def render_shadow(self):
        """
        Render the shadow of the button
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height)) # remove the area the button takes up from the shadow
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)

        