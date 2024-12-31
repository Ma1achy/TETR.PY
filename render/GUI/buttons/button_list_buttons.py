from render.GUI.buttons.button import Button
from utils import draw_border, draw_solid_colour, brightness
from render.GUI.font import Font
import pygame

class ButtonListButtons(Button):
    def __init__(self, Timing, Mouse, surface, container, definition, themeing, function, parent):
        super().__init__(Timing, surface, Mouse, function, container, container.width, container.height, style = 'lighten', maintain_alpha = False, slider = None, parent = parent)
        """
        A list of buttons where only one can be active at a time
        """
        self.Timing = Timing
        self.Mouse = Mouse
        
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
        self.font = Font('hun2', 23)
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        self.update_apperance()

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
    
    def render(self):
        """
        Render the button in its active and inactive states
        """
        self.render_inactive_state()
        self.render_active_state()
    
    def render_inactive_state(self):
        """
        Render the button in its inactive state
        """
        draw_solid_colour(self.inactive_surface, self.inactive_themeing['background']['colour'], self.inactive_surface.get_rect())
        draw_border(self.inactive_surface, self.inactive_themeing['border'], self.inactive_surface.get_rect())
        self.render_text(self.inactive_surface, self.inactive_themeing['text_colour'], self.display_text)
        
    def render_active_state(self):
        """
        Render the button in its active state
        """
        draw_solid_colour(self.active_surface, self.active_themeing['background']['colour'], self.active_surface.get_rect())
        draw_border(self.active_surface, self.active_themeing['border'], self.active_surface.get_rect())
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