import pygame
from render.GUI.font import Font

class FloatingText():
    def __init__(self, surface, definition, y_position):
        self.surface = surface
        self.definition = definition
        self.y_position = y_position
        
        self.font_type = self.definition["font"]
        self.font_colour = self.definition["colour"]
        self.font_alpha = self.definition["alpha"]
        self.font_size = self.definition["size"]
        self.alignment = self.definition["alignment"]
        self.x_padding, self.y_padding = self.definition["padding"][0], self.definition["padding"][1]
        self.display_text = self.definition["display_text"]
        
        self.main_font = Font(self.font_type, self.font_size)

        self.scroll_y = 0
        
        self.convert_alpha()
        self.get_rect_and_surface()
        self.render()
        
    def get_rect_and_surface(self):
        self.main_font.render_text(self.display_text, self.font_colour)
        self.width = self.main_font.rendered_text.get_width()
        self.height = self.main_font.rendered_text.get_height()
        
        self.font_rect = self.main_font.rendered_text.get_rect(topleft = self.get_alignment())
        self.font_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    
    def draw(self):
        self.surface.blit(self.font_surface, self.font_rect)

    def render(self):
        self.main_font.draw(self.font_surface, self.display_text, self.font_colour, self.alignment, self.x_padding, self.y_padding, None)
        self.font_surface.set_alpha(self.font_alpha)
        
    def update(self, in_dialog):
        self.handle_scroll()
        
    
    def convert_alpha(self):
        self.font_alpha = min(255, int(self.font_alpha * 255))
    
    def reset_state(self):
        pass
    
    def get_alignment(self):
        match self.alignment:
            case 'center':
                topleft = (self.surface.get_width() // 2 - self.main_font.rendered_text.get_width() // 2 + self.x_padding, self.y_position + self.y_padding)
            case 'left':
                topleft = (0 + self.x_padding, self.y_position)
            case 'right':
                topleft = (self.surface.get_width() - self.main_font.rendered_text.get_width() + self.x_padding, self.y_position + self.y_padding)
            case _:
                topleft = (self.surface.get_width() // 2 - self.main_font.rendered_text.get_width() // 2 + self.x_padding, self.y_position + self.y_padding)
            
        return topleft
    
    def handle_scroll(self):      
        self.font_rect.top = self.y_position + self.scroll_y
        self.draw()
        
        
        
        
    