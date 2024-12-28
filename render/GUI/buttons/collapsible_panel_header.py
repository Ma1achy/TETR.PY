import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha, hex_to_rgb, brightness, brightness_maintain_alpha
from render.GUI.buttons.button import Button
from render.GUI.font import Font
from render.GUI.buttons.generic_button import GenericButton

class CollapsiblePanelHeader(Button):
    def __init__(self, Timing, Mouse, surface, container, definition, y_position, parent):
        super().__init__(Timing, surface, Mouse, None, container, container.width, height = 75, style = 'lighten', maintain_alpha = True, slider = 'left', parent = parent)
        
        self.Timing = Timing

        self.Mouse = Mouse
        self.surface = surface
        self.container = container
        self.definition = definition
        self.y_position = y_position
        
        self.height = 75
        self.width = self.container.width - self.container.width // 3
        self.x_position = self.container.width // 6
        
        self.open = False
        
        self.default_x_position = self.container.width // 6
        self.hovered_x_position = self.x_position
        self.pressed_x_position = self.x_position

        self.shadow_radius = 5
        
        self.main_font = Font('d_din_bold', 45)
        
        self.elements = []
    
        self.__get_rect_and_surface()
        self.get_overlays()
        self.render()
        self.__render_states()
        self.get_state_overlays()
        self.__init_elements()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
    
    def __init_elements(self):
        if 'elements' not in self.definition:
            return
        
        for element in self.definition['elements']:
            if element['type'] == 'generic_button':
                function = None
                self.elements.append(GenericButton(self.Timing, self.Mouse, self.open_button_surface, self.button_surface.get_rect(), element, function, self))
    
    def render(self):
        self.render_shadow()
        self.render_panel(self.button_surface)
        self.render_button(self.button_surface, self.definition["button"]["closed_colour"])
        self.render_text(self.button_surface)
    
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)

        padd = 25
        height = self.height - padd
        width = height
        self.arrow_rect = pygame.Rect(padd//2 + 11, padd//2, width, height)
        
    def render_button(self, surface, colour):
        pygame.draw.rect(surface, hex_to_rgb(colour), self.arrow_rect, border_radius=5)
        
    def render_panel(self, surface):
        draw_solid_colour(surface, self.definition['background']['colour'], surface.get_rect())
        draw_border(surface, self.definition['border'], surface.get_rect())
        
    def render_shadow(self):
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height))
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
         
    def render_text(self, surface):
        self.main_font.draw(surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'left', 86, -3)
    
    def get_state_overlays(self):
        if self.open:
            self.button_surface = self.open_button_surface
            self.hover_surface = self.open_hover_surface
            self.pressed_surface = self.open_pressed_surface
        else:
            self.button_surface = self.closed_button_surface
            self.hover_surface = self.closed_hover_surface
            self.pressed_surface = self.closed_pressed_surface
            
    def get_overlays(self):
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        
    def __get_lighten_overlay(self):
       
        self.closed_hover_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_closed_state(self.closed_hover_surface)
        brightness_maintain_alpha(self.closed_hover_surface, 1.5)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, "#0B0D12")
        self.temp_surface.blit(self.closed_hover_surface, (0, 0))
        self.closed_hover_surface = self.temp_surface
        
        self.open_hover_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_open_state(self.open_hover_surface)
        brightness_maintain_alpha(self.open_hover_surface, 1.5)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, "#0B0D12")
        self.temp_surface.blit(self.open_hover_surface, (0, 0))
        self.open_hover_surface = self.temp_surface

        self.closed_pressed_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_closed_state(self.closed_pressed_surface)
        brightness_maintain_alpha(self.closed_pressed_surface, 2.0)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, "#0e0f11")
        self.temp_surface.blit(self.closed_pressed_surface, (0, 0))
        self.closed_pressed_surface = self.temp_surface
        
        self.open_pressed_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_open_state(self.open_pressed_surface)
        brightness_maintain_alpha(self.open_pressed_surface, 2.0)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, "#0e0f11")
        self.temp_surface.blit(self.open_pressed_surface, (0, 0))
        self.open_pressed_surface = self.temp_surface
        
    def __render_states(self):
        
        self.open_button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.__render_open_state()
        self.closed_button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.__get_closed_state()
        
    def __render_open_state(self):
        self.render_panel(self.open_button_surface)
        self.render_button(self.open_button_surface, self.definition["button"]["open_colour"])
        self.draw_open_state(self.open_button_surface)
    
    def __get_closed_state(self):
        self.render_panel(self.closed_button_surface)
        self.render_button(self.closed_button_surface, self.definition["button"]["closed_colour"])
        self.draw_closed_state(self.closed_button_surface)
        
    def click(self):
        self.open = not self.open
        self.get_state_overlays()
        if self.function is None:
            return
        self.function()
          
    def draw_open_state(self, surface):
    
        self.render_text(surface)
        pygame.draw.polygon(
            surface, 
            hex_to_rgb(self.definition['main_text']['colour']), 
            [
                (self.arrow_rect.center[0] - self.arrow_rect.width // 4, self.arrow_rect.center[1] + self.arrow_rect.height // 8), 
                (self.arrow_rect.center[0] + self.arrow_rect.width // 4, self.arrow_rect.center[1] + self.arrow_rect.height // 8), 
                (self.arrow_rect.center[0], self.arrow_rect.center[1] - self.arrow_rect.height // 8)
            ]
        )
    
    def draw_closed_state(self, surface):
      
        self.render_text(surface)
        pygame.draw.polygon(
            surface, 
            hex_to_rgb(self.definition['main_text']['colour']), 
            [
                (self.arrow_rect.center[0] - self.arrow_rect.width // 4, self.arrow_rect.center[1] - self.arrow_rect.height // 8), 
                (self.arrow_rect.center[0] + self.arrow_rect.width // 4, self.arrow_rect.center[1] - self.arrow_rect.height // 8), 
                (self.arrow_rect.center[0], self.arrow_rect.center[1] + self.arrow_rect.height // 8)
            ]
        )
    
    def update(self, in_dialog):
        self.update_elements(in_dialog)
        super().update(in_dialog)
       
       
    def update_elements(self, in_dialog):
        if not self.open:
            return
        
        for element in self.elements:
            element.update(in_dialog)
       
    
        