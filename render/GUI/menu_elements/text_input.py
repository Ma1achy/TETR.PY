import re
from utils import hex_to_rgb
import os
import pygame
from app.input.keyboard.text_input_manager import TextInputManager
from render.GUI.text_input_visualiser import TextInputVisualizer
from app.core.sound.sfx import SFX

class TextInput():
    def __init__(self, allowed_input = 'str', no_empty_input = True, max_chars = 32, force_caps = True, font_colour = '#000000', cursor_colour = '#000000', font_type = 'hun2.ttf', font_size = 30, pygame_events_queue = [], function = None, RENDER_SCALE = 1, Sound = None):
        """
        Utility class to quickly create a text input field that only accepts certain input and passes the input to a function when the user presses enter.
        """
        self.RENDER_SCALE = RENDER_SCALE
        
        pygame.key.set_repeat(500, 33)
        
        self.function = function
        
        self.max_chars = max_chars
        self.force_caps = force_caps
        
        self.font_colour = hex_to_rgb(font_colour)
        self.cursor_colour = hex_to_rgb(cursor_colour)
        
        self.font_type = font_type
        
        self.font_size = int(font_size * self.RENDER_SCALE)
        
        self.base_path = 'resources/font/'
        
        self.font_path = os.path.join(self.base_path, self.font_type)
        
        self.font = pygame.font.Font(self.font_path, self.font_size)

        self.allowed_input = allowed_input
        
        self.pygame_events_queue = pygame_events_queue
        self.events_to_remove = []
        self.events = []
        
        self.focused = True
        self.no_empty_input = no_empty_input
        
        self.Sound = Sound
        
        match self.allowed_input:
            case 'str':
                self.validator = lambda input: len(input) <= self.max_chars and re.match(r'^[A-Za-z0-9-_\/\\(),<>?!@#$%&*+=\[\].:"\' ]*$', input) is not None
            case 'str_no_space':
                self.validator = lambda input: len(input) <= self.max_chars and re.match(r'^[A-Za-z0-9-_\/\\(),<>?!@#$%&*+=\[\].:"\']*$', input) is not None
            case 'alphanumeric':
                self.validator = lambda input: len(input) <= self.max_chars and re.match(r'^[A-Z0-9-_]*$', input.upper()) is not None
            case 'int':
                self.validator = lambda input: len(input) <= self.max_chars and re.match(r'^\d*$', input) is not None
            case 'float':
                self.validator = lambda input: len(input) <= self.max_chars and re.match(r'^[0-9]*\.?[0-9]*$', input) is not None
            case _:
                self.validator = lambda input: len(input) <= self.max_chars and re.match(r'^[A-Z0-9-_]*$', input.upper()) is not None
          
    def init(self, surface):
        """
        Initialise the text input field
        """
        self.surface = surface  
        self.manager = TextInputManager(validator = self.validator, force_caps = self.force_caps)
        self.textinput = TextInputVisualizer(self.manager, self.font, font_color = self.font_colour, cursor_color = self.cursor_colour)
        
        self.textinput.cursor_blink_interval = 500
        self.textinput.cursor_width = int(2 * self.RENDER_SCALE)
        
    def update(self):
        """
        Update the text input field
        """
        if self.focused:
            self.__handle_events()
        
        if not self.focused:
            self.textinput.cursor_visible = False
            
        self.surface.blit(self.textinput.surface, (int(10 * self.RENDER_SCALE), int(10 * self.RENDER_SCALE)))
        
    def __handle_events(self):
        """
        Handle the events for the text input field
        """
        self.dequeue_events()
        self.textinput.update(self.events)
        
        for event in self.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.call_function()
                self.Sound.sfx_queue.append(SFX.MenuHit1)
                
        self.events = []
    
    def get_value(self):
        """
        Get the value of the text within the input field
        """
        value = self.manager.value
        
        if value == '' or value is None:
            return None
        
        match self.allowed_input:
            case 'int':
                return int(value)
            case 'float':
                return float(value)
            case _:
                return value

    def dequeue_events(self):
        """
        Dequeue the events from the pygame events queue
        """
        for event in self.pygame_events_queue:
            self.events.append(event)
            self.events_to_remove.append(event)
        
        for event in self.events_to_remove:
            self.pygame_events_queue.remove(event)
        
        self.events_to_remove = []
    
    def call_function(self):
        """
        Call the function with the value of the text input field
        """
        if self.function is None:
            return
        
        value = self.get_value()
        
        if self.no_empty_input:
            if value == '' or value is None:
                return
        
        self.function(value)