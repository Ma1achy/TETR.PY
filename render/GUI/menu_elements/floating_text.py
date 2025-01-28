import pygame
from render.GUI.font import Font
from utils import smoothstep, smoothstep_interpolate
class FloatingText():
    def __init__(self, Timing, surface, definition, y_position, RENDER_SCALE = 1):
        """
        A text element that can floats on the page
        
        args:
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the text on
            definition (dict): the definition of the text
            y_position (int): the y position of the text
        """
        self.RENDER_SCALE = RENDER_SCALE
        
        self.Timing = Timing
        self.surface = surface
        self.container = surface.get_rect()
        self.definition = definition
        self.y_position = y_position
        
        self.font_type = self.definition["font"]
        self.font_colour = self.definition["colour"]
        self.font_alpha = self.definition["alpha"]
        self.font_size = int(self.definition["size"] * self.RENDER_SCALE)
        self.alignment = self.definition["alignment"]
        self.x_padding, self.y_padding = int(self.definition["padding"][0] * self.RENDER_SCALE), int(self.definition["padding"][1] * self.RENDER_SCALE)
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
        
        self.on_screen = False
        
    def get_rect_and_surface(self):
        """
        Get the rects and surfaces for the text
        """
        self.main_font.render_text(self.display_text, self.font_colour)
        self.width = self.main_font.rendered_text.get_width()
        self.height = self.main_font.rendered_text.get_height()
        
        self.font_rect = self.main_font.rendered_text.get_rect(topleft = self.get_alignment())
        self.font_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.on_screen_rect = self.surface.get_rect()
    
    def draw(self):
        """
        Draw the text
        """
        if not self.on_screen:
            return
        
        self.surface.blit(self.font_surface, self.font_rect)

    def render(self):
        """
        Render the text
        """
        self.main_font.draw(self.font_surface, self.display_text, self.font_colour, self.alignment, self.x_padding, self.y_padding, None)
        self.font_surface.set_alpha(self.font_alpha)
        
    def update(self):
        """
        Update the text
        """
        self.handle_scroll()
        self.check_if_on_screen()
        self.animate_menu_enter_transition()
        self.animate_menu_leave_transition()
    
    def convert_alpha(self):
        """
        Convert the alpha value from 0 - 1 to a 0 - 255 scale
        """
        self.font_alpha = min(255, int(self.font_alpha * 255))
    
    def reset_state(self):
        """
        Reset the state of the text
        """
        self.menu_transition_timer = 0
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
    
    def get_alignment(self):
        """
        Get the alignment of the text within the container
        """
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
        """
        Handle the scrolling of the menu
        """
        self.font_rect.top = self.y_position + self.scroll_y
        self.draw()
        
    def do_menu_enter_transition_animation(self):
        """
        Start the menu enter transition animation
        """
        self.do_menu_enter_transition = True
    
    def do_menu_leave_transition_animation(self):
        """
        Start the menu leave transition animation
        """
        self.do_menu_leave_transition = True
    
    def animate_menu_enter_transition(self):
        """
        Animate the text during a menu enter transition.
        """
        if not self.do_menu_enter_transition:
            return
        
        self.animate_menu_transition(True)
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_enter_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_leave_transition(self):
        """
        Animate the text during a menu leave transition.
        """
        if not self.do_menu_leave_transition:
            return
        
        self.animate_menu_transition(False)
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_leave_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_transition(self, is_enter):
        """
        Animate the text during a menu transition.
        """
        if not (self.do_menu_enter_transition or self.do_menu_leave_transition):
            return
        
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
            
        self.animate_menu_transition_alpha(progress, is_enter)
        
    def animate_slide(self, timer, duration, start_pos, end_pos):
        """
        Animate the slide of the text during a menu transition.
        
            timer (float): The current time of the animation.
            duration (float): The total duration of the animation.
            start_pos (int): The starting x position of the text.
            end_pos (int): The ending x position of the text.
        """
  
        timer += self.Timing.frame_delta_time
        timer = min(timer, duration)

        progress = timer / duration
        progress = max(0, min(1, progress)) 

        new_pos = smoothstep_interpolate(start_pos, end_pos, progress)
   
        self.x_position = new_pos
        self.font_rect.topleft = (self.x_position, self.y_position + self.scroll_y) 
      
        return timer, progress
    
    def animate_menu_transition_alpha(self, progress, is_enter):
        """
        Animate the alpha of the text surface during a menu transition.
        
            progress (float): Progress percentage of the animation.
            is_enter (bool): Whether the transition is entering or leaving the menu.
        """
        p = smoothstep(progress)
        alpha = ((p) * 255) if is_enter else (((1 - p)) * 255)
        alpha = max(0, min(self.font_alpha, alpha))
        
        self.font_surface.set_alpha(alpha)
    
    def check_if_on_screen(self):
        """
        Check if the panel is on screen
        """
        if self.font_rect.bottom > 0 and self.font_rect.top < self.on_screen_rect.height:
            self.on_screen = True
            return
        self.on_screen = False
        

        
        
        
    