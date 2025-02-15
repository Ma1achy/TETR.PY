from render.GUI.buttons.button import Button
from render.GUI.font import Font
import pygame
from utils import load_image, align_element, brightness_maintain_alpha, align_centre
from app.core.sound.sfx import SFX

class MusicSelectorButton(Button):
    def __init__(self, Timing, Mouse, Sound, surface, container, definition, function, parent, RENDER_SCALE = 1, ToolTips = None, button_functions = None):
        super().__init__(Timing, surface, Mouse, function, container, definition['size']['width'], definition['size']['height'], style = 'lighten', maintain_alpha = True, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
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
         
        self.font = Font('hun2', int(30 * self.RENDER_SCALE))
        
        self.button_functions = button_functions
        
         
        self.value_getter = self.button_functions[definition['value_getter']]
        self.text = self.value_getter()
        
        self.__get_rect_and_surface()
        self.render()
        self.init_tooltip(self.definition)

        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        self.hover_sound = SFX.MenuTap

        self.reset_on_click = True
        
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
        self.background_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        """
        Render the button
        """
        self.render_image()
        self.render_text()
        self.render_button()
        self.get_overlays()
    
    def render_button(self):
        """
        Render the background and border of the button
        """
        self.background_surface.fill(self.definition['background']['colour'])
          
    def render_text(self):
        """
        Render the text on the button
        """
        self.font.draw(self.button_surface, self.text, self.definition['text']['colour'], 'left', int(28 * self.RENDER_SCALE), 0)
    
    def render_image(self):
        """
        Render the image on the button
        """
    
        image_width = int(22 * self.RENDER_SCALE)

        image = load_image(self.definition['image'])
        
        aspect_ratio = image.get_width() / image.get_height()
        new_height = int(image_width * aspect_ratio)

        image = pygame.transform.smoothscale(image, (image_width, new_height))
        image_rect = align_element(self.button_surface.get_rect(), image.get_width(), image.get_height(), - self.width // 2 + image.get_width() // 2 , 0, 'centre_left')
        self.button_surface.blit(image, image_rect.topleft)
        
    def get_overlays(self):
        """
        Render the overlays for the button (hover and pressed states).
        """
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        
    def __get_lighten_overlay(self):
        """
        Render the lighten overlays for the button (hover and pressed states).
        """
        self.hover_surface = self.button_surface.copy()
        brightness_maintain_alpha(self.hover_surface, 1.5)

        self.pressed_surface = self.button_surface.copy()
        brightness_maintain_alpha(self.pressed_surface, 2.0)
    
    def draw(self):
        """
        Draw the button.
        """
        if not hasattr(self, 'button_surface') or self.button_surface is None:
            return 
        
        self.surface.blit(self.background_surface, self.rect.topleft)
        self.surface.blit(self.button_surface, self.rect.topleft)
    
    def get_value(self):
        """
        Get the value of the button
        """
        self.text = self.value_getter()
    
    def update_apperance(self):
        if self.text == self.value_getter():
            return
        
        self.background_surface.fill(self.definition['background']['colour'])
        self.button_surface.fill((0, 0, 0, 0))
        self.get_value()
        self.render()
        
    def update(self):
        """
        Update the button
        """
        self.update_apperance()
        super().update()
    
        
    