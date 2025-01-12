from render.GUI.buttons.button import Button
from render.GUI.font import Font
import pygame
from utils import draw_border, draw_solid_colour, align_element, apply_gaussian_blur_with_alpha

class GenericButton(Button):
    def __init__(self, Timing, Mouse, surface, container, definition, function, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, function, container, definition['size']['width'], definition['size']['height'], style = 'lighten', maintain_alpha = False, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips)
        """
        A generic button that can be used for any purpose
        
        args:
            Timing (Timing): the Timing object
            Mouse (Mouse): the Mouse object
            surface (pygame.Surface): the surface to draw the button on
            container (pygame.Rect): the container the button is in
            definition (dict): the definition of the button
            function (callable): the function to call when the button is pressed
            parent (Object): the parent UI element
        """
        self.RENDER_SCALE = RENDER_SCALE
        
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        
        self.definition = definition
        
        self.width = int(definition['size']['width'] * self.RENDER_SCALE)
        self.height = int(definition['size']['height'] * self.RENDER_SCALE)
        
        self.x_position = int(definition['position']['x'] * self.RENDER_SCALE)
        self.y_position = int(definition['position']['y'] * self.RENDER_SCALE)
        
        self.shadow_radius = int(3 * self.RENDER_SCALE)
         
        self.font = Font('hun2', int(23 * self.RENDER_SCALE))
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        self.init_tooltip(self.definition)

        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
    
    
    def get_local_position(self):
        """
        Get the position of the button relative to the container it is in for collision detection
        """
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button
        """

        if 'alignment' in self.definition:
            self.rect = align_element(self.container, self.width, self.height, self.x_position, self.y_position, self.definition['alignment'])
        else:
            self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
            
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.rect.x - self.shadow_radius * 2, self.rect.y - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        """
        Render the button
        """
        self.render_button()
        self.render_text()
        self.render_shadow()

    def render_button(self):
        """
        Render the background and border of the button
        """
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect(), self.RENDER_SCALE)
    
    def render_text(self):
        """
        Render the text on the button
        """
        self.font.draw(self.button_surface, self.definition['text']['display_text'], self.definition['text']['colour'], 'center', 0, 0)
    
    def render_shadow(self):
        """
        Render the shadow of the button
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height))
    
    def draw(self):
        """
        Draw the button.
        """
        if not hasattr(self, 'button_surface') or self.button_surface is None:
            return 
        
        self.shadow_surface.fill((0, 0, 0, 0))
        self.render_shadow()
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.surface.blit(self.button_surface, self.rect.topleft)
        
    def update(self, in_dialog):
        """
        Update the button
        """
        self.disable_layer_below()
        super().update(in_dialog)
        
    def disable_layer_below(self):
        """
        Disable the parent in the layer below the button when it is being hovered or pressed
        """
        if self.state is not None:
            self.parent.ignore_events = True
            self.parent.reset_state()
        else:
            self.parent.ignore_events = False
           
        
    

     
        
        