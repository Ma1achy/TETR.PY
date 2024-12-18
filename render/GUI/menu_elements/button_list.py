import pygame
from render.GUI.buttons.button import Button
from utils import draw_border, draw_solid_colour, brightness
from render.GUI.font import Font
from render.GUI.menu_elements.nested_element import NestedElement

class ButtonList(NestedElement):
    def __init__(self, Timing, Mouse, surface, container, definition, y_position, parent):
        super().__init__(parent)
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        
        self.definition = definition
        self.themeing = self.definition['themeing']
        
        self.title_font_size = 23
        self.title_padding = self.title_font_size + 5
        self.x_padding = 25
        self.y_padding = 0
        
        self.x_position = self.x_padding
        self.y_position = self.y_padding + y_position

        self.width = self.container.width - self.x_padding * 2
        self.height = 65 - self.y_padding * 2
        
        self.buttons = []
        
        self.title_font = Font('d_din_bold', self.title_font_size )
        self.title_text = self.get_title()
        self.__get_rect_and_surface()
        self.__init_buttons()
        self.render()
    
    def get_title(self):
        if 'title' in self.definition:
            self.title = True
            return self.definition['title']
        self.title = False
        
    def get_local_position(self):
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        if self.title:
            self.height += self.title_padding
            
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.button_list_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def __init_buttons(self):
        for idx, button in enumerate(self.definition['buttons']):
            self.generate_button(button, idx)
      
    def generate_button(self, button, idx):
        
        button_rect = self.get_button_rect(idx) 
       
        self.buttons.append(ButtonListButtons(self.Timing, self.Mouse, self.button_list_surface, button_rect, button, self.themeing, button['function'], parent = self))     
    
    def get_button_rect(self, idx):
        num_buttons = len(self.definition['buttons'])
        edge_padding = 15
        inter_button_padding = 5
        y_padd = 15
        
        total_padding = edge_padding * 2 + inter_button_padding * (num_buttons - 1)
        button_width = (self.width - total_padding) // num_buttons
        button_height = self.height - y_padd * 2 if not self.title else self.height - y_padd * 2 - self.title_padding
        
        x_position = edge_padding + idx * (button_width + inter_button_padding)
        y_position = y_padd if not self.title else y_padd + self.title_padding
        
        return pygame.Rect(x_position, y_position, button_width, button_height)
        
    def render(self):
        self.render_background()
        self.render_title()
        self.render_buttons()
    
    def render_title(self):
        if not self.title:
            return
        
        self.title_font.draw(self.button_list_surface, self.title_text, self.themeing["title_colour"], 'left_top', 15, 0)
        
    def render_background(self):
        pygame.draw.rect(self.button_list_surface, self.themeing['background_colour'], self.button_list_surface.get_rect(), border_radius = 5)
        
    def render_buttons(self):
        pass
    
    def draw(self):
        self.surface.blit(self.button_list_surface, (self.x_position, self.y_position))

    def update(self, in_dialog):
        self.draw()
        
        if in_dialog:
            return
        
        self.update_buttons(in_dialog)
    
    def update_buttons(self, in_dialog):
        for button in self.buttons:
            button.update(in_dialog)
    
    def on_click(self):
        for button in self.buttons:
            button.active = False
class ButtonListButtons(Button):
    def __init__(self, Timing, Mouse, surface, container, definition, themeing, function, parent):
        super().__init__(Timing, surface, Mouse, function, container, container.width, container.height, style = 'lighten', maintain_alpha = False, slider = None, parent = parent)
        
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        self.width = container.width
        self.height = container.height
        
        self.function = function
        
        self.function = None # temp
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
    
    def get_local_position(self):
        return self.container.topleft
    
    def __get_rect_and_surface(self):
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        self.active_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.inactive_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render(self):
        self.render_inactive_state()
        self.render_active_state()
    
    def render_inactive_state(self):
        draw_solid_colour(self.inactive_surface, self.inactive_themeing['background']['colour'], self.inactive_surface.get_rect())
        draw_border(self.inactive_surface, self.inactive_themeing['border'], self.inactive_surface.get_rect())
        self.render_text(self.inactive_surface, self.inactive_themeing['text_colour'], self.display_text)
        
    def render_active_state(self):
        draw_solid_colour(self.active_surface, self.active_themeing['background']['colour'], self.active_surface.get_rect())
        draw_border(self.active_surface, self.active_themeing['border'], self.active_surface.get_rect())
        self.render_text(self.active_surface, self.active_themeing['text_colour'], self.display_text)
    
    def render_text(self, surface, colour, text):
        self.font.draw(surface, text, colour, 'centre', 0, 0)
    
    def get_overlays(self):
        self.get_inactive_overlay()
        self.get_active_overlay()
    
    def get_inactive_overlay(self):
        self.inactive_hover_surface = self.inactive_surface.copy()
        brightness(self.inactive_hover_surface, 1.2)
        
        self.inactive_pressed_surface = self.inactive_surface.copy()
        brightness(self.inactive_pressed_surface, 1.5)
        
    def get_active_overlay(self):
        self.active_hover_surface = self.active_surface.copy()
        brightness(self.active_hover_surface, 1.2)
        
        self.active_pressed_surface = self.active_surface.copy()
        brightness(self.active_pressed_surface, 1.5)
    
    def update_apperance(self):
        if self.active:
            self.button_surface = self.active_surface
            self.hover_surface = self.active_hover_surface
            self.pressed_surface = self.active_pressed_surface
        else:
            self.button_surface = self.inactive_surface
            self.hover_surface = self.inactive_hover_surface
            self.pressed_surface = self.inactive_pressed_surface
    
    def click(self):
        self.parent.on_click()
        self.active = not self.active
        super().click()
        
    def update(self, in_dialog):
        self.update_apperance()
        super().update(in_dialog)
        
        
    
        

        
        
        
    
    
        
    

       