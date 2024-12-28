import pygame
from render.GUI.font import Font
from render.GUI.menu_elements.nested_element import NestedElement
from render.GUI.buttons.button_list_buttons import ButtonListButtons

class ButtonList(NestedElement):
    def __init__(self, Timing, Mouse, surface, container, definition, y_position, parent):
        super().__init__(parent)
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        
        self.definition = definition
        self.themeing = self.definition['themeing']
        
        self.title_font_size = 23
        self.title_padding = self.title_font_size + 5
        self.x_padding = 25
        self.y_padding = 0
        
        self.x_position = self.x_padding
        self.y_position = self.y_padding + y_position

        self.width = self.container.width - self.x_padding * 2
        self.height = 65
        
        self.buttons = []
        
        self.title_font = Font('d_din_bold', self.title_font_size )
        self.title_text = self.get_title()
        self.__get_rect_and_surface()
        self.__init_buttons()
        self.render()
    
    def get_title(self):
        if 'title' in self.definition:
            self.title = True
            return self.definition['title']
        self.title = False
        
    def get_local_position(self):
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        if self.title:
            self.height += self.title_padding
            
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.button_list_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def __init_buttons(self):
        for idx, button in enumerate(self.definition['buttons']):
            self.generate_button(button, idx)
      
    def generate_button(self, button, idx):
        
        button_rect = self.get_button_rect(idx) 
        function = None
        self.buttons.append(ButtonListButtons(self.Timing, self.Mouse, self.button_list_surface, button_rect, button, self.themeing, function, parent = self))     
    
    def get_button_rect(self, idx):
        num_buttons = len(self.definition['buttons'])
        edge_padding = 15
        inter_button_padding = 7
        y_padd = 15
        
        total_padding = edge_padding * 2 + inter_button_padding * (num_buttons - 1)
        button_width = (self.width - total_padding) // num_buttons
        button_height = self.height - y_padd * 2 if not self.title else self.height - y_padd * 2 - self.title_padding
        
        x_position = edge_padding + idx * (button_width + inter_button_padding)
        y_position = y_padd if not self.title else y_padd + self.title_padding
        
        return pygame.Rect(x_position, y_position, button_width, button_height)
        
    def render(self):
        self.render_background()
        self.render_title()
        self.render_buttons()
    
    def render_title(self):
        if not self.title:
            return
        
        self.title_font.draw(self.button_list_surface, self.title_text, self.themeing["title_colour"], 'left_top', 15, 0)
        
    def render_background(self):
        pygame.draw.rect(self.button_list_surface, self.themeing['background_colour'], self.button_list_surface.get_rect(), border_radius = 5)
        
    def render_buttons(self):
        pass
    
    def draw(self):
        self.surface.blit(self.button_list_surface, (self.x_position, self.y_position))

    def update(self, in_dialog):
        self.draw()
        
        if in_dialog:
            return
        
        self.update_buttons(in_dialog)
    
    def update_buttons(self, in_dialog):
        for button in self.buttons:
            button.update(in_dialog)
    
    def on_click(self):
        for button in self.buttons:
            button.active = False
    
        
        
    
        

        
        
        
    
    
        
    

       