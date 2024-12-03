import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font
import json
from render.GUI.header import Header
from render.GUI.footer import Footer
from render.GUI.main_body import MainBody
from render.GUI.buttons.footer_button import FooterButton

class Menu():
    def __init__(self, surface, Config, Timing, menu_definition):
        self.surface = surface
        self.Config = Config
        self.Timing = Timing
        
        self.header_height = 0
        self.footer_height = 0
        
        self.footer_widgets = []
        self.open_definition(menu_definition)
        self.__init_elements()
        
    def __init_elements(self):
        
        if 'menu_header' in self.definition:
            self.header_height = 70
            self.menu_header = Header(self.surface.get_rect(), self.header_height, self.definition['menu_header']['text'], self.definition['menu_header']['background'], self.definition['menu_header']['border'])
            
        if 'menu_footer' in self.definition:
            self.footer_height = 55
            if 'image' in self.definition['menu_footer']:
                image = self.definition['menu_footer']['image']
            else:
                image = None
            self.menu_footer = Footer(self.surface.get_rect(), self.footer_height, self.definition['menu_footer']['text'], self.definition['menu_footer']['background'], self.definition['menu_footer']['border'], image)
            
        if 'menu_body' in self.definition:
            self.main_body_rect = pygame.Rect(0, self.header_height, self.surface.get_width(), self.surface.get_height() - self.footer_height - self.header_height)
            self.main_body = MainBody(self.main_body_rect.width, self.main_body_rect.height, self.main_body_rect.topleft, self.definition['menu_body'])
            
        if "footer_widgets" in self.definition:
            for element in self.definition["footer_widgets"]['elements']:
                if element['type'] == 'footer_button':
                    self.footer_widgets.append(FooterButton(self.surface, self.surface.get_rect(), element))
      
    def update(self):
        self.main_body.draw(self.surface)
        self.menu_header.draw(self.surface)
        self.menu_footer.draw(self.surface)
        
        for widget in self.footer_widgets:
            widget.draw()
        
    def definition_to_json(self, path):
        with open(path, 'w') as f:
            json.dump(self.definition, f, indent = 4)
            
    def open_definition(self, path):
        with open(path, 'r') as f:
            self.definition = json.load(f)
    
    def handle_window_resize(self):
        if 'menu_header' in self.definition:
            self.menu_header.container = self.surface.get_rect()
            self.menu_header.handle_window_resize()
        
        if 'menu_footer' in self.definition:
            self.menu_footer.container = self.surface.get_rect()
            self.menu_footer.handle_window_resize()
        
        if 'menu_body' in self.definition:
            self.main_body.width = self.surface.get_width()
            self.main_body.height = self.surface.get_height() - self.footer_height - self.header_height
            self.main_body.handle_window_resize()
        
        if "footer_widgets" in self.definition:
            for widget in self.footer_widgets:
                widget.container = self.surface.get_rect()
                widget.handle_window_resize()