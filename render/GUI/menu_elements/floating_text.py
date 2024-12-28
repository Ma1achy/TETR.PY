import pygame
from render.GUI.font import Font
from utils import smoothstep, smoothstep_interpolate
class FloatingText():
    def __init__(self, Timing, surface, definition, y_position):
        self.Timing = Timing
        self.surface = surface
        self.container = surface.get_rect()
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
        
        self.default_x_position = self.font_rect.left
        
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
        
        self.menu_transition_timer = 0
        self.menu_transition_time = 0.20
        
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
        self.animate_menu_enter_transition()
        self.animate_menu_leave_transition()
    
    def convert_alpha(self):
        self.font_alpha = min(255, int(self.font_alpha * 255))
    
    def reset_state(self):
        self.menu_transition_timer = 0
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
    
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
        )
            
        prog = smoothstep(progress)
        alpha = ((prog) * 255) if is_enter else (((1 - prog)) * 255)
        alpha = max(0, min(255, alpha))
        self.surface.set_alpha(alpha)
        
    
    def animate_slide(self, timer, duration, start_pos, end_pos):
  
        timer += self.Timing.frame_delta_time
        timer = min(timer, duration)

        progress = timer / duration
        progress = max(0, min(1, progress)) 

        new_pos = smoothstep_interpolate(start_pos, end_pos, progress)
   
        self.x_position = new_pos
        self.font_rect.topleft = (self.x_position, self.y_position + self.scroll_y) 
      
        return timer, progress
        
        
        
    