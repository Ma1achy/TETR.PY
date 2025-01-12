from render.render import StructRender
import pygame
from utils import hex_to_rgb, smoothstep, TransformSurface, align_left_edge, align_right_edge, align_centre
from render.GUI.font import Font
from render.GUI.buttons.dialog_button import DialogButton
from render.GUI.buttons.dialog_click_off_button import DialogClickOffButton
import re
from render.GUI.menu_elements.nested_element import NestedElement
import math

from render.GUI.buttons.button import Button
from app.input.mouse.mouse import MouseEvents

class DialogBox(NestedElement):
    def __init__(self, Timing, window, Mouse, RenderStruct:StructRender, title, message, buttons, funcs, click_off_dissmiss, width, TextEntry = None):
        super().__init__(parent = None)
        """
        A dialog box that can be used for any purpose
        
        args:
            Timing (Timing): the Timing object
            window (pygame.Surface): the window to draw the dialog box on
            Mouse (Mouse): the Mouse object
            RenderStruct (RenderStruct): the RenderStruct object
            title (str): the title of the dialog box
            message (str): the message of the dialog box
            buttons (list): the buttons to display on the dialog box
            funcs (list): the functions to call when the buttons are pressed
            click_off_dissmiss (bool): whether the dialog box can be dismissed by clicking off it
            width (int): the width of the dialog box
            TextEntry (TextEntry): the text entry box to display on the dialog box
        """
        self.Timing = Timing
        self.window = window
            
        self.title = title
        self.message = message
        
        self.buttons = buttons
        self.num_buttons = len(buttons)

        self.primary_button = None
        self.secondary_button = None
        self.text_entry_box = None
        
        self.TextEntry = TextEntry
        
        self.funcs = funcs
        self.Mouse = Mouse
        self.RenderStruct = RenderStruct
        self.RENDER_SCALE = self.RenderStruct.RENDER_SCALE
        
        self.click_off_dissmiss = click_off_dissmiss
        
        self.main_font = Font('hun2', int(30 * self.RENDER_SCALE))
        self.sub_font = Font('hun2', int(20 * self.RENDER_SCALE))
        
        self.width = int(width * self.RENDER_SCALE)
        self.button_height = int(50 * self.RENDER_SCALE)
        self.height = 0 
        self.text_entry_height = int(40 * self.RENDER_SCALE)
        
        self.x_padding = int(10 * self.RENDER_SCALE)
        self.y_padding = int(7 * self.RENDER_SCALE)
        self.border_radius = int(5 * self.RENDER_SCALE)  
        
        self.closed = False
        self.alpha = 0
        self.do_animate_appear = True
        self.do_animate_disappear = False
        self.timer = 0
        self.animation_length = 0.35
        
        self.is_validating_size = False
        self.__wrap_text(self.message, self.sub_font.font, self.width - 2 * self.x_padding)
        self.__get_height()
               
        self.__get_rect_and_surface()
        self.__create_buttons()
        self.__create_text_entry()
        
        if self.primary_button is not None:
            self.primary_button.render()
        
        if self.secondary_button is not None:
            self.secondary_button.render()
        
        self.render()

    def get_local_position(self):
        """
        Get the local position of the dialog box
        """
        return self.dialog_rect.topleft
    
    def __validate_size(self):
        """
        Validate the size of the dialog box and adjust it if necessary when wrapping text
        """
        self.is_validating_size = True
        self.height = 0
        self.width += int(400 * self.RENDER_SCALE)
        self.__wrap_text(self.message, self.sub_font.font, self.width - 2 * self.x_padding)
        self.__get_height()
        self.is_validating_size = False
        
    def __strip_tags(self, text):
        """
        Strip colour tags from the text
        
        args:
            text (str): The text to strip the tags from
        """
        tag_pattern = r"\[colour=#[0-9A-Fa-f]{6}\]|\[\/colour\]"
        return re.sub(tag_pattern, "", text)

    def __wrap_text(self, text, font, max_width):
        """	
        Wrap text to fit inside a given width
        
        args:
            text (str): The text to wrap
            font (pygame.font.Font): The font to use
            max_width (int): The maximum width of the text
        """
        if text is None:
            return
        
        words = re.split(r"(\s+)", text)
        lines = []
        current_line = ""

        for word in words:
            stripped_word = self.__strip_tags(current_line + word)
            
            if font.size(stripped_word.strip())[0] > max_width:
                
                if font.size(word.strip())[0] > max_width:
                    
                    while font.size(word.strip())[0] > max_width:  # Split the word if it's too long
                        for i in range(1, len(word) + 1):
                            if font.size(word[:i].strip())[0] > max_width - font.size(current_line.strip())[0]:
            
                                lines.append(current_line.strip() + word[:i-1])
                                word = word[i-1:]
                                current_line = ""
                                break
                            
                    current_line += word
                else:
                    lines.append(current_line.strip())   # Add the current line to lines and start a new line with the word
                    current_line = word
            else:
                current_line += word

        if current_line:
            lines.append(current_line.strip())

        return lines

    def __get_height(self):
        """
        Get the height of the dialog box
        """
        self.height += int(50 * self.RENDER_SCALE)
        
        if self.title:
            self.height += int(50 * self.RENDER_SCALE)
        
        if self.message:
            wrapped_message = []
            for paragraph in self.message.split('\n'):
                wrapped_message.extend(self.__wrap_text(paragraph, self.sub_font.font, self.width - 2 * self.x_padding))

            self.wrapped_message = wrapped_message
            self.height += len(wrapped_message) * self.sub_font.font.get_height()
            
        if self.TextEntry is not None:
            self.height += int(50 * self.RENDER_SCALE)
                
        if self.height > self.RenderStruct.RENDER_HEIGHT - int(10 * self.RENDER_SCALE):
            if not self.is_validating_size:
                self.__validate_size()
          
    def __get_rect_and_surface(self):
        """
        Get the rect and surface for the dialog box
        """
        self.dialog_rect = pygame.Rect(self.RenderStruct.RENDER_WIDTH // 2 - self.width // 2, self.RenderStruct.RENDER_HEIGHT // 2 - self.height // 2, self.width, self.height)
        self.dialog_surface = pygame.Surface((self.dialog_rect.width, self.dialog_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
    
    def render(self):
        """
        Render the dialog box
        """
        pygame.draw.rect(self.dialog_surface, hex_to_rgb('#fffffffff'), (0, 0, self.width, self.height), border_radius = self.border_radius)
        pygame.draw.rect(self.dialog_surface, hex_to_rgb('#CCCCCC'), self.button_container, border_bottom_left_radius = self.border_radius, border_bottom_right_radius = self.border_radius)
        
        if self.title:
            self.main_font.draw(
                self.dialog_surface,
                self.title,
                '#222222',
                'left_top',
                int(10 * self.RENDER_SCALE),
                int(3 * self.RENDER_SCALE),
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
                            self.y_padding * 5.5 + i * self.sub_font.font.get_height(),
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
        """
        Draw the dialog box
        """
        if self.do_animate_appear or self.do_animate_disappear:
            return
        
        self.window.blit(self.dialog_surface, self.dialog_rect)
            
    def update(self):
        """
        Update the dialog box
        """
        self.__update_click_off_buttons()
        if self.primary_button is not None:
            self.primary_button.update()
        
        if self.secondary_button is not None:
            self.secondary_button.update()
            
        if self.text_entry_box is not None:
            self.text_entry_box.update()
 
        self.animate_appear()
        self.animate_disappear()
        self.draw()
    
    def __update_click_off_buttons(self):
        """
        Update the click off buttons
        """
        if not self.click_off_dissmiss:
            return
        
        self.invisible_button1.update()
        self.invisible_button2.update()
        self.invisible_button3.update()
        self.invisible_button4.update()
            
    def __create_buttons(self):
        """
        Create the buttons for the dialog box
        """
        if self.num_buttons == 1:
            self.button_width = self.dialog_rect.width - self.x_padding * 2
            self.button_height = self.button_height - self.y_padding * 2
        else:
            self.button_width, self.button_height = self.dialog_rect.width // 2 - self.x_padding * 1.5, self.button_height - self.y_padding * 2
            
        self.button_container = pygame.Rect(0, self.dialog_rect.height - self.button_height - self.y_padding * 2, self.dialog_rect.width, self.button_height + self.y_padding * 2)
        
        self.__get_click_off_buttons()
         
        if self.num_buttons == 1:
            self.secondary_button = DialogButton(self.Timing, self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[0], function = self.funcs[0], width = self.button_width, height = self.button_height, colour = '#1E48FF', text_colour = '#CBD5FF', style = 'lighten', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'right', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius, parent = self, RENDER_SCALE = self.RENDER_SCALE)
        else:
            self.primary_button   = DialogButton(self.Timing, self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[0], function = self.funcs[0], width = self.button_width, height = self.button_height, colour = '#AAAAAA', text_colour = '#222222', style = 'darken', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'left', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius, parent = self, RENDER_SCALE = self.RENDER_SCALE)
            self.secondary_button = DialogButton(self.Timing, self.dialog_surface, self.Mouse, self.RenderStruct, text = self.buttons[1], function = self.funcs[1], width = self.button_width, height = self.button_height, colour = '#1E48FF', text_colour = '#CBD5FF', style = 'lighten', container = self.button_container, dialog_rect = self.dialog_rect, alignment = 'right', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius, parent = self, RENDER_SCALE = self.RENDER_SCALE)
    
    def __create_text_entry(self):
        """
        Create the text entry box for the dialog box
        """
        if self.TextEntry is None:
            return
        
        function = None
        self.text_entry_container = pygame.Rect(self.button_container.left, self.button_container.top - self.text_entry_height - self.y_padding * 2, self.width, self.text_entry_height)
        self.text_entry_box = DialogTextEntryBox(self.Timing, self.dialog_surface, self.Mouse, self.RenderStruct, function = function, width = self.width - self.x_padding * 2, height = self.text_entry_height, colour = '#222222', text_colour = '#eeeeee', style = None, container = self.text_entry_container, dialog_rect = self.dialog_rect, alignment = 'right', padding = (self.x_padding, self.y_padding), border_radius = self.border_radius, parent = self, TextEntry = self.TextEntry)
        
    def __get_click_off_buttons(self):
        """
        Get the click off buttons for the dialog box
        """
        if not self.click_off_dissmiss:
            return
        
        self.invisible_button1 = DialogClickOffButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, self.window.get_rect().top, self.window.get_rect().width, (self.window.get_rect().height - self.height)//2), parent = None, RENDER_SCALE = 1)
        self.invisible_button2 = DialogClickOffButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, (self.window.get_rect().bottom + self.height)//2, self.window.get_rect().width, (self.window.get_rect().height - self.height)//2), parent = None, RENDER_SCALE = 1)
        self.invisible_button3 = DialogClickOffButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.window.get_rect().left, self.dialog_rect.top, (self.window.get_rect().width - self.dialog_rect.width)//2, self.dialog_rect.height), parent = None, RENDER_SCALE = 1)
        self.invisible_button4 = DialogClickOffButton(self.Timing, self.window, self.Mouse, function = self.funcs[0], container = pygame.Rect(self.dialog_rect.right, self.dialog_rect.top, (self.window.get_rect().width - self.dialog_rect.width)//2, self.dialog_rect.height), parent = None, RENDER_SCALE = 1)
    
    def handle_window_resize(self):
        """
        Handle the window resize
        """
        self.__resize_dialog_box()
        self.__resize_click_off_buttons()
    
    def __resize_dialog_box(self):
        """
        Resize the dialog box
        """
        self.dialog_rect.topleft = (self.RenderStruct.RENDER_WIDTH // 2 - self.width // 2, self.RenderStruct.RENDER_HEIGHT // 2 - self.height // 2)
        
        if self.primary_button is not None:
            self.primary_button.offset = (self.dialog_rect.left, self.dialog_rect.top)
        
        if self.secondary_button is not None:
            self.secondary_button.offset = (self.dialog_rect.left, self.dialog_rect.top)
        
    def __resize_click_off_buttons(self):
        """
        Resize the click off buttons
        """
        self.__get_click_off_buttons()
    
    def reset_state(self):
        """
        Reset the state of the dialog box
        """
        if self.primary_button is not None:
            self.primary_button.reset_state()
        
        if self.secondary_button is not None:
            self.secondary_button.reset_state()
        
        if self.click_off_dissmiss:
            self.invisible_button1.reset_state()
            self.invisible_button2.reset_state()
            self.invisible_button3.reset_state()
            self.invisible_button4.reset_state()
        
        if self.text_entry_box is not None:
            self.text_entry_box.reset_state()
    
    def animate_appear(self):
        """
        Animate the dialog box appearing
        """
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

        self.animation_surface = TransformSurface(self.dialog_surface, smoothstep(self.timer / self.animation_length), 0, pygame.Vector2(self.dialog_rect.width // 2, self.dialog_rect.height // 2), pygame.Vector2(self.RenderStruct.RENDER_WIDTH // 2, self.RenderStruct.RENDER_HEIGHT // 2), pygame.Vector2(0, 0))
        self.window.blit(self.animation_surface[0], self.animation_surface[1].topleft)
    
    def animate_disappear(self):
        """
        Animate the dialog box disappearing
        """
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
        
        self.animation_surface = TransformSurface(self.dialog_surface, max(0, 1 - smoothstep(self.timer / self.animation_length)), 0, pygame.Vector2(self.dialog_rect.width // 2, self.dialog_rect.height // 2), pygame.Vector2(self.RenderStruct.RENDER_WIDTH // 2, self.RenderStruct.RENDER_HEIGHT // 2), pygame.Vector2(0, 0))
        self.window.blit(self.animation_surface[0], self.animation_surface[1].topleft)
            
    def close(self):
        """
        Close the dialog box
        """
        self.do_animate_disappear = True
        self.timer = 0

class DialogTextEntryBox(Button):
    def __init__(self, Timing, surface, Mouse, RenderStruct, function, width, height, colour, text_colour, style, container, dialog_rect, alignment, padding, border_radius, parent, TextEntry):
        super().__init__(Timing, surface, Mouse, function, container, width, height, style = None, maintain_alpha = False, parent = parent)
        
        self.RenderStruct = RenderStruct
        self.RENDER_SCALE = self.RenderStruct.RENDER_SCALE
        self.y_position = self.container.top + int(padding[1] * self.RENDER_SCALE)
     
        self.text_colour = text_colour
        self.colour = colour
        self.style = style
        self.alignment = alignment
        self.border_radius = border_radius
        self.x_padding, self.y_padding = int(padding[0] * self.RENDER_SCALE), int(padding[1] * self.RENDER_SCALE)
        self.dialog_rect = dialog_rect
        
        self.__get_rect_and_surface()
        self.render()
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))    
        self.focused = False
        
        self.TextEntry = TextEntry
        self.TextEntry.init(self.button_surface)
    
    def render(self):
        """
        Render the text entry box
        """
        pygame.draw.rect(self.button_surface, hex_to_rgb(self.colour), (0, 0, self.width, self.height), border_radius = self.border_radius)
       
    def __get_rect_and_surface(self):
        """
        Get the rect and surface for the text entry box
        """
        self.__get_alignment(self.alignment)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA | pygame.HWSURFACE)
    
    def __get_alignment(self, alignment):
        """
        Align the text entry box within the container
        """
        if alignment == 'left':
            self.rect = align_left_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        elif alignment == 'right':
            self.rect = align_right_edge(self.container, self.width, self.height, self.x_padding, self.y_padding)
        else:
            self.rect = align_centre(self.container, self.width, self.height, self.x_padding, self.y_padding)
    
    def check_events(self):
        """
        Check the events for the text entry box
        """
        events_to_remove = []
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button is MouseEvents.SCROLLWHEEL:
                    return
                
                event_x, event_y = info['pos']
                mouse_x, mouse_y = self.Mouse.position

                if button is MouseEvents.MOUSEBUTTON1 and info['down'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button is MouseEvents.MOUSEBUTTON1 and info['up'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)) and self.state == 'pressed':
                    events_to_remove.append(event)
                    self.start_click()
                
                if button is MouseEvents.MOUSEBUTTON1 and info['down'] and not self.collision_rect.collidepoint((event_x, event_y)) and not self.collision_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = None
                    self.focused = False
                    
                if button is MouseEvents.MOUSEBUTTON1 and info['up'] and not self.collision_rect.collidepoint((event_x, event_y)) and not self.collision_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = None
                    self.focused = False
        
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
            
    def click(self):
        """
        Click the text entry box
        """
        super().click()
        self.focused = True
        
    def update(self):
        """
        Update the text entry box
        """
        self.__update_text_entry()
        super().update()
    
    def __update_text_entry(self):
        """
        Update the text entry
        """
        self.__draw_background()
        
        self.TextEntry.focused = self.focused
        self.TextEntry.update()
        
    def __draw_background(self):
        """
        Draw the background of the text entry box
        """
        if self.focused:
            pygame.draw.rect(self.button_surface, hex_to_rgb(self.colour), (0, 0, self.width, self.height), border_radius = self.border_radius)
            pygame.draw.rect(self.button_surface, hex_to_rgb('#E59700'), (0, 0, self.width, self.height), width = math.ceil(3 * self.RENDER_SCALE), border_radius = self.border_radius) 
        else:
            pygame.draw.rect(self.button_surface, hex_to_rgb(self.colour), (0, 0, self.width, self.height), border_radius = self.border_radius)          
    
    def reset_state(self):
        """
        Reset the state of the text entry box
        """
        self.focused = False
        super().reset_state()
           