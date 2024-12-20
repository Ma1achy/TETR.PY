import pygame
from utils import draw_border, draw_solid_colour, apply_gaussian_blur_with_alpha
from render.GUI.menu_elements.button_list import ButtonList
from render.GUI.menu_elements.nested_element import NestedElement

class CollapsiblePanel(NestedElement):
    def __init__(self, Timing, Mouse, surface, container, definition, y_position, linked_header, parent):
        super().__init__(parent = parent)
        
        self.Timing = Timing
        self.Mouse = Mouse
        self.surface = surface
        self.container = container
        self.definition = definition
        self.linked_header = linked_header
        
        self.scroll_y = 0
        self.y_position = y_position
        self.x_position = self.container.width // 6
    
        self.elements = []
        self.open = False
        
        self.width = self.container.width - self.container.width // 3
        self.height = 200
        
        self.shadow_radius = 5
        
        self.__get_height()
        self.__get_rect_and_surface()
        self.__init_elements()
        self.render()
    
    def get_local_position(self):
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.panel_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def __get_height(self):
        self.__get_rect_and_surface()
        self.height = self.__init_elements()
        
    def __init_elements(self):
        self.elements = []
        
        y = 0
        for element in self.definition['elements']:
            if element['type'] == "button_list":
                button_list = ButtonList(self.Timing, self.Mouse, self.panel_surface, self.rect, element, y_position = y, parent = self)
                self.elements.append(button_list)
                y += button_list.height
        
        y += 25
        return y   
      
    def render(self):
        self.render_shadow()
        self.render_panel()
    
    def render_panel(self):
        draw_solid_colour(self.panel_surface, self.definition['background']['colour'], self.panel_surface.get_rect())
        draw_border(self.panel_surface, self.definition['border'], self.panel_surface.get_rect())
    
    def render_shadow(self):
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        self.shadow_surface.fill((0, 0, 0, 0), rect=[0, 0, self.shadow_surface.get_width(), self.shadow_radius * 2])
              
    def draw(self):        
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.surface.blit(self.panel_surface, self.rect.topleft)
    
    def update(self, in_dialog):
        self.open = self.linked_header.open
            
        if not self.open:
            return
        
        self.handle_scroll()
        self.update_elements(in_dialog)
    
    def update_elements(self, in_dialog):
        for element in self.elements:
            element.update(in_dialog)
    
    def handle_scroll(self):
        self.rect.top = self.y_position + self.scroll_y
        self.shadow_rect.top = self.y_position + self.scroll_y - self.shadow_radius * 2
        self.draw()

    def reset_state(self):
        pass