import pygame
from utils import draw_border, draw_solid_colour, apply_gaussian_blur_with_alpha, smoothstep, smoothstep_interpolate
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
        
        self.default_x_position = self.container.width // 6
        
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
        self.menu_transition_timer = 0
        self.menu_transition_time = 0.2
    
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
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height))
              
    def draw(self):        
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.surface.blit(self.panel_surface, self.rect.topleft)
    
    def update(self, in_dialog):
        self.open = self.linked_header.open
            
        if not self.open:
            self.reset_state()
            return
        
        self.handle_scroll()
        self.update_elements(in_dialog)
        self.animate_menu_enter_transition()
        self.animate_menu_leave_transition()
    
    def update_elements(self, in_dialog):
        for element in self.elements:
            element.update(in_dialog)
    
    def handle_scroll(self):
        self.rect.top = self.y_position + self.scroll_y
        self.shadow_rect.top = self.y_position + self.scroll_y - self.shadow_radius * 2
        self.draw()

    def reset_state(self):
        self.menu_transition_timer = 0
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
    
    def do_menu_enter_transition_animation(self):
        self.do_menu_enter_transition = True
    
    def do_menu_leave_transition_animation(self):
        self.do_menu_leave_transition = True
    
    def animate_menu_enter_transition(self):
        if not self.do_menu_enter_transition:
            return
        
        self.animate_menu_transition('enter')
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_enter_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_leave_transition(self):
        if not self.do_menu_leave_transition:
            return
        
        self.animate_menu_transition('leave')
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_leave_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_transition(self, direction):
        if not (self.do_menu_enter_transition or self.do_menu_leave_transition):
            return
        
        is_enter = direction == 'enter'
        
        if is_enter:
            start_x = self.default_x_position + self.container.width//12
            end_x = self.default_x_position
            
        elif not is_enter:
            start_x = self.default_x_position
            end_x = self.default_x_position + self.container.width//12
         
        self.menu_transition_timer, progress = self.animate_slide(
            self.menu_transition_timer,
            self.menu_transition_time,
            start_x,
            end_x,
            self.shadow_radius * 2
        )
            
        prog = smoothstep(progress)
        alpha = ((prog) * 255) if is_enter else (((1 - prog)) * 255)
        alpha = max(0, min(255, alpha))
        self.panel_surface.set_alpha(alpha)
        self.shadow_surface.set_alpha(alpha)
        
    def animate_slide(self, timer, duration, start_pos, end_pos, shadow_offset):
  
        timer += self.Timing.frame_delta_time
        timer = min(timer, duration)

        progress = timer / duration
        progress = max(0, min(1, progress))
        
        new_pos = smoothstep_interpolate(start_pos, end_pos, progress)

        self.x_position = new_pos
        self.rect.topleft = (self.x_position, self.y_position + self.scroll_y) 
        self.shadow_rect.topleft = (self.x_position - shadow_offset, self.y_position - shadow_offset + self.scroll_y)
       
        return timer, progress