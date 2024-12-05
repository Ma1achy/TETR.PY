from render.render_new import StructRender
import pygame
from utils import hex_to_rgb
from render.GUI.font import Font
from render.GUI.buttons.dialog_button import DialogButton

class DialogBox():
    def __init__(self, window, Mouse, RenderStruct:StructRender, title, message, buttons, funcs):
        
        self.window = window
        self.title = title
        self.message = message
        self.buttons = buttons
        self.funcs = funcs
        self.Mouse = Mouse
        self.RenderStruct = RenderStruct
        
        self.width = 500
        self.height = 100
        self.x_padding = 10
        self.y_padding = 7
        self.border_radius = 5    
                   
        self.main_font = Font('hun2', 30)
        
        self.__get_rect_and_surface()
        self.__create_buttons()
        self.primary_button.render()
        self.secondary_button.render()
        self.render()
    
    def __get_rect_and_surface(self):
        self.dialog_rect = pygame.Rect(self.RenderStruct.WINDOW_WIDTH//2 - self.width // 2, self.RenderStruct.WINDOW_HEIGHT//2 - self.height // 2, self.width, self.height)
        self.dialog_surface = pygame.Surface((self.dialog_rect.width, self.dialog_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
    
    def render(self):
        pygame.draw.rect(self.dialog_surface, hex_to_rgb('#fffffffff'), (0, 0, self.width, self.height), border_radius = self.border_radius)
        pygame.draw.rect(self.dialog_surface, hex_to_rgb('#CCCCCC'), self.button_container, border_bottom_left_radius = self.border_radius, border_bottom_right_radius = self.border_radius)
        
        self.main_font.draw(
            self.dialog_surface,
            self.title,
            '#000000',
            'left_top',
            15,
            3,
        )
        
        self.primary_button.draw(self.dialog_surface)
        self.secondary_button.draw(self.dialog_surface)
        
    def draw(self):
        self.window.blit(self.dialog_surface, self.dialog_rect)
         
    def handle_window_resize(self):
        self.dialog_rect.topleft = (self.RenderStruct.WINDOW_WIDTH//2 - self.width // 2, self.RenderStruct.WINDOW_HEIGHT//2 - self.height // 2)
    
    def update(self):
        self.primary_button.update()
        self.secondary_button.update()
        self.render()
        self.draw()
    
    def __create_buttons(self):
        self.button_width, self.button_height = self.dialog_rect.width // 2 - self.x_padding * 1.5, self.dialog_rect.height // 2 - self.y_padding * 2
        self.button_container = pygame.Rect(0, self.dialog_rect.height // 2, self.dialog_rect.width, self.dialog_rect.height // 2)
        
        self.primary_button   = DialogButton(self.Mouse, self.RenderStruct, text = self.buttons[0], function = self.funcs[0], width = self.button_width, height = self.button_height, colour = '#AAAAAA', text_colour = '#000000', style = 'darken', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'left', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius)
        self.secondary_button = DialogButton(self.Mouse, self.RenderStruct, text = self.buttons[1], function = self.funcs[1], width = self.button_width, height = self.button_height, colour = '#1E48FF', text_colour = '#CCCCCC', style = 'lighten', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'right', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius)

