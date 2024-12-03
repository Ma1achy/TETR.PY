import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from render.GUI.font import Font
import json

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
            widget.update_image()
        
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
                
class Header:
    def __init__(self, container, height, text, background, border):
        self.container = container
        self.text = text
        self.background = background
        self.border = border

        self.width = self.container.width
        self.height = height
        
        self.rect = align_top_edge(self.container, self.width, self.height, 0, 0)
        
        self.header_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
        self.font = Font('hun2', 40)
        self.render_header()
        
    def render_header(self):
        if self.background['style'] == 'linear_gradient':
            draw_linear_gradient(self.header_surface, self.background['colours'][0], self.background['colours'][1], self.header_surface.get_rect())
        elif self.background['style'] == 'solid':
            draw_solid_colour(self.header_surface, self.background['colour'], self.header_surface.get_rect())
        
        self.font.draw(self.header_surface, self.text['display_text'], self.text['colour'], 'left', 20, 0)
        draw_border(self.header_surface, self.border, self.rect)
    
    def draw(self, surface):
        surface.blit(self.header_surface, self.rect.topleft)
    
    def handle_window_resize(self):
        self.width = self.container.width
        self.rect = align_top_edge(self.container, self.width, self.height, 0, 0)
        
        self.header_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
        self.render_header()
        
class Footer:
    def __init__(self, container, height, text, background, border, image = None):
        self.container = container
        self.text = text
        self.background = background
        self.border = border
              
        self.width = self.container.width
        self.height = height
        
        self.rect = align_bottom_edge(self.container, self.width, self.height, 0, 0)

        self.footer_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
    
        self.font = Font('hun2', 30)
        self.render_footer()
        
        if image:
            self.image = load_image(image["path"])
            self.render_image()

    def render_footer(self):
        if self.background['style'] == 'linear_gradient':
            draw_linear_gradient(self.footer_surface, self.background['colours'][0], self.background['colours'][1], self.footer_surface.get_rect())
        elif self.background['style'] == 'solid':
            draw_solid_colour(self.footer_surface, self.background['colour'], self.footer_surface.get_rect())
            
        draw_border(self.footer_surface, self.border, self.footer_surface.get_rect())
        self.font.draw(self.footer_surface, self.text['display_text'], self.text['colour'], 'left', 20, 0)
        
    def render_image(self):
        
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = self.height - 25
        new_width = int(new_height * aspect_ratio)
        
        image = pygame.transform.smoothscale(self.image, (new_width, new_height))
        image_rect = align_centre(self.footer_surface.get_rect(), image.get_width(), image.get_height(), 0, 0)

        self.footer_surface.blit(image, (image_rect.left + self.footer_surface.get_rect().width//2 - new_width - 40, image_rect.top))
        
    def draw(self, surface):
        surface.blit(self.footer_surface, self.rect.topleft)
        
    def handle_window_resize(self):
        self.width = self.container.width
        self.rect = align_bottom_edge(self.container, self.width, self.height, 0, 0)
        
        self.footer_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE)
        self.render_footer()
        
        if hasattr(self, 'image'):
            self.render_image()

class MainBody():
    def __init__(self, width, height, topleft, definition):
        
        self.definition = definition
        
        self.width = width
        self.height = height
        self.topleft = topleft
              
        self.body_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_body_container = self.body_surface.get_rect()
        self.render_body()
    
    def render_body(self):
        if 'logo' in self.definition:
            self.logo = Logo(self.main_body_container, self.definition['logo'])
            self.logo.draw(self.body_surface)
        
        if 'menu' in self.definition:
            for idx, element in enumerate(self.definition['menu']['elements']):
                if element['type'] == 'bar_button':
                    button = ButtonBar(self.body_surface, self.main_body_container, element, idx, height = 120)
                    button.update_image()
        
        if 'back_button' in self.definition:
            self.back_button = BackButton(self.body_surface, self.main_body_container, self.definition['back_button'])
            self.back_button.update_image()
        
    def draw(self, surface):
        surface.blit(self.body_surface, self.topleft)
    
    def handle_window_resize(self):
        self.body_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_body_container = self.body_surface.get_rect()
        
        if 'logo' in self.definition:
            self.logo = Logo(self.main_body_container, self.definition['logo'])
            self.logo.draw(self.body_surface)
        
        if 'menu' in self.definition:
            for idx, element in enumerate(self.definition['menu']['elements']):
                if element['type'] == 'bar_button':
                    button = ButtonBar(self.body_surface, self.main_body_container, element, idx, height = 120)
                    button.update_image()
        
        if 'back_button' in self.definition:
            self.back_button = BackButton(self.body_surface, self.main_body_container, self.definition['back_button'])
            self.back_button.update_image()
        
        self.render_body()
        
class Logo():
    def __init__(self, container, definition):
        
        self.container = container
        self.definition = definition
        self.image = load_image(self.definition['image'])  
        self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width() * self.definition['scale']), int(self.image.get_height() * self.definition['scale'])))
        
        if self.definition['alignment'] == 'bottom_left':
            self.rect = align_bottom_left(self.container, self.image.get_width(), self.image.get_height(), self.definition['padding'][0], self.definition['padding'][1])
            
        self.image.set_alpha(self.definition['opacity'])
        
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class ButtonBar():
    def __init__(self, surface, container, definition, list_index, height):
        self.surface = surface
        self.container = container
        self.definition = definition
        self.width = self.container.width
        self.height = height 
        
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.main_font = Font('hun2', 50)
        self.sub_font = Font('hun2', 23)
                
        self.y_offset = list_index * (self.height + 20) + 35
        self.start = self.container.width // 5.5
        
        self.render_button()
        self.get_hovered_image()
        self.get_pressed_image()
        
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.rect)
        draw_border(self.button_surface, self.definition['border'], self.rect)
        self.render_image()
        self.render_text()
       
    def render_image(self):
           
        x_padding = self.definition['image']['padding'][0]
        y_padding = self.definition['image']['padding'][1]
        button_height = self.rect.height - y_padding
        
        image = load_image(self.definition['image']['path'])     
        
        aspect_ratio = image.get_width() / image.get_height()
        new_width = int(button_height * aspect_ratio)

        image = pygame.transform.smoothscale(image, (new_width, button_height))
        image_rect = align_left_edge(self.rect, image.get_width(), image.get_height(), x_padding, y_padding)
        
        self.button_surface.blit(image, image_rect.topleft)
    
    def render_text(self):
        self.main_font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'left', 275, - self.main_font.font.get_ascent()//2 + 3)
        self.sub_font.draw(self.button_surface, self.definition['sub_text']['display_text'], self.definition['sub_text']['colour'], 'left', 275, self.main_font.font.get_ascent()//2 + 10)
    
    def get_hovered_image(self):
        self.hovered_surface = self.button_surface.copy()
        brightness(self.hovered_surface, 1.2)
    
    def get_pressed_image(self):
        self.pressed_surface = self.button_surface.copy()
        brightness(self.pressed_surface, 1.5)
        
    def update_image(self):
        self.surface.blit(self.button_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
        # self.surface.blit(self.hovered_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
        # self.surface.blit(self.pressed_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False
    
    def update(self, surface):
        self.hover = self.check_hover(pygame.mouse.get_pos())
        self.update_image(surface)
class BackButton():
    def __init__(self, surface, container, definition):
        self.surface = surface
        self.container = container
        self.definition = definition
        self.width = 300
        self.height = 60
        
        self.x_start = 150
        
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.font = Font('hun2', 33)
        
        self.render_button()
        self.get_hovered_image()
        self.get_pressed_image()
    
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.rect)
        draw_border(self.button_surface, self.definition['border'], self.rect)
        self.render_text()
    
    def get_hovered_image(self):
        self.hovered_surface = self.button_surface.copy()
        brightness(self.hovered_surface, 1.2)
    
    def get_pressed_image(self):
        self.pressed_surface = self.button_surface.copy()
        brightness(self.pressed_surface, 1.5)
    
    def render_text(self):
        self.font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'right', 20, 0)
        
    def update_image(self):
        self.surface.blit(self.button_surface, (self.rect.left - self.x_start , self.rect.top + 15))
        # self.surface.blit(self.hovered_surface, (self.rect.left - self.x_start, self.rect.top + 15))
        # self.surface.blit(self.pressed_surface, (self.rect.left - self.x_start, self.rect.top + 15))
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False

