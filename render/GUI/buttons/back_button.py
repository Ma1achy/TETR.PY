import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha, brightness, brightness_maintain_alpha
from render.GUI.font import Font
from render.GUI.buttons.button import Button
from app.core.sound.sfx import SFX
from app.core.config_manager import VideoSettings

class BackButton(Button):
    def __init__(self, function, Mouse, Timing, Sound, surface, container, definition, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, function, container, 300, 60, style = 'lighten', maintain_alpha = False, slider = 'right', parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
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
        self.RENDER_SCALE = RENDER_SCALE
        
        self.definition = definition
        
        self.type = self.definition['type'] if 'type' in self.definition else None
        self.maintain_alpha = True if self.type == 'exit' else False

        self.default_x_position = int(150 * self.RENDER_SCALE)
        self.hovered_x_position = int(180 * self.RENDER_SCALE)
        self.pressed_x_position = int(200 * self.RENDER_SCALE)
        
        self.x_position = self.default_x_position
        
        self.y_position = int(15 * self.RENDER_SCALE)
        
        self.font = Font('hun2', int(33 * self.RENDER_SCALE))
        self.shadow_radius = int(5 * self.RENDER_SCALE)
        
        self.__get_rect_and_surface()
        self.render()
        self.get_overlays()
        self.init_tooltip(self.definition)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
        
        self.click_sound = SFX.MenuBack
        
        if "dropdown" in self.definition:
            self.dropdown = self.definition["dropdown"]
            self.y_position += int(70 * self.RENDER_SCALE)
        else:
            self.dropdown = False
            
        self.reset_on_click = True
        self.disable_shadow = True
        
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
        if self.type == 'exit':
            alpha_bg = 0.3
            alpha_br = 0.5
        else:
            alpha_bg = 1
            alpha_br = 1
            
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.button_surface.get_rect(), alpha = alpha_bg)
        draw_border(self.button_surface, self.definition['border'], self.button_surface.get_rect(), self.RENDER_SCALE, alpha = alpha_br)
        
        self.render_text()
        
    def render_text(self):
        """
        Render the text on the button
        """    
        if self.type == 'exit':
            alpha = 0.5
        else:
            alpha = 1
        self.font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'right', int(20 * self.RENDER_SCALE), 0, alpha = alpha)
    
    def render_shadow(self):
        """
        Render the shadow of the button
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height)) # remove the area the button takes up from the shadow
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
    
    def get_overlays(self):
        """
        Render the overlays for the button (hover and pressed states).
        """
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        self.__get_darken_overlay()
        
    def __get_lighten_overlay(self):
        """
        Render the lighten overlays for the button (hover and pressed states).
        """
        if self.style != 'lighten':
            return
        
        if self.maintain_alpha:
            self.hover_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.hover_surface)
            brightness_maintain_alpha(self.hover_surface, 1.2)

            self.pressed_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.pressed_surface)
            brightness_maintain_alpha(self.pressed_surface, 1.5)
        else:
            self.hover_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.hover_surface)
            brightness(self.hover_surface, 1.2)

            self.pressed_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.pressed_surface) 
            brightness(self.pressed_surface, 1.5)
        
    def __get_darken_overlay(self):
        """
        Render the darken overlays for the button (hover and pressed states).
        """
        if self.style != 'darken':
            return
        
        if self.maintain_alpha:
            self.hover_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.hover_surface)
            brightness_maintain_alpha(self.hover_surface, 0.8)

            self.pressed_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.pressed_surface)
            brightness_maintain_alpha(self.pressed_surface, 0.5)
        else:
            self.hover_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.hover_surface)
            brightness(self.hover_surface, 0.8)

            self.pressed_surface = self.button_surface.copy()
            if self.type == 'exit':
                self.draw_exit_apperance(self.pressed_surface)
            brightness(self.pressed_surface, 0.5)
            
    def draw_exit_apperance(self, surface):
        surface.fill((0, 0, 0, 0))
        draw_solid_colour(surface, "#440000", surface.get_rect(), alpha = 0.3)
        draw_border(
            surface, 
            {
            "top": [
                3,
                "#442222"
            ],
            "bottom": [
                3,
                "#440000",
            ],
            "right": [
                3,
                "#441111"
            ]
            }, 
            surface.get_rect(),
            self.RENDER_SCALE,
            alpha = 0.6
        )
        self.font.draw(surface, self.definition['main_text']['display_text'], "#ffaaaa", 'right', int(20 * self.RENDER_SCALE), 0)
