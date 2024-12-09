from render.render_new import StructRender
import pygame
from utils import hex_to_rgb, smoothstep, TransformSurface
from render.GUI.font import Font
from render.GUI.buttons.dialog_button import DialogButton
from render.GUI.buttons.invisible_button import InvisibleButton
import re

class DialogBox():
    def __init__(self, Timing, window, Mouse, RenderStruct:StructRender, title, message, buttons, funcs, click_off_dissmiss, width):
        
        self.Timing = Timing
        self.window = window
        self.title = title
        self.message = message
        self.buttons = buttons
        self.num_buttons = len(buttons)

        self.primary_button = None
        self.secondary_button = None
        
        self.funcs = funcs
        self.Mouse = Mouse
        self.RenderStruct = RenderStruct
        
        self.click_off_dissmiss = click_off_dissmiss
        
        self.main_font = Font('hun2', 30)
        self.sub_font = Font('hun2', 25)
        
        self.width = width
        self.height = 50
        
        self.x_padding = 10
        self.y_padding = 7
        self.border_radius = 5   
        
        self.closed = False
        self.alpha = 0
        self.do_animate_appear = True
        self.do_animate_disappear = False
        self.timer = 0
        self.animation_length = 0.35
        
        self.__wrap_text(self.message, self.sub_font.font, self.width - 2 * self.x_padding)
        self.__get_height()
                    
        self.__get_rect_and_surface()
        self.__create_buttons()
        
        if self.primary_button is not None:
            self.primary_button.render()
        
        if self.secondary_button is not None:
            self.secondary_button.render()
        
        self.render()

    def __strip_tags(self, text):
        tag_pattern = r"\[colour=#[0-9A-Fa-f]{6}\]|\[\/colour\]"
        return re.sub(tag_pattern, "", text)

    def __wrap_text(self, text, font, max_width):
        if text is None:
            return
        
        words = re.split(r"(\s+)", text)
        lines = []
        current_line = ""

        for word in words:
            stripped_word = self.__strip_tags(current_line + word)
            if font.size(stripped_word.strip())[0] > max_width:
                if font.size(word.strip())[0] > max_width:
                    # Split the word if it's too long
                    while font.size(word.strip())[0] > max_width:
                        for i in range(1, len(word) + 1):
                            if font.size(word[:i].strip())[0] > max_width - font.size(current_line.strip())[0]:
            
                                lines.append(current_line.strip() + word[:i-1])
                                word = word[i-1:]
                                current_line = ""
                                break
                    current_line += word
                else:
                    # Add the current line to lines and start a new line with the word
                    lines.append(current_line.strip())
                    current_line = word
            else:
                current_line += word

        if current_line:
            lines.append(current_line.strip())

        return lines

    def __get_height(self):
        if self.title:
            self.height += 50

        if self.message:
            wrapped_message = []
            for paragraph in self.message.split('\n'):
                wrapped_message.extend(self.__wrap_text(paragraph, self.sub_font.font, self.width - 2 * self.x_padding))

            self.wrapped_message = wrapped_message
            self.height += len(wrapped_message) * self.sub_font.font.get_height()
          
    def __get_rect_and_surface(self):
        self.dialog_rect = pygame.Rect(self.RenderStruct.WINDOW_WIDTH//2 - self.width // 2, self.RenderStruct.WINDOW_HEIGHT//2 - self.height // 2, self.width, self.height)
        self.dialog_surface = pygame.Surface((self.dialog_rect.width, self.dialog_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
    
    def render(self):
        pygame.draw.rect(self.dialog_surface, hex_to_rgb('#fffffffff'), (0, 0, self.width, self.height), border_radius = self.border_radius)
        pygame.draw.rect(self.dialog_surface, hex_to_rgb('#CCCCCC'), self.button_container, border_bottom_left_radius = self.border_radius, border_bottom_right_radius = self.border_radius)
        
        if self.title:
            self.main_font.draw(
                self.dialog_surface,
                self.title,
                '#222222',
                'left_top',
                10,
                3,
            )
        
        if self.message:
            tag_pattern = r"(\[colour=#[0-9A-Fa-f]{6}\]|\[\/colour\])"
            default_colour = "#555555"
            current_colour = default_colour

            for i, line in enumerate(self.wrapped_message):
                segments = re.split(tag_pattern, line)
                x_offset = self.x_padding

                for segment in segments:
                    if segment.startswith("[colour="):
                        current_colour = segment[8:-1]
                    elif segment == "[/colour]":
                        current_colour = default_colour 
                    else:
                        self.sub_font.draw(
                            self.dialog_surface,
                            segment,
                            current_colour,
                            'left_top',
                            x_offset,
                            self.y_padding * 5.25 + i * self.sub_font.font.get_height(),
                        )
                        x_offset += self.sub_font.font.size(segment)[0]

        if self.click_off_dissmiss:
            self.invisible_button1.draw()
            self.invisible_button2.draw()
            self.invisible_button3.draw()
            self.invisible_button4.draw()

        if self.primary_button is not None:
            self.primary_button.draw()
        
        if self.secondary_button is not None:
            self.secondary_button.draw()
        
    def draw(self):
        if self.do_animate_appear or self.do_animate_disappear:
            return
        
        self.window.blit(self.dialog_surface, self.dialog_rect)
            
    def update(self):
        self.__update_click_off_buttons()
        if self.primary_button is not None:
            self.primary_button.update()
        
        if self.secondary_button is not None:
            self.secondary_button.update()
 
        self.animate_appear()
        self.animate_disappear()
        self.draw()
    
    def __update_click_off_buttons(self):
        if not self.click_off_dissmiss:
            return
        
        self.invisible_button1.update()
        self.invisible_button2.update()
        self.invisible_button3.update()
        self.invisible_button4.update()
            
    def __create_buttons(self):
        button_height = 50
        
        if self.num_buttons == 1:
            self.button_width = self.dialog_rect.width - self.x_padding * 2
            self.button_height = button_height - self.y_padding * 2
            self.button_container = pygame.Rect(0, self.dialog_rect.height - button_height, self.dialog_rect.width, button_height)
        else:
            self.button_width, self.button_height = self.dialog_rect.width // 2 - self.x_padding * 1.5, button_height - self.y_padding * 2
            self.button_container = pygame.Rect(0, self.dialog_rect.height - button_height, self.dialog_rect.width, button_height)
        
        self.__get_click_off_buttons()
         
        if self.num_buttons == 1:
            self.secondary_button = DialogButton(self.Timing, self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[0], function = self.funcs[0], width = self.button_width, height = self.button_height, colour = '#1E48FF', text_colour = '#CBD5FF', style = 'lighten', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'right', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius)
        else:
            self.primary_button   = DialogButton(self.Timing, self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[0], function = self.funcs[0], width = self.button_width, height = self.button_height, colour = '#AAAAAA', text_colour = '#222222', style = 'darken', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'left', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius)
            self.secondary_button = DialogButton(self.Timing, self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[1], function = self.funcs[1], width = self.button_width, height = self.button_height, colour = '#1E48FF', text_colour = '#CBD5FF', style = 'lighten', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'right', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius)
    
    def __get_click_off_buttons(self):
        if not self.click_off_dissmiss:
            return
        
        self.invisible_button1 = InvisibleButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, self.window.get_rect().top, self.window.get_rect().width, (self.window.get_rect().height - self.height)//2))
        self.invisible_button2 = InvisibleButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, (self.window.get_rect().bottom + self.height)//2, self.window.get_rect().width, (self.window.get_rect().height - self.height)//2))
        self.Timing, 
        self.invisible_button3 = InvisibleButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, self.dialog_rect.top, (self.window.get_rect().width - self.dialog_rect.width)//2, self.dialog_rect.height))
        self.invisible_button4 = InvisibleButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.dialog_rect.right, self.dialog_rect.top, (self.window.get_rect().width - self.dialog_rect.width)//2, self.dialog_rect.height))
    
    def handle_window_resize(self):
        self.__resize_dialog_box()
        self.__resize_click_off_buttons()
    
    def __resize_dialog_box(self):
        self.dialog_rect.topleft = (self.RenderStruct.WINDOW_WIDTH//2 - self.width // 2, self.RenderStruct.WINDOW_HEIGHT//2 - self.height // 2)
        self.primary_button.offset = (self.dialog_rect.left, self.dialog_rect.top)
        self.secondary_button.offset = (self.dialog_rect.left, self.dialog_rect.top)
        
    def __resize_click_off_buttons(self):
        self.__get_click_off_buttons()
    
    def reset_buttons(self):
        if self.primary_button is not None:
            self.primary_button.reset_state()
        
        if self.secondary_button is not None:
            self.secondary_button.reset_state()
        
        if self.click_off_dissmiss:
            self.invisible_button1.reset_state()
            self.invisible_button2.reset_state()
            self.invisible_button3.reset_state()
            self.invisible_button4.reset_state()
    
    def animate_appear(self):
        if not self.do_animate_appear:
            return
        
        if self.timer >= self.animation_length:
            self.timer = self.animation_length
            self.do_animate_appear = False
            self.timer = 0
            return
            
        self.timer += self.Timing.frame_delta_time
        self.alpha = min(255, smoothstep(self.timer / self.animation_length) * 255)
        self.dialog_surface.set_alpha(self.alpha)

        self.animation_surface = TransformSurface(self.dialog_surface, smoothstep(self.timer / self.animation_length), 0, pygame.Vector2(self.dialog_rect.width//2, self.dialog_rect.height//2), pygame.Vector2(self.RenderStruct.WINDOW_WIDTH//2, self.RenderStruct.WINDOW_HEIGHT//2), pygame.Vector2(0, 0))
        self.window.blit(self.animation_surface[0], self.animation_surface[1].topleft)
    
    def animate_disappear(self):
     
        if not self.do_animate_disappear:
            return
    
        if self.timer >= self.animation_length:
            self.timer = self.animation_length
            self.do_animate_disappear = False
            self.closed = True
            return
        
        self.timer += self.Timing.frame_delta_time
        self.alpha = max(0, 255 - smoothstep(self.timer / self.animation_length) * 255)
        self.dialog_surface.set_alpha(self.alpha)
        
        self.animation_surface = TransformSurface(self.dialog_surface, max(0, 1 - smoothstep(self.timer / self.animation_length)), 0, pygame.Vector2(self.dialog_rect.width//2, self.dialog_rect.height//2), pygame.Vector2(self.RenderStruct.WINDOW_WIDTH//2, self.RenderStruct.WINDOW_HEIGHT//2), pygame.Vector2(0, 0))
        self.window.blit(self.animation_surface[0], self.animation_surface[1].topleft)
            
    def close(self):
        self.do_animate_disappear = True
        self.timer = 0