class FooterButton():
    def __init__(self, surface, container, definition):
        self.surface = surface
        self.container = container
        self.definition = definition
        self.width = 70
        self.height = 70
        self.x_start = 70
        
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.y_offset = 35
        self.render_button()
        self.render_image()
        self.get_hovered_image()
        self.get_pressed_image()
    
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.rect)
        draw_border(self.button_surface, self.definition['border'], self.rect)
    
    def render_image(self):
        x_padding = self.definition['image']['padding'][0]
        y_padding = self.definition['image']['padding'][1]
        button_width = self.rect.width - x_padding

        image = load_image(self.definition['image']['path'])     
        
        aspect_ratio = image.get_width() / image.get_height()
        new_height = int(button_width * aspect_ratio)

        image = pygame.transform.smoothscale(image, (button_width, new_height))
        image_rect = align_centre(self.rect, image.get_width(), image.get_height(), 0, -self.height//2 + y_padding - 2)
        
        self.button_surface.blit(image, image_rect.topleft)
    
    def get_hovered_image(self):
        self.hovered_surface = self.button_surface.copy()
        brightness(self.hovered_surface, 1.2)
    
    def get_pressed_image(self):
        self.pressed_surface = self.button_surface.copy()
        brightness(self.pressed_surface, 1.5)
        
    def update_image(self):
        self.surface.blit(self.button_surface, (self.container.right - 20 - self.width, self.container.bottom - self.x_start))
        # self.surface.blit(self.hovered_surface, (self.container.right - 20 - self.width, self.container.bottom - self.height + self.y_offset + self.x_start))
        # self.surface.blit(self.pressed_surface, (self.container.right - 20 - self.width, self.container.bottom - self.height + self.y_offset + self.x_start))
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False
    
    def handle_window_resize(self):
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.render_button()
        self.render_image()

    
