from utils import brightness_maintain_alpha, brightness, smoothstep, smoothstep_interpolate
import pygame
class Button:
    def __init__(self, Timing, surface, Mouse, function, container, width, height, offset = (0, 0), style = 'lighten', maintain_alpha = False, slider = None):
        
        self.Timing = Timing
        self.surface = surface
        
        self.Mouse = Mouse
        
        self.function = function
        self.container = container
        self.width = width
        self.height = height
        self.offset = offset
        
        self.style = style
        self.maintain_alpha = maintain_alpha
        
        self.state = None
        self.previous_state = None
        
        self.hover_surface_transition_time = 0.35
        self.pressed_surface_transition_time = 0.1
        
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
        
    def get_rect_and_surface(self):
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
    def draw(self):
        self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.surface.blit(self.button_surface, self.rect.topleft)
         
    def animate_hover_surface_transition(self):
        if self.style is None:
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
        
        self.pressed_surface_alpha = min(255, smoothstep(self.pressed_timer / self.pressed_surface_transition_time) * 255)
        
        if self.pressed_timer == 0:
            return
        
        if self.pressed_surface_alpha == 0:
            return
        
        self.pressed_surface.set_alpha(self.pressed_surface_alpha)
        self.surface.blit(self.pressed_surface, self.rect.topleft)
            
    def check_hover(self):
        x, y = self.Mouse.position
        x -= self.offset[0]
        y -= self.offset[1]
        
        if self.rect.collidepoint((x, y)):
            if self.state == 'pressed':
                return
            self.state = 'hovered'
        else:
            self.state = None
    
    def check_events(self):
        events_to_remove = []
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button == 'scrollwheel':
                    return
                
                event_x, event_y = info['pos']
                event_x -= self.offset[0]
                event_y -= self.offset[1]
                
                mouse_x, mouse_y = self.Mouse.position
                mouse_x -= self.offset[0]
                mouse_y -= self.offset[1]
                
                if button == 'mb1' and info['down'] and self.rect.collidepoint((event_x, event_y)) and self.rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button == 'mb1' and info['up'] and self.rect.collidepoint((event_x, event_y)) and self.rect.collidepoint((mouse_x, mouse_y)) and self.state == 'pressed':
                    self.state = None
                    events_to_remove.append(event)
                    self.click()
        
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def click(self):
        self.function()
        
    def update(self, in_dialog = False):
        if in_dialog:
            self.draw()
            return
        
        self.check_hover()
        self.check_events()

        if self.state is None and self.previous_state is None:
            self.slider_hover_start_timer = 0
            
            if self.slider_hover_end_timer > 0 and self.slider_hover_end_timer < self.hover_slider_end_length:
                self.slider_hover_end_animation()
            
            if self.slider_pressed_end_timer > 0 and self.slider_pressed_end_timer < self.pressed_slider_end_length:
                self.slider_pressed_end_animation()
                
            self.draw()
              
        if self.state == 'hovered':
            self.handle_hover_start_events()
        
        elif self.state is None and self.previous_state == 'hovered':
            self.handle_hover_end_events()
        
        elif self.state == 'pressed':
            self.handle_pressed_start_events()
        
        elif self.previous_state == 'pressed' and self.state is None:
            self.handle_pressed_end_events()
    
    def handle_hover_start_events(self):
        self.slider_hover_end_timer = 0
        self.slider_hover_start_animation()
        self.draw()
        self.animate_hover_surface_transition()
        self.hover_timer += self.Timing.frame_delta_time
        
        if self.hover_timer >= self.hover_surface_transition_time:
            self.hover_timer = self.hover_surface_transition_time
        
        self.previous_state = 'hovered'
    
    def handle_hover_end_events(self):
        self.slider_hover_start_timer = 0
        self.slider_hover_end_animation()
        self.draw()
        self.animate_hover_surface_transition()
        self.hover_timer -= self.Timing.frame_delta_time
     
        if self.hover_timer <= 0:
            self.hover_timer = 0
            self.hover_surface_alpha = 0
            self.previous_state = None
        
    def handle_pressed_start_events(self):
        self.slider_pressed_end_timer = 0
        self.slider_pressed_start_animation()
        self.draw()
        self.animate_pressed_surface_transition()
        self.pressed_timer += self.Timing.frame_delta_time
        
        if self.pressed_timer >= self.pressed_surface_transition_time:
            self.pressed_timer = self.pressed_surface_transition_time
            
        self.previous_state = 'pressed'
    
    def handle_pressed_end_events(self):
        self.slider_pressed_start_timer = 0
        self.slider_pressed_end_animation()
        self.draw()
        self.animate_pressed_surface_transition()
        self.pressed_timer -= self.Timing.frame_delta_time
               
        if self.pressed_timer <= 0:
            self.pressed_timer = 0
            self.pressed_surface_alpha = 0
            self.previous_state = None
            self.hover_timer = 0
            self.hover_surface_alpha = 0
                
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
        
        if self.slider == 'left':
            self.x_position = self.default_x_position
            self.rect.topleft = (self.x_position, self.y_position)
            self.shadow_rect.topleft = (self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2)
        if self.slider == 'right':
            self.x_position = self.default_x_position
            self.rect.topright = (self.x_position, self.y_position)
            self.shadow_rect.topright = (self.x_position + self.shadow_radius * 2, self.y_position - self.shadow_radius * 2)
        if self.slider == 'up':
            self.y_position = self.default_y_position
            self.rect.topleft = (self.x_position, self.container.bottom - self.y_position)
            self.shadow_rect.topleft = self.rect.topleft[0] - self.shadow_radius * 2, self.rect.topleft[1] - self.shadow_radius * 2
      
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
            self.rect.topleft = (self.x_position, self.y_position)
            self.shadow_rect.topleft = (self.x_position - shadow_offset, self.y_position - shadow_offset)
        elif dir == 'right':
            self.x_position = new_pos
            self.rect.topright = (self.x_position, self.y_position)
            self.shadow_rect.topright = (self.x_position + shadow_offset, self.y_position - shadow_offset)
        elif dir == 'up':
            self.y_position = new_pos
            self.rect.topleft = (self.x_position, self.container.bottom - self.y_position)
            self.shadow_rect.topleft = (self.rect.topleft[0] - shadow_offset, self.rect.topleft[1] - shadow_offset)
        elif dir == 'down':
            self.y_position = new_pos
            self.rect.topleft = (self.x_position, self.container.top + self.y_position)
            self.shadow_rect.topleft = (self.rect.topleft[0] - shadow_offset, self.rect.topleft[1] - shadow_offset)

        return timer, progress

    def slider_hover_start_animation(self):
        if self.slider is None:
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
