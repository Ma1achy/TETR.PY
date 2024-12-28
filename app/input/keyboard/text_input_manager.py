from typing import List, Callable
import pygame
import pygame.locals as pl
"""
Couldn't be bothered to write my own text input manager, so I used this one instead as its pretty good:

Credit: Silas Gyger, silasgyger@gmail.com 
https://github.com/Nearoo/pygame-text-input
"""

class TextInputManager:
    '''
    Keeps track of text inputted, cursor position, etc.
    Pass a validator function returning if a string is valid,
    and the string will only be updated if the validator function
    returns true. 

    For example, limit input to 5 characters:
    ```
    limit_5 = lambda x: len(x) <= 5
    manager = TextInputManager(validator=limit_5)
    ```
    
    :param initial: The initial string
    :param validator: A function string -> bool defining valid input
    '''

    def __init__(self,
                initial = "",
                validator: Callable[[str], bool] = lambda x: True,
                force_caps: bool = False): 
        
        self.left = initial # string to the left of the cursor
        self.right = "" # string to the right of the cursor
        self.validator = validator
        self.force_caps = force_caps
        
    @property
    def value(self):
        """ Get / set the value currently inputted. Doesn't change cursor position if possible."""
        return self.left + self.right
    
    @value.setter
    def value(self, value):
        cursor_pos = self.cursor_pos
        self.left = value[:cursor_pos]
        self.right = value[cursor_pos:]
    
    @property
    def cursor_pos(self):
        """ Get / set the position of the cursor. Will clamp to [0, length of input]. """
        return len(self.left)

    @cursor_pos.setter
    def cursor_pos(self, value):
        complete = self.value
        self.left = complete[:value]
        self.right = complete[value:]
    
    def update(self, events: List[pygame.event.Event]):
        """
        Update the interal state with fresh pygame events.
        Call this every frame with all events returned by `pygame.event.get()`.
        """
        for event in events:
            if event.type == pl.KEYDOWN:
                v_before = self.value
                c_before = self.cursor_pos
                self._process_keydown(event)
                if not self.validator(self.value):
                    self.value = v_before
                    self.cursor_pos = c_before
        
        if self.force_caps:
            self.value = self.value.upper()

    def _process_keydown(self, ev):
        attrname = f"_process_{pygame.key.name(ev.key)}"
        if hasattr(self, attrname):
            getattr(self, attrname)()
        else:
            self._process_other(ev)

    def _process_delete(self):
        self.right = self.right[1:]
    
    def _process_backspace(self):
        self.left = self.left[:-1]
    
    def _process_right(self):
        self.cursor_pos += 1
    
    def _process_left(self):
        self.cursor_pos -= 1

    def _process_end(self):
        self.cursor_pos = len(self.value)
    
    def _process_home(self):
        self.cursor_pos = 0
    
    def _process_return(self):
        pass

    def _process_other(self, event):
        self.left += event.unicode