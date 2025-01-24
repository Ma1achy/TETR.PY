import pygame
from render.GUI.font import Font
from render.GUI.menu_elements.nested_element import NestedElement
from render.GUI.buttons.slider_field import SliderField
from render.GUI.buttons.slider_knob import SliderKnob
from render.GUI.buttons.invisible_button import InvisibleButton
from render.GUI.buttons.slider_bar_button import SliderBarButton

from render.GUI.diaglog_box import DialogBox
from render.GUI.menu_elements.text_input import TextInput

class ConfigSlider(NestedElement):
    def __init__(self, button_functions, dialog_resources, Timing, Mouse, Sound, surface, container, definition, y_position, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(parent)
        """
        
        args:
            Timing (Timing): the Timing object
            Mouse (Mouse): the Mouse object
            surface (pygame.Surface): the surface to draw the slider on
            container (pygame.Rect): the container the slider is in
            definition (dict): the definition of the slider
            y_position (int): the y position of the slider
            parent (Object): the parent UI element
        """
        self.button_functions = button_functions
        self.dialog_resources = dialog_resources
        
        self.RENDER_SCALE = RENDER_SCALE
        self.ToolTips = ToolTips
        
        self.Timing = Timing
        self.Mouse = Mouse
        self.Sound = Sound
        
        self.surface = surface
        self.container = container
        
        self.ignore_events = False
         
        self.bar_height = int(7 * self.RENDER_SCALE)
        
        self.definition = definition
        
        if 'flipped' in self.definition:
            self.flipped = self.definition['flipped']
        else:
            self.flipped = False
            
        if 'max_value_to_inf' in self.definition:
            self.max_value_to_inf = self.definition['max_value_to_inf']
        else:
            self.max_value_to_inf = False
        
        self.themeing = self.definition['themeing']
        
        self.left_end_text = self.definition['left_end_text']
        self.right_end_text = self.definition['right_end_text']
        self.end_text_colour = self.themeing['end_text_colour']
        
        self.max_value = self.definition['max_value']
        self.min_value = self.definition['min_value']
        self.value_range = self.max_value - self.min_value
        
        self.end_text_font_size = int(12 * self.RENDER_SCALE) 
        self.end_text_font = Font('hun2', self.end_text_font_size)
        
        self.start_x = int(self.definition['start_x'] * self.RENDER_SCALE) if 'start_x' in self.definition else int(80 * self.RENDER_SCALE)
        self.end_x = int(140 * self.RENDER_SCALE)
        
        self.title_font_size = int(25 * self.RENDER_SCALE)
        self.title_padding = self.title_font_size + int(5 * self.RENDER_SCALE)
        self.x_padding = int(25 * self.RENDER_SCALE)
        self.y_padding = 0
        
        self.x_position = self.x_padding
        self.y_position = self.y_padding + y_position

        self.width = self.container.width - self.x_padding * 2
        self.height = int(50 * self.RENDER_SCALE)
        
        self.title_font = Font('hun2', self.title_font_size)
        self.title_text = self.get_title()
        
        self.tool_tip_definition = {"tooltip": self.definition['tooltip']}
        
        self.value_field_definiton = {
            "unit_font_colour": self.themeing['value_unit_colour'],
            "value_font_colour": self.themeing['value_value_colour'],
            "unit": self.definition['unit'],
            "background_colour": self.themeing['colour'],
            "tooltip": self.definition['tooltip']
        }
        
        self.knob_definition = self.themeing['knob']
        self.knob_definition['tooltip'] = self.definition['tooltip']
            
        self.__get_rect_and_surface()
        
        self.edit_field_value_dialog = DialogBox(
            self.Timing, 
            self.dialog_resources["window"],
            self.Mouse, 
            self.Sound,
            self.dialog_resources["render_struct"],
            title = self.definition["dialog_title"],
            message = self.definition["dialog_message"],
            buttons = ['CANCEL', 'SUBMIT'],
            funcs = [self.button_functions["close_dialog"], lambda: self.submit_value(self.edit_field_value_dialog.TextEntry.get_value())], 
            click_off_dissmiss = True, 
            width = 550, 
            
            TextEntry = TextInput(
                allowed_input = self.definition["text_entry_params"]["allowed_input"],
                no_empty_input = self.definition["text_entry_params"]["no_empty_input"],
                max_chars = self.definition["text_entry_params"]["max_chars"],
                force_caps = self.definition["text_entry_params"]["force_caps"],
                font_colour = '#ffffff',
                cursor_colour = '#ffffff',
                font_type = 'hun2.ttf',
                font_size = 25,
                pygame_events_queue =  self.dialog_resources["pygame_event_queue"],
                function = self.submit_value,
                RENDER_SCALE = self.RENDER_SCALE
            )
        )
     
        self.value_field_function = self.open_edit_field_value_dialog
        
        self.ValueField = SliderField(self.button_functions, self.value_button_rect.width, self.value_button_rect.height, self.value_button_rect, self.value_field_function, self.Mouse, self.Timing, self.Sound, self.slider_surface, self.value_button_rect, self.value_field_definiton, self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
        self.ValueField.min_value = self.min_value
        self.ValueField.max_value = self.max_value
        self.ValueField.max_value_to_inf = self.max_value_to_inf
        
        self.ValueField.value = self.max_value if not self.flipped else self.min_value
        self.Knob = SliderKnob(self.knob_rect.width, self.knob_rect.height, self.knob_rect, None, self.Mouse, self.Timing, self.Sound, self.surface, self.knob_rect, self.knob_definition, self.parent, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips, slider = self)
        
        self.render()
        
        self.slider_bar_button = SliderBarButton(self.slider_bar_rect.width, self.slider_bar_rect.height, self.slider_bar_rect, self.get_click_position, self.Mouse, self.Timing, self.slider_surface, self.slider_bar_rect, self.tool_tip_definition, self, self.RENDER_SCALE, self.ToolTips)
        
        self.title_width = self.title_font.get_width()
        self.title_height = self.title_font.font.get_height()
        
        self.title_rect = pygame.Rect(self.x_padding * 2, self.y_padding, self.title_width + self.x_padding, self.height - self.y_padding * 2)
        
        self.title_invisible_button = InvisibleButton(self.title_rect.width, self.title_rect.height, self.title_rect, None, self.Mouse, self.Timing, self.slider_surface, self.title_rect, self.tool_tip_definition, self, self.RENDER_SCALE, self.ToolTips)
        
    def get_title(self):
        """
        Get the title of the slider
        """
        if 'title' in self.definition:
            self.title = True
            return self.definition['title']
        self.title = False
        
    def get_local_position(self):
        """
        Get the position of the slider relative to the container it is in for collision detection.
        """
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the slider
        """ 
        self.x_padding = int(6 * self.RENDER_SCALE)
        self.value_button_width = int(135 * self.RENDER_SCALE) - self.x_padding * 2
        
        self.y_padding = int(6 * self.RENDER_SCALE)
        self.value_button_height = self.height - self.y_padding * 2
        
        self.knob_width = int(25 * self.RENDER_SCALE)
        self.knob_height = self.value_button_height - self.y_padding
         
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.slider_bar_rect = pygame.Rect(self.start_x, (self.height - self.bar_height) // 2, self.width - self.start_x - self.end_x, self.bar_height)
        self.slider_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.value_button_rect = pygame.Rect(self.slider_bar_rect.right + self.x_padding * 2, self.y_padding, self.value_button_width, self.value_button_height)
        self.knob_rect = pygame.Rect(self.rect.left + self.slider_bar_rect.left, self.rect.top + self.y_padding * 1.5, self.knob_width, self.knob_height)
       
    def render(self):
        """
        Render the slider
        """
        self.render_background()
        self.render_title()
        self.render_slider_bar()
        self.render_end_text()
    
    def render_title(self):
        """
        Render the title of the slider
        """
        if not self.title:
            return
        
        self.title_font.draw(self.slider_surface, self.title_text, self.themeing["title_colour"], 'left', int(15 * self.RENDER_SCALE), 0)
    
    def render_end_text(self):
        """
        Render the end text of the slider
        """
        self.end_text_font.draw(self.slider_surface, self.left_end_text, self.end_text_colour, 'left_bottom', self.start_x, int(5 * self.RENDER_SCALE))
        self.end_text_font.draw(self.slider_surface, self.right_end_text, self.end_text_colour, 'right_bottom', self.end_x, int(5 * self.RENDER_SCALE))
        
    def render_slider_bar(self):
        pygame.draw.rect(self.slider_surface, self.themeing['colour'], self.slider_bar_rect)
        
    def render_background(self):
        """
        Render the background of the slider
        """
        pygame.draw.rect(self.slider_surface, self.themeing['background_colour'], self.slider_surface.get_rect(), border_radius = int(5 * self.RENDER_SCALE))
        pygame.draw.rect(self.slider_surface, self.themeing['colour'], self.value_button_rect, border_radius = int(5 * self.RENDER_SCALE))
             
    def draw(self):   
        self.surface.blit(self.slider_surface, (self.x_position, self.y_position))
        
    def update(self, in_dialog):
        
        self.update_field(in_dialog)
        self.update_slider_bar(in_dialog)
        self.draw()
        self.update_knob(in_dialog)
        self.update_invisible_buttons(in_dialog)
        self.perform_drag()
        
    def value_to_position(self, value):
        """
        Convert the value to a position on the slider
        """
        min_position = self.slider_bar_rect.left + self.knob_rect.width
        max_position = self.slider_bar_rect.right
        length = max_position - min_position
              
        percentage = (value - self.min_value) / self.value_range
        
        if self.flipped:
            position = int(max_position - (length * percentage))
        else:
            min_position = self.slider_bar_rect.left + self.knob_rect.width + 1
            position = int(min_position + (length * percentage))
        
        if position < self.slider_bar_rect.left:
            position = self.slider_bar_rect.left + self.knob_rect.width
            
        elif position > self.slider_bar_rect.right:
            position = self.slider_bar_rect.right
             
        self.Knob.update_position(position)
    
    def position_to_value(self):
        """
        Convert the position of the knob to a value
        """ 
        min_position = self.slider_bar_rect.left + self.knob_rect.width
        max_position = self.slider_bar_rect.right
        length = max_position - min_position
        
        percentage = (self.knob_rect.x - min_position) / length
        
        if self.flipped:
            self.ValueField.value = int(self.max_value - (self.value_range * percentage))
        else:
            self.ValueField.value = int(self.min_value + (self.value_range * percentage))
            
    def get_click_position(self, click_x):
        """
        Get the position of the mouse click along the slider and set the knob to that position
        """
        tl = self.get_screen_position()
        relative_position = click_x - tl[0]
        
        self.update_knob_position(relative_position)
            
    def update_knob_position(self, position):
        """
        Update the position of the knob
        """
        if position - self.Knob.rect.width // 2 < self.slider_bar_rect.left:
            position = self.slider_bar_rect.left + self.Knob.rect.width
     
        elif position > self.slider_bar_rect.right - self.knob_rect.width // 2:
            position = self.slider_bar_rect.right
        else:
            position += self.knob_rect.width // 2 - 1
            
        self.knob_rect.x = position
        self.Knob.shadow_rect.x = position - self.Knob.shadow_radius * 2
        
        self.Knob.update_position(position)
        
    def update_knob(self, in_dialog):
        """
        Update the knob
        """
        self.position_to_value()
        self.Knob.update(in_dialog)
            
    def update_slider_bar(self, in_dialog):
        if self.ignore_events:
            return
        
        self.slider_bar_button.update(in_dialog)
    
    def update_invisible_buttons(self, in_dialog):
        self.title_invisible_button.update(in_dialog)
    
    def update_field(self, in_dialog):
        if self.ValueField.value < self.min_value:
            self.ValueField.value = self.min_value
            
        elif self.ValueField.value > self.max_value:
            self.ValueField.value = self.max_value
                
        self.ValueField.update(in_dialog)
    
    def reset_state(self):
        """
        Reset the state of the slider
        """
        self.ValueField.reset_state()
        self.Knob.reset_state()
        
    def perform_drag(self):
        """
        Check for input events.
        """
        mouse_x, _ = self.Mouse.position
        
        if self.Knob.being_dragged and self.Mouse.slider_interaction_event:
            tl = self.get_screen_position() 
            pos = mouse_x - tl[0]
            self.update_knob_position(pos)
        
    def open_edit_field_value_dialog(self):
        self.button_functions['open_dialog'](self.edit_field_value_dialog)
        self.edit_field_value_dialog.TextEntry.manager.value = str(self.ValueField.value)
        self.edit_field_value_dialog.TextEntry.manager.cursor_pos = len(self.edit_field_value_dialog.TextEntry.manager.value)
        self.edit_field_value_dialog.text_entry_box.focused = True
        self.edit_field_value_dialog.TextEntry.is_focused = True
    
    def submit_value(self, value):
        
        if value < self.min_value:
            value = self.min_value
            
        elif value > self.max_value:
            value = self.max_value
            
        self.value_to_position(value)
        self.ValueField.value = value
        self.ValueField.update_value()
        self.button_functions['close_dialog']()
        self.reset_state()