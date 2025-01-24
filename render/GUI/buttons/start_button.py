from render.GUI.buttons.button import Button
from render.GUI.font import Font
import pygame
from utils import draw_border, draw_solid_colour, align_element, brightness
import math
from app.input.mouse.mouse import MouseEvents
from app.core.sound.sfx import SFX
class StartButton(Button):
    def __init__(self, Timing, Mouse, Sound, surface, container, definition, function, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, function, container, definition['size']['width'], definition['size']['height'], style = None, maintain_alpha = False, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
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
        
        self.font = Font('hun2', int(65 * self.RENDER_SCALE))
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        self.init_tooltip(self.definition)

        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        
        self.glow_alpha = 0
        self.glow_time = 1
        self.glow_timer = 0

        self.click_sound = SFX.MenuConfirm
        
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
        
    def render(self):
        """
        Render the button
        """
        self.render_button()
        self.render_text()

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
    
    def update(self, in_dialog):
        """
        Update the button
        """
        self.disable_layer_below()
        self.animate_glow()
        super().update(in_dialog)
        
    def disable_layer_below(self):
        """
        Disable the parent in the layer below the button when it is being hovered or pressed
        """
        if self.state is 'hovered':
            self.parent.ignore_events = True
        else:
            self.parent.ignore_events = False
    
    def get_overlays(self):
        self.__get_lighten_overlay()

    def __get_lighten_overlay(self):
        self.glow_surface = self.button_surface.copy()
        brightness(self.glow_surface, 1.75)
        
    def animate_glow(self):
        self.glow_timer += self.Timing.frame_delta_time
        alpha = self.beat(self.glow_timer, intensity = 2, frequency = 2) * 255
        self.glow_alpha = max(0, min(255, alpha)) 
        self.glow_surface.set_alpha(self.glow_alpha)
    
    def beat(self, value, intensity, frequency):
    
        v = math.atan(math.sin(value * math.pi * frequency) * intensity)
        return (v + math.pi / 2) / math.pi

    def draw(self):
        """
        Draw the button.
        """
        if not hasattr(self, 'button_surface') or self.button_surface is None:
            return 
        
        if not self.on_screen:
            return
        
        self.surface.blit(self.button_surface, self.rect.topleft)
        self.surface.blit(self.glow_surface, self.rect.topleft)