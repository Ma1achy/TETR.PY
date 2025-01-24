from render.GUI.buttons.button import Button
from utils import draw_border, draw_solid_colour, brightness, apply_gaussian_blur_with_alpha
from render.GUI.font import Font
import pygame

class ButtonListButtons(Button):
    def __init__(self, Timing, Mouse, Sound, surface, container, definition, themeing, function, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, function, container, container.width, container.height, style = 'lighten', maintain_alpha = False, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
        """
        A list of buttons where only one can be active at a time
        """
        self.RENDER_SCALE = RENDER_SCALE
        
        self.Timing = Timing
        self.Mouse = Mouse
        self.Sound = Sound
        
        self.surface = surface
        self.container = container
        self.width = container.width
        self.height = container.height
        
        self.function = function

        self.definition = definition
        self.themeing = themeing
        
        self.active = False
        self.state = None
        
        self.display_text = definition['display_text']
        self.inactive_themeing = self.themeing['inactive']
        self.active_themeing = self.themeing['active']
        
        self.y_position = container.top
        self.font = Font('hun2', int(23 * self.RENDER_SCALE))
        
        self.shadow_radius = int(3 * self.RENDER_SCALE)
        
        self.pressed_surface_transition_time = 0
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        self.update_apperance()
        self.init_tooltip(self.definition)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        
    def get_local_position(self):
        """
        Get the position of the button relative to the container it is in for collision detection
        """
        return self.container.topleft
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button
        """
        self.active_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.inactive_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.rect.x - self.shadow_radius * 2, self.rect.y - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        """
        Render the button in its active and inactive states
        """
        self.render_inactive_state()
        self.render_active_state()
        self.render_shadow()
    
    def render_inactive_state(self):
        """
        Render the button in its inactive state
        """
        draw_solid_colour(self.inactive_surface, self.inactive_themeing['background']['colour'], self.inactive_surface.get_rect())
        draw_border(self.inactive_surface, self.inactive_themeing['border'], self.inactive_surface.get_rect(), self.RENDER_SCALE)
        self.render_text(self.inactive_surface, self.inactive_themeing['text_colour'], self.display_text)
        
    def render_active_state(self):
        """
        Render the button in its active state
        """
        draw_solid_colour(self.active_surface, self.active_themeing['background']['colour'], self.active_surface.get_rect())
        draw_border(self.active_surface, self.active_themeing['border'], self.active_surface.get_rect(), self.RENDER_SCALE)
        self.render_text(self.active_surface, self.active_themeing['text_colour'], self.display_text)
    
    def render_text(self, surface, colour, text):
        """
        Render the text on the button
        """
        self.font.draw(surface, text, colour, 'centre', 0, 0)
    
    def get_overlays(self):
        """
        Render the overlays for the button (hover and pressed states)
        """
        self.get_inactive_overlay()
        self.get_active_overlay()
    
    def get_inactive_overlay(self):
        """
        Render the hovered and pressed states for the inactive state
        """
        self.inactive_hover_surface = self.inactive_surface.copy()
        brightness(self.inactive_hover_surface, 1.2)
        
        self.inactive_pressed_surface = self.inactive_surface.copy()
        brightness(self.inactive_pressed_surface, 1.5)
        
    def get_active_overlay(self):
        """
        Render the hovered and pressed states for the active state
        """
        self.active_hover_surface = self.active_surface.copy()
        brightness(self.active_hover_surface, 1.2)
        
        self.active_pressed_surface = self.active_surface.copy()
        brightness(self.active_pressed_surface, 1.5)
    
    def update_apperance(self):
        """
        Update the apperance of the button based on its state
        """
        if self.active:
            self.button_surface = self.active_surface
            self.hover_surface = self.active_hover_surface
            self.pressed_surface = self.active_pressed_surface
        else:
            self.button_surface = self.inactive_surface
            self.hover_surface = self.inactive_hover_surface
            self.pressed_surface = self.inactive_pressed_surface
    
    def click(self):
        """
        Handle the button being clicked
        """
        self.parent.on_click()
        self.active = not self.active
        super().click()
        
    def update(self, in_dialog):
        """
        Update the button
        """
        self.update_apperance()
        super().update(in_dialog)
    
    def draw(self):
        """
        Draw the button.
        """
        if not hasattr(self, 'button_surface') or self.button_surface is None:
            return 
        
        if not self.active:
            self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.surface.blit(self.button_surface, self.rect.topleft)
    
    def render_shadow(self):
        """
        Render the shadow of the button
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height))