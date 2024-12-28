from utils import brightness_maintain_alpha, brightness, smoothstep, smoothstep_interpolate
import pygame
from app.input.mouse.mouse import MouseEvents
from render.GUI.menu_elements.nested_element import NestedElement
class Button(NestedElement):
    def __init__(self, Timing, surface, Mouse, function, container, width, height, style = 'lighten', maintain_alpha = False, slider = None, parent = None):
        super().__init__(parent)
        
        self.Timing = Timing
        self.surface = surface
        
        self.Mouse = Mouse
        
        self.function = function
        self.container = container
        self.width = width
        self.height = height
        
        self.style = style
        self.maintain_alpha = maintain_alpha
        
        self.scroll_y = 0
        self.y_position = 0
        
        self.state = None
        self.previous_state = None
        self.doing_click = False
        
        self.hover_surface_transition_time = 0.2
        self.pressed_surface_transition_time = 0.2
        
        self.hover_timer = 0
        self.pressed_timer = 0
        
        self.hover_surface_alpha = 0
        self.pressed_surface_alpha = 0
        
        self.slider_hover_start_timer = 0
        self.slider_hover_end_timer = 0
        self.slider_pressed_start_timer = 0
        self.slider_pressed_end_timer = 0
        
        self.slider = slider
        self.hover_slider_start_length = 0.2
        self.hover_slider_end_length = 0.5
        self.pressed_slider_start_length = 0.2
        self.pressed_slider_end_length = 0.4
        
        self.shadow_surface = pygame.Surface((1, 1), pygame.HWSURFACE|pygame.SRCALPHA)
        self.shadow_rect = pygame.Rect(0, 0, 1, 1)
        self.shadow_radius = 5
        
        self.get_rect_and_surface()
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        
        self.ignore_events = False
        
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
        
        self.menu_transition_timer = 0
        self.menu_transition_time = 0.20
         
    def get_local_position(self):
        return self.rect.topleft
    
    # -------------------------------------------------------------------------- DRAWING --------------------------------------------------------------------------
    
    def get_rect_and_surface(self):
        if self.width < 1:
            self.width = 1
        
        if self.height < 1:
            self.height = 1
        
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def get_overlays(self):
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        self.__get_darken_overlay()
        
    def __get_lighten_overlay(self):
        if self.style != 'lighten':
            return
        
        if self.maintain_alpha:
            self.hover_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.hover_surface, 1.2)

            self.pressed_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.pressed_surface, 1.5)
        else:
            self.hover_surface = self.button_surface.copy()
            brightness(self.hover_surface, 1.2)

            self.pressed_surface = self.button_surface.copy()
            brightness(self.pressed_surface, 1.5)
        
    def __get_darken_overlay(self):
        if self.style != 'darken':
            return
        
        if self.maintain_alpha:
            self.hover_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.hover_surface, 0.8)

            self.pressed_surface = self.button_surface.copy()
            brightness_maintain_alpha(self.pressed_surface, 0.5)
        else:
            self.hover_surface = self.button_surface.copy()
            brightness(self.hover_surface, 0.8)

            self.pressed_surface = self.button_surface.copy()
            brightness(self.pressed_surface, 0.5)
            
    def draw(self):
        if not hasattr(self, 'button_surface') or self.button_surface is None:
            return 
        
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.surface.blit(self.button_surface, self.rect.topleft)
    
    # -------------------------------------------------------------------------- MOUSE EVENTS --------------------------------------------------------------------------
              
    def check_hover(self):
        x, y = self.Mouse.position
        
        self.collision_rect.topleft = self.get_screen_position()
        
        if self.collision_rect.collidepoint((x, y)):
            if self.state == 'pressed':
                return
            self.state = 'hovered'
        else:
            self.state = None
    
    def check_events(self):
        events_to_remove = []
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button is MouseEvents.SCROLLWHEEL:
                    return
                
                event_x, event_y = info['pos']
                mouse_x, mouse_y = self.Mouse.position

                if button is MouseEvents.MOUSEBUTTON1 and info['down'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button is MouseEvents.MOUSEBUTTON1 and info['up'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)) and self.state == 'pressed':
                    events_to_remove.append(event)
                    self.start_click()
        
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def update_click(self):
        if self.doing_click and self.pressed_timer >= self.pressed_surface_transition_time:
            self.doing_click = False
            self.click()
            
    def start_click(self):
        self.doing_click = True
    
    def click(self):
        if self.function is None:
            return
        self.function()
    
    # -------------------------------------------------------------------------- UPDATE LOGIC --------------------------------------------------------------------------
    
    def update_state(self):
        if self.ignore_events:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        self.check_hover()
        self.update_click()
        self.check_events()
        
    def update(self, in_dialog = False):
        
        self.handle_scroll()
        
        if not in_dialog:
            self.update_state()
            
        if self.state is None and self.previous_state is None:
            self.slider_hover_start_timer = 0
            
            if self.slider_hover_end_timer > 0 and self.slider_hover_end_timer < self.hover_slider_end_length:
                self.slider_hover_end_animation()
            
            if self.slider_pressed_end_timer > 0 and self.slider_pressed_end_timer < self.pressed_slider_end_length:
                self.slider_pressed_end_animation()
                  
        if self.state == 'hovered':
            self.handle_hover_start_events()
        
        elif self.state is None and self.previous_state == 'hovered':
            self.handle_hover_end_events()
        
        elif self.state == 'pressed':
            self.handle_pressed_start_events()
        
        elif self.previous_state == 'pressed' and self.state is None:
            self.handle_pressed_end_events()
            
        self.animate_menu_enter_transition()
        self.animate_menu_leave_transition()
    
    def handle_scroll(self):
        self.rect.top = self.y_position + self.scroll_y
        self.shadow_rect.top = self.y_position + self.scroll_y - self.shadow_radius * 2
        self.draw()
        
    def handle_hover_start_events(self):
        self.slider_hover_end_timer = 0
        self.slider_hover_start_animation()
 
        self.animate_hover_surface_transition()
        self.hover_timer += self.Timing.frame_delta_time
        
        if self.hover_timer >= self.hover_surface_transition_time:
            self.hover_timer = self.hover_surface_transition_time
        
        self.previous_state = 'hovered'
    
    def handle_hover_end_events(self):
        self.slider_hover_start_timer = 0
        self.slider_hover_end_animation()
     
        self.animate_hover_surface_transition()
        self.hover_timer -= self.Timing.frame_delta_time
     
        if self.hover_timer <= 0:
            self.hover_timer = 0
            self.hover_surface_alpha = 0
            self.previous_state = None
        
    def handle_pressed_start_events(self):
        self.slider_pressed_end_timer = 0
        self.slider_pressed_start_animation()

        self.animate_pressed_surface_transition()
        self.pressed_timer += self.Timing.frame_delta_time
        
        if self.pressed_timer >= self.pressed_surface_transition_time:
            self.pressed_timer = self.pressed_surface_transition_time
            
        self.previous_state = 'pressed'
    
    def handle_pressed_end_events(self):
        self.slider_pressed_start_timer = 0
        self.slider_pressed_end_animation()

        self.animate_pressed_surface_transition()
        self.pressed_timer -= self.Timing.frame_delta_time
               
        if self.pressed_timer <= 0:
            self.pressed_timer = 0
            self.pressed_surface_alpha = 0
            self.previous_state = None
            self.hover_timer = 0
            self.hover_surface_alpha = 0
                        
    def reset_state(self):
        self.hover_timer = 0
        self.pressed_timer = 0
        self.hover_surface_alpha = 0
        self.pressed_surface_alpha = 0
        self.state = None
        self.previous_state = None
        self.slider_hover_start_timer = 0
        self.slider_hover_end_timer = 0
        self.slider_pressed_start_timer = 0
        self.slider_pressed_end_timer = 0
        
        self.menu_transition_timer = 0
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
        
        if self.slider == 'left':
            self.x_position = self.default_x_position
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topleft = self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2  + self.scroll_y
        if self.slider == 'right':
            self.x_position = self.default_x_position
            self.rect.topright = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topright = self.x_position + self.shadow_radius * 2, self.y_position - self.shadow_radius * 2 + self.scroll_y
        if self.slider == 'up':
            self.y_position = self.default_y_position + self.scroll_y
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topleft = self.rect.topleft[0] - self.shadow_radius * 2, self.rect.topleft[1] - self.shadow_radius * 2  + self.scroll_y
        if self.slider == 'down':
            self.y_position = self.default_y_position + self.scroll_y
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topleft = self.rect.topleft[0] - self.shadow_radius * 2, self.rect.topleft[1] - self.shadow_radius * 2  + self.scroll_y
    
    # -------------------------------------------------------------------------- ANIMATION --------------------------------------------------------------------------
    
    # ----------------------------------- Hover and pressed surface animations -----------------------------------
    
    def animate_hover_surface_transition(self):
        if self.style is None:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        self.hover_surface_alpha = min(255, smoothstep(self.hover_timer / self.hover_surface_transition_time) * 255) 
   
        if self.hover_timer == 0:
            return
        
        if self.hover_surface_alpha == 0:
            return
        
        self.hover_surface.set_alpha(self.hover_surface_alpha)
        self.surface.blit(self.hover_surface, self.rect.topleft)
    
    def animate_pressed_surface_transition(self):
        if self.style is None:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        self.pressed_surface_alpha = min(255, smoothstep(self.pressed_timer / self.pressed_surface_transition_time) * 255)
        
        if self.pressed_timer == 0:
            return
        
        if self.pressed_surface_alpha == 0:
            return
        
        self.pressed_surface.set_alpha(self.pressed_surface_alpha)
        self.surface.blit(self.pressed_surface, self.rect.topleft)
    
    # ----------------------------------- Slider animations -----------------------------------
    
    def animate_slider(self, timer, duration, start_pos, end_pos, dir, shadow_offset):
        """
        Generalized animation logic for sliders.
        - timer: Current animation timer.
        - duration: Total animation duration.
        - start_pos: Starting position.
        - end_pos: Ending position.
        - axis: 'x' or 'y' to determine the axis of animation.
        - shadow_offset: Offset for shadow calculations.
        - direction: 'positive' or 'negative' for determining the slider's direction.
        """
        # Update and clamp the timer
        timer += self.Timing.frame_delta_time
        timer = min(timer, duration)

        # Calculate progress
        progress = timer / duration
        progress = max(0, min(1, progress))  # Clamp to [0, 1]

        # Interpolate position
        if dir == 'right':
            new_pos = smoothstep_interpolate(start_pos, end_pos, progress)
        elif dir == 'up':
            new_pos = smoothstep_interpolate(start_pos, end_pos, progress)
        elif dir == 'left':
            new_pos = smoothstep_interpolate(start_pos, end_pos, progress)
        elif dir == 'down':
            new_pos = smoothstep_interpolate(start_pos, end_pos, progress)
           
        # Update position
        if dir == 'left':
            self.x_position = new_pos
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y) 
            self.shadow_rect.topleft = (self.x_position - shadow_offset, self.y_position - shadow_offset + self.scroll_y)
        elif dir == 'right':
            self.x_position = new_pos
            self.rect.topright = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topright = (self.x_position + shadow_offset, self.y_position - shadow_offset + self.scroll_y)
        elif dir == 'up':
            self.y_position = new_pos
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topleft = (self.rect.topleft[0] - shadow_offset, self.rect.topleft[1] - shadow_offset + self.scroll_y)
        elif dir == 'down':
            self.y_position = new_pos
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topleft = (self.rect.topleft[0] - shadow_offset, self.rect.topleft[1] - shadow_offset + self.scroll_y)

        return timer, progress

    def slider_hover_start_animation(self):
        if self.slider is None:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        if self.slider == 'left' or self.slider == 'right':
            self.slider_hover_start_timer, progress = self.animate_slider(
                self.slider_hover_start_timer,
                self.hover_slider_start_length,
                self.default_x_position,
                self.hovered_x_position,
                self.slider,
                self.shadow_radius * 2,
            )
        elif self.slider == 'up' or self.slider == 'down':
            self.slider_hover_start_timer, progress = self.animate_slider(
                self.slider_hover_start_timer,
                self.hover_slider_start_length,
                self.default_y_position,
                self.hovered_y_position,
                self.slider,
                self.shadow_radius * 2,
            )

    def slider_hover_end_animation(self):
        if self.slider is None:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        if self.slider == 'left' or self.slider == 'right':
            self.slider_hover_end_timer, progress = self.animate_slider(
                self.slider_hover_end_timer,
                self.hover_slider_end_length,
                self.hovered_x_position,
                self.default_x_position,
                self.slider,
                self.shadow_radius * 2,
            )
        elif self.slider == 'up' or self.slider == 'down':
            self.slider_hover_end_timer, progress = self.animate_slider(
                self.slider_hover_end_timer,
                self.hover_slider_end_length,
                self.hovered_y_position,
                self.default_y_position,
                self.slider,
                self.shadow_radius * 2,
            )

    def slider_pressed_start_animation(self):
        if self.slider is None:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        if self.slider == 'left' or self.slider == 'right':
            self.slider_pressed_start_timer, progress = self.animate_slider(
                self.slider_pressed_start_timer,
                self.pressed_slider_start_length,
                self.default_x_position,
                self.pressed_x_position,
                self.slider,
                self.shadow_radius * 2,
            )
        elif self.slider == 'up' or self.slider == 'down':
            self.slider_pressed_start_timer, progress = self.animate_slider(
                self.slider_pressed_start_timer,
                self.pressed_slider_start_length,
                self.default_y_position,
                self.pressed_y_position,
                self.slider,
                self.shadow_radius * 2,
            )

    def slider_pressed_end_animation(self):
        if self.slider is None:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        if self.slider == 'left' or self.slider == 'right':
            self.slider_pressed_end_timer, progress = self.animate_slider(
                self.slider_pressed_end_timer,
                self.pressed_slider_end_length,
                self.pressed_x_position,
                self.default_x_position,
                self.slider,
                self.shadow_radius * 2,
            )
        elif self.slider == 'up' or self.slider == 'down':
            self.slider_pressed_end_timer, progress = self.animate_slider(
                self.slider_pressed_end_timer,
                self.pressed_slider_end_length,
                self.pressed_y_position,
                self.default_y_position,
                self.slider,
                self.shadow_radius * 2,
            )
    
    # ----------------------------------- Menu transition animations -----------------------------------
       
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
        
        # Determine if it's an 'enter' or 'leave' transition
        is_enter = direction == 'enter'
        
        if self.slider == 'left' and is_enter:
            start_x = self.default_x_position + self.container.width//12
            end_x = self.default_x_position
            
        elif self.slider == 'left' and not is_enter:
            start_x = self.default_x_position
            end_x = self.default_x_position + self.container.width//12
        
        elif self.slider == 'right' and is_enter:
            start_x = self.default_x_position - self.width//5
            end_x = self.default_x_position
        
        elif self.slider == 'right' and not is_enter:
            start_x = self.default_x_position
            end_x = self.default_x_position - self.width//5
        
        elif self.slider == 'up' and is_enter:
            start_y = self.default_y_position + self.height // 4
            end_y = self.default_y_position
        
        elif self.slider == 'up' and not is_enter:
            start_y = self.default_y_position
            end_y = self.default_y_position + self.height // 4
        
        elif self.slider == 'down' and is_enter:
            start_y = self.default_y_position - self.height // 4
            end_y = self.default_y_position
        
        elif self.slider == 'down' and not is_enter:
            start_y = self.default_y_position
            end_y = self.default_y_position - self.height // 4
           
        # Animate slider using the helper
        if self.slider in ['left', 'right']:
            self.menu_transition_timer, progress = self.animate_slider(
                self.menu_transition_timer,
                self.menu_transition_time,
                start_x,
                end_x,
                self.slider,
                self.shadow_radius * 2,
            )
            
        elif self.slider in ['up', 'down']:
            self.menu_transition_timer, progress = self.animate_slider(
                self.menu_transition_timer,
                self.menu_transition_time,
                start_y,
                end_y,
                self.slider,
                self.shadow_radius * 2,
            )
        
        prog = smoothstep(progress)
        alpha = ((prog) * 255) if is_enter else (((1 - prog)) * 255)
        alpha = max(0, min(255, alpha))
        self.button_surface.set_alpha(alpha)
        self.shadow_surface.set_alpha(alpha)
        
