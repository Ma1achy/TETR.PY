from render.render_new import StructRender
import pygame
from utils import hex_to_rgb
from render.GUI.font import Font
from render.GUI.buttons.dialog_button import DialogButton
from render.GUI.buttons.invisible_button import InvisibleButton
class DialogBox():
    def __init__(self, window, Mouse, RenderStruct:StructRender, title, message, buttons, funcs, click_off_dissmiss):
        
        self.window = window
        self.title = title
        self.message = message
        self.buttons = buttons
        self.funcs = funcs
        self.Mouse = Mouse
        self.RenderStruct = RenderStruct
        
        self.click_off_dissmiss = click_off_dissmiss
        
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
            '#222222',
            'left_top',
            15,
            3,
        )

        if self.click_off_dissmiss:
            self.invisible_button1.draw()
            self.invisible_button2.draw()
            self.invisible_button3.draw()
            self.invisible_button4.draw()
            
        self.primary_button.draw()
        self.secondary_button.draw()
        
    def draw(self):
        self.window.blit(self.dialog_surface, self.dialog_rect)
            
    def update(self):
        self.__update_click_off_buttons()
        self.primary_button.update()
        self.secondary_button.update()
        self.render()
        self.draw()
    
    def __update_click_off_buttons(self):
        if not self.click_off_dissmiss:
            return
        
        self.invisible_button1.update()
        self.invisible_button2.update()
        self.invisible_button3.update()
        self.invisible_button4.update()
            
    def __create_buttons(self):
        self.button_width, self.button_height = self.dialog_rect.width // 2 - self.x_padding * 1.5, self.dialog_rect.height // 2 - self.y_padding * 2
        self.button_container = pygame.Rect(0, self.dialog_rect.height // 2, self.dialog_rect.width, self.dialog_rect.height // 2)
        
        self.__get_click_off_buttons()

        self.primary_button   = DialogButton(self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[0], function = self.funcs[0], width = self.button_width, height = self.button_height, colour = '#AAAAAA', text_colour = '#222222', style = 'darken', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'left', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius)
        self.secondary_button = DialogButton(self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[1], function = self.funcs[1], width = self.button_width, height = self.button_height, colour = '#1E48FF', text_colour = '#CBD5FF', style = 'lighten', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'right', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius)
    
    def __get_click_off_buttons(self):
        if not self.click_off_dissmiss:
            return
        
        self.invisible_button1 = InvisibleButton(self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, self.window.get_rect().top, self.window.get_rect().width, (self.window.get_rect().height - self.height)//2))
        self.invisible_button2 = InvisibleButton(self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, (self.window.get_rect().bottom + self.height)//2, self.window.get_rect().width, (self.window.get_rect().height - self.height)//2))
        
        self.invisible_button3 = InvisibleButton(self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, self.dialog_rect.top, (self.window.get_rect().width - self.dialog_rect.width)//2, self.dialog_rect.height))
        self.invisible_button4 = InvisibleButton(self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.dialog_rect.right, self.dialog_rect.top, (self.window.get_rect().width - self.dialog_rect.width)//2, self.dialog_rect.height))
    
    def handle_window_resize(self):
        self.__resize_dialog_box()
        self.__resize_click_off_buttons()
    
    def __resize_dialog_box(self):
        self.dialog_rect.topleft = (self.RenderStruct.WINDOW_WIDTH//2 - self.width // 2, self.RenderStruct.WINDOW_HEIGHT//2 - self.height // 2)
        self.primary_button.offset = (self.dialog_rect.left, self.dialog_rect.top)
        self.secondary_button.offset = (self.dialog_rect.left, self.dialog_rect.top)
        
    def __resize_click_off_buttons(self):
        self.__get_click_off_buttons()
        
        