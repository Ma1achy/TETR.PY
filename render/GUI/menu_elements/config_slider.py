import pygame
from render.GUI.font import Font
from render.GUI.menu_elements.nested_element import NestedElement

class ConfigSlider(NestedElement):
    def __init__(self, Timing, Mouse, surface, container, definition, y_position, parent, RENDER_SCALE = 1):
        super().__init__(parent)
        """
        
        args:
            Timing (Timing): the Timing object
            Mouse (Mouse): the Mouse object
            surface (pygame.Surface): the surface to draw the button list on
            container (pygame.Rect): the container the button list is in
            definition (dict): the definition of the button list
            y_position (int): the y position of the button list
            parent (Object): the parent UI element
        """
        self.RENDER_SCALE = RENDER_SCALE
        
        self.Timing = Timing
        self.Mouse = Mouse
        
        self.surface = surface
        self.container = container
        
        self.bar_height = int(7 * self.RENDER_SCALE)
        
        self.definition = definition
        self.themeing = self.definition['themeing']
        
        self.left_end_text = self.definition['left_end_text']
        self.right_end_text = self.definition['right_end_text']
        self.end_text_colour = self.themeing['end_text_colour']
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
        self.__get_rect_and_surface()
        self.render()
    
    def get_title(self):
        """
        Get the title of the button list
        """
        if 'title' in self.definition:
            self.title = True
            return self.definition['title']
        self.title = False
        
    def get_local_position(self):
        """
        Get the position of the button list relative to the container it is in for collision detection.
        """
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the button list
        """ 
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.slider_bar_rect = pygame.Rect(self.start_x, self.height // 2 - self.bar_height // 2, self.width - self.start_x - self.end_x, self.bar_height)
        self.button_list_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def render(self):
        """
        Render the button list
        """
        self.render_background()
        self.render_title()
        self.render_slider_bar()
        self.render_end_text()
    
    def render_title(self):
        """
        Render the title of the button list
        """
        if not self.title:
            return
        
        self.title_font.draw(self.button_list_surface, self.title_text, self.themeing["title_colour"], 'left', int(15 * self.RENDER_SCALE), 0)
    
    def render_end_text(self):
        """
        Render the end text of the button list
        """
        self.end_text_font.draw(self.button_list_surface, self.left_end_text, self.end_text_colour, 'left_bottom', self.start_x, int(5 * self.RENDER_SCALE))
        self.end_text_font.draw(self.button_list_surface, self.right_end_text, self.end_text_colour, 'right_bottom', self.end_x, int(5 * self.RENDER_SCALE))
    
    def render_slider_bar(self):
        pygame.draw.rect(self.button_list_surface, self.themeing['colour'], self.slider_bar_rect)
        
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

    def update(self, in_dialog):
        """
        Update the button list
        """
        self.draw()
        
        if in_dialog:
            return