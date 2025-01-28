import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha, hex_to_rgb, brightness_maintain_alpha, smoothstep
from render.GUI.buttons.button import Button
from render.GUI.font import Font
from render.GUI.buttons.generic_button import GenericButton
from app.core.sound.sfx import SFX

class CollapsiblePanelHeader(Button):
    def __init__(self, Timing, Mouse, Sound, surface, container, definition, y_position, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, None, container, container.width, height = 75, style = 'lighten', maintain_alpha = True, slider = 'left', parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
        """
        A button that can be clicked to open or close a collapsible panel
        
        args:
            Timing (Timing): the Timing object
            Mouse (Mouse): the Mouse object
            surface (pygame.Surface): the surface to draw the button on
            container (pygame.Rect): the container the button is in
            definition (dict): the definition of the button
            y_position (int): the y position of the button
            parent (Object): the parent UI element
        """
        self.RENDER_SCALE = RENDER_SCALE
        self.ToolTips = ToolTips
        
        self.Timing = Timing
        self.Mouse = Mouse
        self.Sound = Sound
        
        self.surface = surface
        self.container = container
        self.definition = definition
        
        self.open = False
        self.elements = None
        self.ignore_events = False
        
        self.height = int(75 * self.RENDER_SCALE)
        self.width = self.container.width - self.container.width // 3
        
        self.x_position = self.container.width // 6
         
        self.default_x_position = self.container.width // 6
        self.hovered_x_position = self.x_position
        self.pressed_x_position = self.x_position

        self.y_position = y_position
        
        self.main_font = Font('d_din_bold', int(45 * self.RENDER_SCALE))
        self.shadow_radius = int(5 * self.RENDER_SCALE)
        
        self.__get_rect_and_surface()
        self.get_overlays()
        self.render()
        self.__render_states()
        self.get_state_overlays()
        self.__init_elements()
        self.init_tooltip(self.definition)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
        
        self.hover_sound = SFX.MenuTap
        
    def __init_elements(self):
        """
        Initialise the elements of the button
        """
        if 'elements' not in self.definition:
            return
        
        self.elements = []
        
        for element in self.definition['elements']:
            if element['type'] == 'generic_button':
                function = None
                self.elements.append(GenericButton(self.Timing, self.Mouse, self.Sound, self.element_surface, self.button_surface.get_rect(), element, function, self, self.RENDER_SCALE, self.ToolTips))
    
    def render(self):
        """
        Render the button and its shadow
        """
        self.render_shadow()
        self.render_panel(self.button_surface)
        self.render_button(self.button_surface, self.definition["button"]["closed_colour"])
        self.render_text(self.button_surface)
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button
        """
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.element_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)

        padd = int(25 * self.RENDER_SCALE)
        height = self.height - padd
        width = height
        self.arrow_rect = pygame.Rect(padd // 2 + int(11 * self.RENDER_SCALE), padd // 2, width, height)
        
    def render_button(self, surface, colour):
        """
        Render the button
        """
        pygame.draw.rect(surface, hex_to_rgb(colour), self.arrow_rect, border_radius = int(5 * self.RENDER_SCALE))
        
    def render_panel(self, surface):
        """
        Render the panel
        """
        draw_solid_colour(surface, self.definition['background']['colour'], surface.get_rect())
        draw_border(surface, self.definition['border'], surface.get_rect(), self.RENDER_SCALE)
        
    def render_shadow(self):
        """
        Render the shadow of the panel
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height))
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
         
    def render_text(self, surface):
        """
        Render the text of the button
        """
        self.main_font.draw(surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'left', int(86 * self.RENDER_SCALE), int(- 3 * self.RENDER_SCALE)) 
    
    def get_state_overlays(self):
        """
        Switch the hover and pressed overlays for the button based on its state
        """
        if self.open:
            self.button_surface = self.open_button_surface
            self.hover_surface = self.open_hover_surface
            self.pressed_surface = self.open_pressed_surface
        else:
            self.button_surface = self.closed_button_surface
            self.hover_surface = self.closed_hover_surface
            self.pressed_surface = self.closed_pressed_surface
            
    def get_overlays(self):
        """
        Get the hover and pressed overlays for the button
        """
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        
    def __get_lighten_overlay(self):
        """
        Get the hover and pressed overlays for the button for its open and closed states
        """
        self.closed_hover_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_closed_state(self.closed_hover_surface)
        brightness_maintain_alpha(self.closed_hover_surface, 1.5)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, self.definition["button"]["closed_colour"])
        brightness_maintain_alpha(self.temp_surface, 0.8)
        self.temp_surface.blit(self.closed_hover_surface, (0, 0))
        self.closed_hover_surface = self.temp_surface
        
        self.open_hover_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_open_state(self.open_hover_surface)
        brightness_maintain_alpha(self.open_hover_surface, 1.5)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, self.definition["button"]["open_colour"])
        brightness_maintain_alpha(self.temp_surface, 0.8)
        self.temp_surface.blit(self.open_hover_surface, (0, 0))
        self.open_hover_surface = self.temp_surface

        self.closed_pressed_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_closed_state(self.closed_pressed_surface)
        brightness_maintain_alpha(self.closed_pressed_surface, 2.0)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, self.definition["button"]["closed_colour"])
        brightness_maintain_alpha(self.temp_surface, 0.8)
        self.temp_surface.blit(self.closed_pressed_surface, (0, 0))
        self.closed_pressed_surface = self.temp_surface
        
        self.open_pressed_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_open_state(self.open_pressed_surface)
        brightness_maintain_alpha(self.open_pressed_surface, 2.0)
        
        self.temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button(self.temp_surface, self.definition["button"]["open_colour"])
        brightness_maintain_alpha(self.temp_surface, 0.8)
        self.temp_surface.blit(self.open_pressed_surface, (0, 0))
        self.open_pressed_surface = self.temp_surface
        
    def __render_states(self):
        """
        Render the open and closed states of the button
        """
        self.open_button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.__render_open_state()
        self.closed_button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.__get_closed_state()
        
    def __render_open_state(self):
        """
        Render the open state of the button
        """
        self.render_panel(self.open_button_surface)
        self.render_button(self.open_button_surface, self.definition["button"]["open_colour"])
        self.draw_open_state(self.open_button_surface)
    
    def __get_closed_state(self):
        """
        Render the closed state of the button
        """
        self.render_panel(self.closed_button_surface)
        self.render_button(self.closed_button_surface, self.definition["button"]["closed_colour"])
        self.draw_closed_state(self.closed_button_surface)
        
    def click(self):
        """
        Handle the click event for the button
        """
        self.open = not self.open
        self.get_state_overlays()
        if self.function is None:
            return
        self.function()
          
    def draw_open_state(self, surface):
        """
        Draw the open state of the button
        """
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
        """
        Draw the closed state of the button
        """
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
    
    def draw(self):
        """
        Draw the button.
        """
        if not hasattr(self, 'button_surface') or self.button_surface is None:
            return 
        
        if not self.on_screen:
            return
        
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.surface.blit(self.button_surface, self.rect.topleft)
        self.surface.blit(self.element_surface, self.rect.topleft)
    
    def check_elements_state(self):
        if self.elements is None:
            return 
        
        if any([element.state is not None for element in self.elements]):
            self.ignore_events = True
            self.state = None
            return
        
        self.ignore_events = False
        
    def update(self):
        """
        Update the button
        """
        self.check_elements_state()
        self.handle_scroll()
        self.check_if_on_screen()
        
        if not self.ignore_events:
            self.update_state()
            
        if self.state is None and self.previous_state is None:
            self.slider_hover_start_timer = 0
            
            if self.slider_hover_end_timer > 0 and self.slider_hover_end_timer < self.hover_slider_end_length:
                self.slider_hover_end_animation()
            
            if self.slider_pressed_end_timer > 0 and self.slider_pressed_end_timer < self.pressed_slider_end_length:
                self.slider_pressed_end_animation()
                  
        if self.state == 'hovered':
            self.handle_hover_start_events()
  
        elif self.state is None and self.previous_state == 'hovered':
            self.handle_hover_end_events()
        
        elif self.state == 'pressed':
            self.handle_pressed_start_events()
        
        elif self.previous_state == 'pressed' and self.state is None:
            self.handle_pressed_end_events()
            
        self.animate_menu_enter_transition()
        self.animate_menu_leave_transition()

        self.update_elements()
        
    def update_elements(self):
        """
        Update the elements of the button
        """
        if self.elements is None:
            return
        
        if not self.on_screen:
            return
        
        self.element_surface.fill((0, 0, 0, 0))
        
        if not self.open:
            return
        
        for element in self.elements:
            element.update()
    
    def animate_menu_transition_alpha(self, progress, is_enter):
        """
        Animate the alpha of the button surface during a menu transition.
        
            progress (float): Progress percentage of the animation.
            is_enter (bool): Whether the transition is entering or leaving the menu.
        """
        p = smoothstep(progress)
        alpha = ((p) * 255) if is_enter else (((1 - p)) * 255)
        alpha = max(0, min(255, alpha))
        
        self.button_surface.set_alpha(alpha)
        self.hover_surface.set_alpha(alpha)
        self.pressed_surface.set_alpha(alpha)
        self.shadow_surface.set_alpha(alpha)
        self.element_surface.set_alpha(alpha)
        