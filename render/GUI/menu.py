import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font
import json
from render.GUI.header import Header
from render.GUI.footer import Footer
from render.GUI.main_body import MainBody
from render.GUI.buttons.footer_button import FooterButton

class Menu():
    def __init__(self, surface, Config, Timing, Mouse, button_functions, menu_definition):
        self.surface = surface
        self.Config = Config
        self.Timing = Timing
        self.Mouse = Mouse
        self.button_functions = button_functions
        
        self.header_height = 0
        self.footer_height = 0
        
        self.footer_widgets = []

        self.__open_definition(menu_definition)
        self.__init_elements()
        
    def __open_definition(self, path):
        with open(path, 'r') as f:
            self.definition = json.load(f)
               
    def __init_elements(self):
        
        self.__init_header()
        self.__init_footer()  
        self.__init_menu_body()
        self.__init_footer_widgets()
        
    def __init_header(self):
        if 'menu_header' not in self.definition:
            return
        
        self.header_height = 70
        self.menu_header = Header(self.surface.get_rect(), self.header_height, self.definition['menu_header']['text'], self.definition['menu_header']['background'], self.definition['menu_header']['border'])
    
    def __init_footer(self):
        if 'menu_footer' not in self.definition:
            return
        
        self.footer_height = 55
        self.menu_footer = Footer(self.surface.get_rect(), self.footer_height, self.definition['menu_footer']['text'], self.definition['menu_footer']['background'], self.definition['menu_footer']['border'], image = self.__init_footer_image())
    
    def __init_footer_image(self):
        if 'image' in self.definition['menu_footer']:
            return self.definition['menu_footer']['image']
        return None
    
    def __init_menu_body(self):
        if 'menu_body' not in self.definition:
            return
            
        self.main_body_rect = pygame.Rect(0, self.header_height, self.surface.get_width(), self.surface.get_height() - self.footer_height - self.header_height)
        self.main_body = MainBody(self.Mouse, self.Timing, self.main_body_rect, self.button_functions, self.definition['menu_body'], parent = None)
    
    def __init_footer_widgets(self):
        if "footer_widgets" not in self.definition:
            return
            
        for element in self.definition["footer_widgets"]['elements']:
            if element['type'] == 'footer_button':
                func = self.button_functions[element['function']]
                self.footer_widgets.append(FooterButton(self.Timing, func, self.Mouse, self.surface, self.surface.get_rect(), element, parent = None))
             
    def update(self, in_dialog): 
        self.main_body.update(in_dialog)
        self.draw(self.surface)
        self.update_footer_widgets(in_dialog)
            
    def handle_window_resize(self):
        
        self.__header_resize()
        self.__footer_resize()
        self.__menu_body_resize()
        self.__footer_widgets_resize()

    def __header_resize(self):
        if 'menu_header' not in self.definition:
            return
        
        self.menu_header.container = self.surface.get_rect()
        self.menu_header.handle_window_resize()
    
    def __footer_resize(self):
        if 'menu_footer' not in self.definition:
            return
        
        self.menu_footer.container = self.surface.get_rect()
        self.menu_footer.handle_window_resize()
    
    def __menu_body_resize(self):
        if 'menu_body' not in self.definition:
            return
        
        self.main_body_rect = pygame.Rect(0, self.header_height, self.surface.get_width(), self.surface.get_height() - self.footer_height - self.header_height)
        self.main_body.rect = self.main_body_rect
        
        if self.main_body.rect.height <= 0: # to prevent crash
            self.main_body.rect.height = 1
        
        if self.main_body.rect.width <= 0:
            self.main_body.rect.width = 1
                 
        self.main_body.handle_window_resize()
    
    def __footer_widgets_resize(self):
        if "footer_widgets" not in self.definition:
            return 
        
        for widget in self.footer_widgets:
            widget.container = self.surface.get_rect()
            widget.handle_window_resize()
    
    def update_footer_widgets(self, in_dialog):
        if "footer_widgets" not in self.definition:
            return
        
        for widget in self.footer_widgets:
            widget.update(in_dialog)
    
    def reset_buttons(self):
        if 'menu_body' in self.definition:
            self.main_body.reset_buttons()
        
        if 'footer_widgets' in self.definition:
            for widget in self.footer_widgets:
                widget.reset_state()
          
    def draw(self, surface):
        self.main_body.draw(surface)
        self.menu_footer.draw(surface)
        self.menu_header.draw(surface)
        
        surface.blit(self.surface, (0, 0))
            
        