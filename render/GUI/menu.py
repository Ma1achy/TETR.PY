import pygame
from utils import hex_to_rgb
import os
import json
import numpy as np
import time
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
            self.menu_body = self.definition['menu_body']
            self.main_body_rect = pygame.Rect(0, self.header_height, self.surface.get_width(), self.surface.get_height() - self.footer_height - self.header_height)
            self.main_body = MainBody(self.main_body_rect.width, self.main_body_rect.height, self.main_body_rect.topleft, self.menu_body)
        if "footer_widgets" in self.definition:
            for element in self.definition["footer_widgets"]['elements']:
                if element['type'] == 'footer_button':
                    self.footer_widgets.append(FooterButton(self.surface, self.surface.get_rect(), element))
      
    def draw(self):
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
            
        
def align_top_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.top + v_padding, element_width, element_height)

def align_bottom_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.bottom - element_height - v_padding, element_width, element_height)

def align_right_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.right - element_width - h_padding, container.top + v_padding, element_width, element_height)

def align_left_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.top + v_padding, element_width, element_height)

def align_centre(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + (container.width - element_width) // 2 + h_padding, container.top + (container.height - element_height)//2 + v_padding, element_width, element_height)

def align_bottom_left(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.bottom - element_height - v_padding, element_width, element_height)

def align_bottom_right(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.right - element_width - h_padding, container.bottom - element_height - v_padding, element_width, element_height)

def align_top_right(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.right - element_width - h_padding, container.top + v_padding, element_width, element_height)

def align_top_left(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.top + v_padding, element_width, element_height)

def load_image(image_path):
    try:
        image = pygame.image.load(image_path).convert_alpha()
    except FileNotFoundError:
        image = pygame.surface.Surface((128, 128), pygame.HWSURFACE|pygame.SRCALPHA)
        image.fill((255, 0, 255))
    return image

def draw_linear_gradient(surface, start_colour, end_colour, rect):
    start_colour = hex_to_rgb(start_colour)
    end_colour = hex_to_rgb(end_colour)
    for y in range(rect.height):
        colour = [int(start_colour[i] + (y / rect.height) * (end_colour[i] - start_colour[i])) for i in range(3)]
        pygame.draw.line(surface, colour, (rect.left, rect.top + y), (rect.right, rect.top + y))

def draw_solid_colour(surface, colour, rect):
    pygame.draw.rect(surface, hex_to_rgb(colour), rect)

def draw_border(surface, border, rect):
    for side, value in border.items():
        width, colour = value
        if side == 'top':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.left, rect.top, rect.width, width))
        elif side == 'bottom':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.left, rect.bottom - width, rect.width, width))
        elif side == 'left':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.left, rect.top, width, rect.height))
        elif side == 'right':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.right - width, rect.top, width, rect.height))

def brightness(surface, brightness_factor):
    """
    Adjust the brightness of a surface
    
    args:
        surface (pygame.Surface): The surface to adjust the brightness of
        brightness_factor (float): The factor to adjust the brightness by (< 1 = darken, > 1 = brighten)
    """
    pygame.surfarray.blit_array(
        surface,  
        np.clip(
            (np.multiply(
                pygame.surfarray.array3d(surface), 
                brightness_factor
                )
            ),  
            0, 
            255
        )
    )
    
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
        
        # Assuming align_right_edge is your alignment function
        image = pygame.transform.smoothscale(self.image, (new_width, new_height))

        # Align the image to the right edge of the footer surface
        image_rect = align_centre(self.footer_surface.get_rect(), image.get_width(), image.get_height(), 0, 0)

        self.footer_surface.blit(image, (image_rect.left + self.footer_surface.get_rect().width//2 - new_width - 40, image_rect.top))
        
    def draw(self, surface):
        surface.blit(self.footer_surface, self.rect.topleft)

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
        
class Font():
    def __init__(self, type, size:int = 20):
        """
        Fonts used in the game
        
        args:
            size (int): The size of the font
        """
        self.size = size
        self.base_path = 'resources/font'
        self.type = type
    
        if self.type == 'hun2':

            font_path = os.path.join(self.base_path, 'hun2.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'pfw':

            font_path = os.path.join(self.base_path, 'pfw.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'cr':
            font_path = os.path.join(self.base_path, 'cr.ttf')
            self.font = pygame.font.Font(font_path, self.size)
        
        elif self.type == 'action_icons':
            font_path = os.path.join(self.base_path, 'action-icons.ttf')
            self.font = pygame.font.Font(font_path, self.size)
                
    def draw(self, surface, text, colour, alignment, h_padding=0, v_padding=0):
        rendered_text = self.font.render(text, True, hex_to_rgb(colour))

        if alignment == 'center':
            text_rect = rendered_text.get_rect(topleft = (surface.get_width() // 2 - rendered_text.get_width() // 2, (surface.get_height() //2 - self.font.get_ascent()//2)))
        elif alignment == 'left':
            text_rect = rendered_text.get_rect(topleft = (0, (surface.get_height() //2 - self.font.get_ascent()//2)))
        elif alignment == 'right':
            text_rect = rendered_text.get_rect(topleft = (surface.get_width() - rendered_text.get_width(), (surface.get_height() //2 - self.font.get_ascent()//2)))
            h_padding = -h_padding
        elif alignment == 'left_top':
            text_rect = rendered_text.get_rect(topleft = (0, (self.font.get_ascent()//2)))
        elif alignment == 'right_top':
            text_rect = rendered_text.get_rect(topleft = (surface.get_width() - rendered_text.get_width(), (self.font.get_ascent()//2)))
            h_padding = -h_padding
        elif alignment == 'left_bottom':
            text_rect = rendered_text.get_rect(topleft = (0, (surface.get_height() - self.font.get_height())))
            v_padding = -v_padding
        elif alignment == 'right_bottom':
            text_rect = rendered_text.get_rect(topleft = (surface.get_width() - rendered_text.get_width(), (surface.get_height() - self.font.get_height())))
            h_padding = -h_padding
            v_padding = -v_padding
        
        # Adjust positioning with paddings
        text_rect.x += h_padding
        text_rect.y += v_padding

        surface.blit(rendered_text, text_rect)

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
        self.surface.blit(self.hovered_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
        self.surface.blit(self.pressed_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))
    
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
        self.width = 150
        self.height = 60
        
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.font = Font('hun2', 35)
        
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
        self.surface.blit(self.button_surface, (self.rect.left, self.rect.top + 15))
        # self.surface.blit(self.hovered_surface, (self.rect.left, self.rect.top + 15))
        # self.surface.blit(self.pressed_surface, (self.rect.left, self.rect.top + 15))
    
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
        self.height = 100
        
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
        self.surface.blit(self.button_surface, (self.container.right - 20 - self.width, self.container.bottom - self.height + self.y_offset))
        # self.surface.blit(self.hovered_surface, (self.container.right - 20 - self.width, self.container.bottom - self.height + self.y_offset))
        # self.surface.blit(self.pressed_surface, (self.container.right - 20 - self.width, self.container.bottom - self.height + self.y_offset))
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False

    
