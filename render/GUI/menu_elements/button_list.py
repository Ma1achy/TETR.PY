import pygame
from render.GUI.font import Font
from render.GUI.menu_elements.nested_element import NestedElement
from render.GUI.buttons.button_list_buttons import ButtonListButtons
from render.GUI.buttons.invisible_button import InvisibleButton

class ButtonList(NestedElement):
    def __init__(self, button_functions, Timing, Mouse, Sound, surface, container, definition, y_position, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(parent)
        """
        A list of buttons where only one can be active at a time
        
        args:
            Timing (Timing): the Timing object
            Mouse (Mouse): the Mouse object
            surface (pygame.Surface): the surface to draw the button list on
            container (pygame.Rect): the container the button list is in
            definition (dict): the definition of the button list
            y_position (int): the y position of the button list
            parent (Object): the parent UI element
        """
        self.button_functions = button_functions
        self.RENDER_SCALE = RENDER_SCALE
        self.ToolTips = ToolTips
        self.Sound = Sound
        
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        
        self.definition = definition
        self.themeing = self.definition['themeing']
        
        self.title_font_size = int(23 * self.RENDER_SCALE)
        self.title_padding = self.title_font_size + int(5 * self.RENDER_SCALE)
        self.x_padding = int(25 * self.RENDER_SCALE)
        self.y_padding = 0
        
        self.x_position = self.x_padding
        self.y_position = self.y_padding + y_position

        self.width = self.container.width - self.x_padding * 2
        self.height = int(65 * self.RENDER_SCALE)
        
        self.buttons = []
        self.title_hover_button = None
        
        self.tooltip = {"tooltip": self.definition['tooltip']} if 'tooltip' in self.definition else None
        
        self.title_font = Font('d_din_bold', self.title_font_size)
        self.title_text = self.get_title()
        self.__get_rect_and_surface()
        self.__init_buttons()
        self.render()
        self.get_title_hover_button()
    
    def get_title(self):
        """
        Get the title of the button list
        """
        if 'title' in self.definition:
            self.title = True
            return self.definition['title']
        self.title = False
    
    def get_title_hover_button(self):
        if 'title' not in self.definition:
            return
        
        self.title_width = self.title_font.get_width()
        self.title_height = self.title_font.font.get_height()
        self.title_rect = pygame.Rect(int(15 * self.RENDER_SCALE), int(10 * self.RENDER_SCALE), self.title_width, self.title_height) 
        
        self.title_hover_button = InvisibleButton(self.title_width, self.title_height, self.title_rect, None, self.Mouse, self.Timing, self.button_list_surface, self.title_rect, self.tooltip, self, self.RENDER_SCALE, self.ToolTips)
        
    def get_local_position(self):
        """
        Get the position of the button list relative to the container it is in for collision detection.
        """
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button list
        """
        if self.title:
            self.height += self.title_padding
            
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.button_list_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.buttons_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def __init_buttons(self):
        """
        Initialise the buttons in the button list
        """
        for idx, button in enumerate(self.definition['buttons']):
            self.generate_button(button, idx)
      
    def generate_button(self, button, idx):
        """
        Generate a button in the button list.
        """
        button_rect = self.get_button_rect(idx) 
        function = None
        self.buttons.append(ButtonListButtons(self.Timing, self.Mouse, self.Sound, self.buttons_surface, button_rect, button, self.themeing, function, parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips))     
    
    def get_button_rect(self, idx):
        """
        Get the rect for a button in the button list.
        """
        num_buttons = len(self.definition['buttons'])
        edge_padding = int(15 * self.RENDER_SCALE)
        inter_button_padding = int(7 * self.RENDER_SCALE)
        y_padd = int(15 * self.RENDER_SCALE)
        
        total_padding = edge_padding * 2 + inter_button_padding * (num_buttons - 1)
        button_width = (self.width - total_padding) // num_buttons
        button_height = self.height - y_padd * 2 if not self.title else self.height - y_padd * 2 - self.title_padding
        
        x_position = edge_padding + idx * (button_width + inter_button_padding)
        y_position = y_padd if not self.title else y_padd + self.title_padding
        
        return pygame.Rect(x_position, y_position, button_width, button_height)
        
    def render(self):
        """
        Render the button list
        """
        self.render_background()
        self.render_title()
    
    def render_title(self):
        """
        Render the title of the button list
        """
        if not self.title:
            return
        
        self.title_font.draw(self.button_list_surface, self.title_text, self.themeing["title_colour"], 'left_top', int(15 * self.RENDER_SCALE), 0)
        
    def render_background(self):
        """
        Render the background of the button list
        """
        pygame.draw.rect(self.button_list_surface, self.themeing['background_colour'], self.button_list_surface.get_rect(), border_radius = int(5 * self.RENDER_SCALE))
    
    def draw(self):
        """
        Draw the button list
        """
        self.surface.blit(self.button_list_surface, (self.x_position, self.y_position))
        self.surface.blit(self.buttons_surface, (self.x_position, self.y_position))

    def update(self):
        """
        Update the button list
        """
        self.draw()
        
        if self.Mouse.in_dialog:
            return
        
        self.update_buttons()
    
    def update_buttons(self):
        """
        Update the buttons in the button list
        """
        self.buttons_surface.fill((0, 0, 0, 0))
        for button in self.buttons:
            button.update()
        
        self.update_title_hover_button()
    
    def update_title_hover_button(self):
        """
        Update the hover button for the title
        """
        if self.title_hover_button is None:
            return
        
        self.title_hover_button.update()
    
    def on_click(self):
        """
        Handle a click event on the button list
        """
        for button in self.buttons:
            button.active = False
    
    def reset_state(self):
        """
        Reset the state of the button list
        """
        for button in self.buttons:
            button.reset_state()
        
    
        

        
        
        
    
    
        
    

       