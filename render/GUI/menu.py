import pygame
from utils import hex_to_rgb
import os

class Menu():
    def __init__(self, surface, Config, Timing):
        self.surface = surface
        self.Config = Config
        self.Timing = Timing
        
        self.header_height = 0
        self.footer_height = 0
        
        self.definition = {
            'menu_header': {
                    'background': {
                    'style': 'linear_gradient', 
                    'colours': ('#272931', '#17191d')
                },
                'border': {
                    'bottom': (2, '#343642'),
                },
                'text': {
                    'colour': '#767d97', 
                    'display_text': 'HOME'
                },
            },
            'menu_body': {
                'logo' : {
                    'image': 'resources/logos/LogoLightGlow.png',
                    'alignment': 'bottom_left',
                    'padding': (20, 20),
                    'scale': 0.25,
                    'opacity': 32
                },
                'menu': {'scrollable': True, 'elements': [
                        {
                            'type': 'bar_button',
                            'function': 'go_to_multi',
                            'main_text': {
                                'colour': '#e9bed9',
                                'display_text': 'MULTIPLAYER'
                            },
                            'sub_text': {
                                'colour': '#c09ab3',
                                'display_text':'Play with friends and foes'
                            },
                            'image': 'resources/buttons/multi.svg',
                            'background': {
                                'style': 'solid',
                                'colour': '#34222d',
                            },
                            'border': {
                                'left': (3, '#3c2734'),
                                'top': (3, '#472d3c'),
                                'bottom': (3, '#271b22')
                            }
                        },
                        {
                            'type': 'bar_button',
                            'function': 'go_to_solo',
                            'main_text': {
                                'colour': '#bab8dc',
                                'display_text': 'SOLO'
                            },
                            'sub_text': {
                                'colour': '#8b88bc',
                                'display_text': 'Challenge yourself and top the leaderboards'
                            },
                            'image': 'resources/buttons/solo.svg',
                            'background': {
                                'style': 'solid',
                                'colour': '#1e1d2d',
                            },
                            'border': {
                                'left': (3, '#272639'),
                                'top': (3, '#2e2d42'),
                                'bottom': (3, '#12111b')
                            }
                        },
                        {
                            'type': 'bar_button',
                            'function': 'go_to_channel',
                            'main_text': {
                                'colour': '#a6fca3',
                                'display_text': 'RECORDS'
                            },
                            'sub_text': {
                                'colour': '#70be6d',
                                'display_text': 'Leaderboards, Replays and more'
                                },
                            'image': 'resources/buttons/records.svg',
                            'background': {
                                'style': 'solid',
                                'colour': '#1c3e2a',
                            },
                            'border': {
                                'left': (3, '#1e4822'),
                                'top': (3, '#1d6429'),
                                'bottom': (3, '#0e130f')
                            }
                        },
                        {
                            'type': 'bar_button',
                            'function': 'go_to_config',
                            'main_text': {
                                'colour': '#90aef9',
                                'display_text': 'CONFIG'
                            },
                            'sub_text': {
                                'colour': '#5668ba',
                                'display_text': 'Tweak your TETR.PY experience'
                            },
                            'image': 'resources/buttons/config.svg',
                            'background': {
                                'style': 'solid',
                                'colour': '#1c263e',
                            },
                            'border': {
                                'left': (3, '#1e2a48'),
                                'top': (3, '#1d3164'),
                                'bottom': (3, '#0e0f13')
                            }
                        },
                        {
                            'type': 'bar_button',
                            'function': 'go_to_about',
                            'main_text': {
                                'colour': '#c0c0c0',
                                'display_text': 'ABOUT'
                            },
                            'sub_text': {
                                'colour': '#a0a0a0',
                                'display_text': 'All about TETR.PY'
                            },
                            'image': 'resources/buttons/about.png',
                            'background': {
                                'style': 'solid',
                                'colour': '#222222',
                            },
                            'border': {
                                'left': (3, '#262626'),
                                'top': (3, '#2a2a2a'),
                                'bottom': (3, '#131313')
                            }
                        },
                    ]
                },
            },      
            'menu_footer': {
                'background': {
                    'style': 'linear_gradient', 
                    'colours': ('#17191d', '#272931')
                },
                'border': {
                    'top': (2, '#343642'),
                },
                'text': {
                    'colour': '#8a8fa0', 
                    'display_text': 'Welcome to TETR.PY!'
                },
            }
        }
        
        self.__init_elements()
        
    def __init_elements(self):
        if 'menu_header' in self.definition:
            self.header_height = 70
            self.menu_header = Header(self.surface.get_rect(), self.header_height, self.definition['menu_header']['text'], self.definition['menu_header']['background'], self.definition['menu_header']['border'])
        if 'menu_footer' in self.definition:
            self.footer_height = 55
            self.menu_footer = Footer(self.surface.get_rect(), self.footer_height, self.definition['menu_footer']['text'], self.definition['menu_footer']['background'], self.definition['menu_footer']['border'])
        if 'menu_body' in self.definition:
            self.menu_body = self.definition['menu_body']
            self.main_body_rect = pygame.Rect(0, self.header_height, self.surface.get_width(), self.surface.get_height() - self.footer_height - self.header_height)
            self.main_body = MainBody(self.main_body_rect.width, self.main_body_rect.height, self.main_body_rect.topleft, self.menu_body)
        
    def draw(self):
        self.main_body.draw(self.surface)
        self.menu_header.draw(self.surface)
        self.menu_footer.draw(self.surface)
        
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
    def __init__(self, container, height, text, background, border):
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

    def render_footer(self):
        if self.background['style'] == 'linear_gradient':
            draw_linear_gradient(self.footer_surface, self.background['colours'][0], self.background['colours'][1], self.footer_surface.get_rect())
        elif self.background['style'] == 'solid':
            draw_solid_colour(self.footer_surface, self.background['colour'], self.footer_surface.get_rect())
            
        draw_border(self.footer_surface, self.border, self.footer_surface.get_rect())
        self.font.draw(self.footer_surface, self.text['display_text'], self.text['colour'], 'left', 20, 0)
        
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
                    button.draw()
        
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
        
        self.image = pygame.image.load(self.definition['image']).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width() * self.definition['scale']), int(self.image.get_height() * self.definition['scale']))
        )
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
        self.sub_font = Font('hun2', 25)
        
        self.y_offset = list_index * (self.height + 20) + 30
        self.start = self.container.width // 4
        
        self.render_button()
        
    def render_button(self):
        draw_solid_colour(self.button_surface, self.definition['background']['colour'], self.rect)
        draw_border(self.button_surface, self.definition['border'], self.rect)
         
        scale = 0.145
        image = pygame.image.load(self.definition['image']).convert_alpha()
        image = pygame.transform.smoothscale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        image_rect = align_bottom_left(self.rect, image.get_width(), image.get_height(), 20, 3)
        self.button_surface.blit(image, image_rect.topleft)
        
        self.main_font.draw(self.button_surface, self.definition['main_text']['display_text'], self.definition['main_text']['colour'], 'left', 250, - self.main_font.font.get_ascent()//2)
        self.sub_font.draw(self.button_surface, self.definition['sub_text']['display_text'], self.definition['sub_text']['colour'], 'left', 250, self.main_font.font.get_ascent()//2 + 10)
    
    def draw(self):
        self.surface.blit(self.button_surface, (self.rect.left + self.start, self.rect.top + self.y_offset))


