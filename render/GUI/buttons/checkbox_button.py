import pygame
from utils import draw_solid_colour, draw_border, brightness_maintain_alpha, load_image, apply_gaussian_blur_with_alpha
from render.GUI.buttons.button import Button
from render.GUI.font import Font
from app.core.sound.sfx import SFX
class CheckboxButton(Button):
    def __init__(self, button_functions, Timing, Mouse, Sound, surface, container, definition, y_position, parent, background_colour, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(Timing, surface, Mouse, None, container, width = container.width, height = container.height, style = 'lighten', maintain_alpha = True, slider = None, parent = parent, RENDER_SCALE = RENDER_SCALE, ToolTips = ToolTips, Sound = Sound)
        
        self.button_functions = button_functions
        self.RENDER_SCALE = RENDER_SCALE
        
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        
        self.x_padding = int(25 * self.RENDER_SCALE)
        self.y_padding = 0
        
        self.x_position = self.x_padding
        self.y_position = self.y_padding + y_position

        self.width = self.container.width - self.x_padding * 2
        self.height = int(44 * self.RENDER_SCALE)
        
        self.definition = definition
        self.y_position = y_position
        
        self.checkbox_width = int(32 * self.RENDER_SCALE)
        self.checkbox_height = int(32 * self.RENDER_SCALE)
        
        self.checkbox_x_pos = int((5 * self.RENDER_SCALE))
        self.checkbox_y_pos = int((self.height - self.checkbox_height) / 2)
        
        self.x_padding = int(10 * self.RENDER_SCALE)
        
        self.checkmark = load_image('resources/GUI/checkmark.png')
        self.checkmark_x_padding = int(6 * self.RENDER_SCALE)
        self.checkmark_y_padding = int(6 * self.RENDER_SCALE)
        self.checkmark = pygame.transform.smoothscale(self.checkmark, (self.checkbox_width - self.checkmark_x_padding, self.checkbox_height - self.checkmark_y_padding))
                
        self.active = False
        
        self.background_colour = background_colour
        self.active_themeing = self.definition['themeing']['active_state']
        self.inactive_themeing = self.definition['themeing']['inactive_state']
        
        self.shadow_radius = int(5 * self.RENDER_SCALE)
        
        self.font_size = int(25 * self.RENDER_SCALE)
        self.font = Font('hun2', self.font_size)      
        self.text = self.definition['text']
        
        self.pressed_surface_transition_time = 0
        
        self.__get_rect_and_surface()
        self.render_shadow()
        self.render_states()
        self.init_tooltip(self.definition)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height)) 
        
        self.hover_sound = SFX.MenuTap
        
        self.function = self.button_functions.get(self.definition.get('function'))
        self.value_getter = self.button_functions.get(self.definition.get('value_getter'))
        
        self.section = self.definition.get('section')
        self.key = self.definition.get('key')
        
        self.active = self.get_value()
        
    def get_value(self):
        if self.value_getter is None:
            return False
        
        return self.value_getter(self.section, self.key)
    
    def get_local_position(self):
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.checkbox_rect = pygame.Rect(self.checkbox_x_pos, self.checkbox_y_pos, self.checkbox_width, self.checkbox_height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rectangle = pygame.Rect(self.checkbox_x_pos - self.shadow_radius * 2, self.checkbox_y_pos - self.shadow_radius * 2, self.checkbox_width + self.shadow_radius * 4, self.checkbox_height + self.shadow_radius * 4)
        self.shadow_surf = pygame.Surface((self.shadow_rectangle.width, self.shadow_rectangle.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.active_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.inactive_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def render_shadow(self):
        pygame.draw.rect(self.shadow_surf, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rectangle.width - 4 * self.shadow_radius, self.shadow_rectangle.height - 4 * self.shadow_radius))
        self.shadow_surf = apply_gaussian_blur_with_alpha(self.shadow_surf, self.shadow_radius)
        
        pygame.draw.rect(self.shadow_surf, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.checkbox_width, self.checkbox_height)) # remove the area the button takes up from the shadow
            
    def draw_active_state(self, surface):
        draw_solid_colour(surface, self.active_themeing['background']['colour'], self.checkbox_rect)
        draw_border(surface, self.active_themeing['border'], self.checkbox_rect, self.RENDER_SCALE)
        self.font.draw(surface, self.text, self.active_themeing['text_colour'], 'left', self.checkbox_x_pos + self.checkbox_width + self.x_padding, 0)
        surface.blit(self.checkmark, (self.checkbox_x_pos + self.checkmark_x_padding // 2, self.checkbox_y_pos + self.checkmark_y_padding // 2))
        
    def draw_inactive_state(self, surface):
        draw_solid_colour(surface, self.inactive_themeing['background']['colour'], self.checkbox_rect)
        draw_border(surface, self.inactive_themeing['border'], self.checkbox_rect, self.RENDER_SCALE)
        self.font.draw(surface, self.text, self.inactive_themeing['text_colour'], 'left', self.checkbox_x_pos + self.checkbox_width + self.x_padding, 0)
    
    def render_states(self):
        # active
        self.draw_active_state(self.active_surface)
        temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        temp_surface.fill(self.background_colour)
        temp_surface.blit(self.active_surface, (0, 0))
        self.active_surface = temp_surface
        self.active_surface.blit(self.shadow_surf, self.shadow_rectangle.topleft)
        
        # inactive
        self.draw_inactive_state(self.inactive_surface)
        temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        temp_surface.fill(self.background_colour)
        temp_surface.blit(self.inactive_surface, (0, 0))
        self.inactive_surface = temp_surface
        
        # inactive hover
        self.inactive_hover_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_inactive_state(self.inactive_hover_surface)
        brightness_maintain_alpha(self.inactive_hover_surface, 1.2)
        
        temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        temp_surface.fill(self.background_colour)
        temp_surface.blit(self.inactive_hover_surface, (0, 0))
        self.inactive_hover_surface = temp_surface
        
        # active hover
        self.active_hover_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_active_state(self.active_hover_surface)
        brightness_maintain_alpha(self.active_hover_surface, 1.2)
        
        temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        temp_surface.fill(self.background_colour)
        temp_surface.blit(self.active_hover_surface, (0, 0))
        self.active_hover_surface = temp_surface
        self.active_hover_surface.blit(self.shadow_surf, self.shadow_rectangle.topleft)
        
        # inactive pressed
        self.inactive_pressed_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_inactive_state(self.inactive_pressed_surface)
        brightness_maintain_alpha(self.inactive_pressed_surface, 1.5)
        
        temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        temp_surface.fill(self.background_colour)
        temp_surface.blit(self.inactive_pressed_surface, (0, 0))
        self.inactive_pressed_surface = temp_surface
        
        # active pressed
        self.active_pressed_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.draw_active_state(self.active_pressed_surface)
        brightness_maintain_alpha(self.active_pressed_surface, 1.5)
        
        temp_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        temp_surface.fill(self.background_colour)
        temp_surface.blit(self.active_pressed_surface, (0, 0))
        self.active_pressed_surface = temp_surface
        self.active_pressed_surface.blit(self.shadow_surf, self.shadow_rectangle.topleft)
        
    def get_state_overlays(self):
        
        if self.active:
            self.button_surface = self.active_surface
            self.hover_surface = self.active_hover_surface
            self.pressed_surface = self.active_pressed_surface
        else:
            self.button_surface = self.inactive_surface
            self.hover_surface = self.inactive_hover_surface
            self.pressed_surface = self.inactive_pressed_surface
    
    def click(self):
        self.active = not self.active

        if self.ToolTips:
            self.ToolTips.tooltip_timer = 0
            
        if self.function is None:
            return
         
        self.function(self.section, self.key, self.active)
        
        if self.reset_on_click:
            self.state = None
    
    def update(self):
        self.get_state_overlays()
        super().update()
    
    def draw(self):
        super().draw()
        
        
        
        
    