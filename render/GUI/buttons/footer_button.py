import pygame
from utils import load_image, draw_solid_colour, draw_border, align_centre, apply_gaussian_blur_with_alpha
from render.GUI.buttons.button import Button
from app.core.sound.sfx import SFX
class FooterButton(Button):
    def __init__(self, Timing, function, Mouse, Sound, surface, container, definition, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, function, container, 70, 100, style = 'lighten', maintain_alpha = False, slider = 'up', parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = None, Sound = Sound)
        """
        A button that is used in the footer of the screen
        
        args:
            Timing (Timing): the Timing object
            function (callable): the function to call when the button is pressed
            Mouse (Mouse): the Mouse object
            surface (pygame.Surface): the surface to draw the button on
            container (pygame.Rect): the container the button is in
            definition (dict): the definition of the button
            parent (Object): the parent UI element
        """
        self.RENDER_SCALE = RENDER_SCALE
        self.definition = definition
         
        self.default_y_position =  self.container.bottom - int(62 * self.RENDER_SCALE)
        self.hovered_y_position = self.default_y_position - int(14 * self.RENDER_SCALE)
        self.pressed_y_position = self.default_y_position - int(24 * self.RENDER_SCALE)
        
        self.x_offset = int(-90 * self.RENDER_SCALE)
        
        self.x_position = self.container.right + self.x_offset
        self.y_position = self.default_y_position
        
        self.shadow_radius = int(5 * self.RENDER_SCALE)
     
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        self.init_tooltip(self.definition)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
        
        self.click_sound = SFX.MenuHit1
        
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button
        """
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect =  pygame.Rect(self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render(self):
        """
        Render the button and its shadow
        """
        self.render_shadow()
        self.render_button()
        self.render_image()
        
    def render_button(self):
        """
        Render the button
        """
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect())
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect(), self.RENDER_SCALE)
        
    def render_image(self):
        """
        Render the image on the button
        """
        x_padding = int(self.definition['image']['padding'][0] * self.RENDER_SCALE)
        y_padding = int(self.definition['image']['padding'][1] * self.RENDER_SCALE)
        button_width = self.rect.width - x_padding

        image = load_image(self.definition['image']['path'])     
        
        aspect_ratio = image.get_width() / image.get_height()
        new_height = int(button_width * aspect_ratio)

        image = pygame.transform.smoothscale(image, (button_width, new_height))
        image_rect = align_centre(self.button_surface.get_rect(), image.get_width(), image.get_height(), 0, -self.height // 2 + y_padding - int(3 * self.RENDER_SCALE))
        
        self.button_surface.blit(image, image_rect.topleft)
    
    def handle_window_resize(self):
        """
        Handle the window being resized
        """
        self.x_position = self.container.right + self.x_offset
        self.default_y_position =  self.container.bottom - int(62 * self.RENDER_SCALE)
        self.hovered_y_position = self.default_y_position - int(14 * self.RENDER_SCALE)
        self.pressed_y_position = self.default_y_position - int(24 * self.RENDER_SCALE)
        self.y_position = self.default_y_position
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
    
    def render_shadow(self):
        """
        Render the shadow of the button
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(+self.shadow_radius * 2, +self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height)) # remove the area the button takes up from the shadow
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)

    