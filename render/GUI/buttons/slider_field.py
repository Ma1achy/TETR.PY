from render.GUI.buttons.button import Button
from render.GUI.font import Font
import pygame
from render.GUI.diaglog_box import DialogBox
from render.GUI.menu_elements.text_input import TextInput

class SliderField(Button):
    def __init__(self, button_functions, width, height, rect, function, Mouse, Timing, surface, container, definition, parent, RENDER_SCALE = 1):
        super().__init__(Timing, surface, Mouse, function, container, width, height, style = 'lighten', maintain_alpha = True, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE)
        """
        A field value button for a slider of the config menu
        
        args:
            width (int): the width of the button
            height (int): the height of the button
            function (callable): the function to call when the button is pressed
            Mouse (Mouse): the Mouse object
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the button on
            container (pygame.Rect): the container the button is in
            definition (dict): the definition of the button
            parent (Object): the parent UI element
        """
        self.button_functions = button_functions
        self.RENDER_SCALE = RENDER_SCALE
        self.x_position = rect.x
        self.y_position = container.y
        
        self.width = width
        self.height = height
        self.rect = rect
                  
        self.definition = definition

        self.unit_font = Font('hun2', int(27 * self.RENDER_SCALE))
        self.shadow_radius = int(5 * self.RENDER_SCALE)
        
        self.value = 100
        self.value_str = str(self.value) if not isinstance(self.value, str) else self.value
        
        self.min_value = 0
        self.max_value = 0
        self.max_value_to_inf = False
        
        if self.value == self.max_value and self.max_value_to_inf:
            self.value_str = '∞'
        
        self.value_font = Font('hun2', int(27 * self.RENDER_SCALE))
         
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
     
    def get_local_position(self):
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.unit_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.value_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        self.render_background()
        self.render_unit()
    
    def render_background(self):
        pygame.draw.rect(self.button_surface, self.definition["background_colour"], self.button_surface.get_rect(), border_radius = int(5 * self.RENDER_SCALE))

    def render_unit(self):
        self.unit_font.draw(self.unit_surface, self.definition['unit'], self.definition['unit_font_colour'], 'right', h_padding = int(7 * self.RENDER_SCALE), v_padding = 0)
        self.button_surface.blit(self.unit_surface, (0, 0))
    
    def draw_value(self):
        self.value_surface.fill((0, 0, 0, 0))
        self.value_font.draw(self.value_surface, self.value_str, self.definition['value_font_colour'], 'right', h_padding = self.unit_font.get_width() + int(10 * self.RENDER_SCALE), v_padding = 0)    
        self.surface.blit(self.value_surface, (self.x_position, self.y_position))
        
    def draw(self):
        super().draw()
        self.draw_value()
    
    def animate_hover_surface_transition(self):
        """
        Animate the transition into the hover surface.
        """
        super().animate_hover_surface_transition()
        self.surface.blit(self.value_surface, (self.x_position, self.y_position))
    
    def update_value(self):
        self.value_str = str(self.value) if not isinstance(self.value, str) else self.value
        
        if self.value == self.max_value and self.max_value_to_inf:
            self.value_str = '∞'
            
    def animate_pressed_surface_transition(self):
        """
        Animate the transition into the pressed surface.
        """
        super().animate_pressed_surface_transition()
        self.surface.blit(self.value_surface, (self.x_position, self.y_position))
    
    def update(self, in_dialog = False):
        self.update_value()
        super().update(in_dialog)