from utils import brightness_maintain_alpha, brightness, smoothstep, smoothstep_interpolate
import pygame
from app.input.mouse.mouse import MouseEvents
from render.GUI.menu_elements.nested_element import NestedElement
from app.core.sound.sound import Sound
from app.core.sound.sfx import SFX
from app.core.config_manager import VideoSettings
class Button(NestedElement):
    def __init__(self, Timing, surface, Mouse, function, container, width, height, style = 'lighten', maintain_alpha = False, slider = None, parent = None, RENDER_SCALE = 1, ToolTips = None, Sound:Sound = None):
        super().__init__(parent)
        """
        Base button class
        
        args:
            Timing (Timing): the Timing object
            surface (pygame.Surface): the surface to draw the button on
            Mouse (Mouse): the Mouse object
            function (callable): the function to call when the button is pressed
            container (pygame.Rect): the container the button is in
            width (int): the width of the button
            height (int): the height of the button
            style (str): the style of the button
            maintain_alpha (bool): whether to maintain the alpha of the button
            slider (str): the direction the button slides in
        """
        self.RENDER_SCALE = RENDER_SCALE
        
        self.Sound = Sound
        
        self.hover_sound = SFX.MenuHover
        self.click_sound = SFX.MenuClick
        
        self.ToolTips = ToolTips
        self.tooltip = None
        
        self.Timing = Timing
        self.surface = surface
        self.Mouse = Mouse
        
        # button properties
        self.function = function
        self.container = container
        self.width = int(width * self.RENDER_SCALE)
        self.height = int(height * self.RENDER_SCALE)
        
        # styling
        self.style = style
        self.maintain_alpha = maintain_alpha
        self.slider = slider
          
        # position
        self.x_position = 0
        self.default_x_position = 0
        
        self.scroll_y = 0
        self.y_position = 0
        self.default_y_position = 0
        
        # state
        self.ignore_events = False
        self.state = None
        self.previous_state = None
        self.doing_click = False
        self.being_dragged = False
        
        # surface and rect
        self.get_rect_and_surface()
        
        # collision detection
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        
        # shadow
        self.shadow_surface = pygame.Surface((1, 1), pygame.HWSURFACE|pygame.SRCALPHA)
        self.shadow_rect = pygame.Rect(0, 0, 1, 1)
        self.shadow_radius = int(5 * self.RENDER_SCALE)
        
        # hover and pressed surface transition animation
        self.hover_surface_transition_time = 0.2
        self.pressed_surface_transition_time = 0.2
        
        self.hover_timer = 0
        self.pressed_timer = 0
        
        self.hover_surface_alpha = 0
        self.pressed_surface_alpha = 0
        
        # slider animation
        self.slider_hover_start_timer = 0
        self.slider_hover_end_timer = 0
        
        self.slider_pressed_start_timer = 0
        self.slider_pressed_end_timer = 0
        
        self.hover_slider_start_length = 0.2
        self.hover_slider_end_length = 0.5
        
        self.pressed_slider_start_length = 0.2
        self.pressed_slider_end_length = 0.4
        
        # menu transition animation
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
        
        self.menu_transition_timer = 0
        self.menu_transition_time = 0.20
        
        self.on_screen = False
        self.on_screen_rect = self.surface.get_rect()
        
        self.dropdown = False 
        self.reset_on_click = False
        
        self.disable_shadow = False
        
    def get_local_position(self):
        """
        Get the local position of the button for collision detection.
        """
        return self.rect.topleft
    
    # -------------------------------------------------------------------------- DRAWING --------------------------------------------------------------------------
    
    def get_rect_and_surface(self):
        """
        Get the rect and surface for the button.
        """
        if self.width < 1:
            self.width = 1
        
        if self.height < 1:
            self.height = 1
        
        self.rect = pygame.Rect(self.container.left, self.container.top, self.width, self.height)
        self.button_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def get_overlays(self):
        """
        Render the overlays for the button (hover and pressed states).
        """
        if self.style is None:
            return
        
        self.__get_lighten_overlay()
        self.__get_darken_overlay()
        
    def __get_lighten_overlay(self):
        """
        Render the lighten overlays for the button (hover and pressed states).
        """
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
        """
        Render the darken overlays for the button (hover and pressed states).
        """
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
        """
        Draw the button.
        """
        if not hasattr(self, 'button_surface') or self.button_surface is None:
            return 
        
        if not self.on_screen:
            return
        
        if VideoSettings.DRAW_BACKGROUND or not self.disable_shadow:
            self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)

        self.surface.blit(self.button_surface, self.rect.topleft)
    
    # -------------------------------------------------------------------------- MOUSE EVENTS --------------------------------------------------------------------------
              
    def check_hover(self):
        """
        Check if the mouse is hovering over the button.
        """
        if self.Mouse.ignore_events:
            return
        
        x, y = self.Mouse.position
        
        self.collision_rect.topleft = self.get_screen_position()
        
        if self.collision_rect.collidepoint((x, y)):
            if self.state == 'pressed':
                return
            self.state = 'hovered'
            self.play_hover_sound()
        else:
            self.state = None
    
    def check_events(self):
        """
        Check for input events.
        """
        if self.Mouse.ignore_events:
            return
        
        events_to_remove = []
        mouse_x, mouse_y = self.Mouse.position
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button is MouseEvents.SCROLLWHEEL:
                    return
                
                event_x, event_y = info['pos']

                if button is MouseEvents.MOUSEBUTTON1 and info['down'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)):
                    self.state = 'pressed'
                    events_to_remove.append(event)
                
                if button is MouseEvents.MOUSEBUTTON1 and info['up'] and self.collision_rect.collidepoint((event_x, event_y)) and self.collision_rect.collidepoint((mouse_x, mouse_y)) and self.state == 'pressed':
                    events_to_remove.append(event)
                    self.start_click()
        
        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def update_click(self):
        """
        Update the click event.
        """
        if not self.doing_click:
            return
        
        if self.doing_click:
            self.state = 'pressed'
            
        if self.doing_click and self.pressed_timer >= self.pressed_surface_transition_time:
            self.doing_click = False
            self.click()
            
    def start_click(self):
        """
        Start the click event.
        """
        self.doing_click = True
        self.play_click_sound()
    
    def click(self):
        """
        Execute the button's function.
        """
        if self.ToolTips:
            self.ToolTips.tooltip_timer = 0
            
        if self.function is None:
            return
         
        self.function()
        
        if self.reset_on_click:
            self.state = None
    
    # -------------------------------------------------------------------------- UPDATE LOGIC --------------------------------------------------------------------------
    
    def update_state(self):
        """
        Update the state of the button and check for input events.
        """
        if not self.on_screen:
            return
        
        if self.Mouse.ignore_events:
            return
        
        if self.Mouse.in_dialog or self.ignore_events:
            return
        
        if self.Mouse.in_dropdown and not self.dropdown:
            return
        
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
           
        if self.Mouse.slider_interaction_event and not self.being_dragged:
            return
            
        self.check_hover()
        self.update_click()
        self.check_events()
        
    def update(self):
        """
        Update the button.
        """
        self.handle_scroll()
        self.check_if_on_screen()
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
        """
        Handle the scrolling of the menu by updating the position of the button.
        """
        self.rect.top = self.y_position + self.scroll_y
        self.shadow_rect.top = self.y_position + self.scroll_y - self.shadow_radius * 2
        self.draw()
        
    def handle_hover_start_events(self):
        """
        Handle the start of the hover state.
        """
        if not self.on_screen:
            return
        
        self.slider_hover_end_timer = 0
        self.slider_hover_start_animation()
 
        self.animate_hover_surface_transition()
        self.hover_timer += self.Timing.frame_delta_time
        
        if self.hover_timer >= self.hover_surface_transition_time:
            self.hover_timer = self.hover_surface_transition_time
            self.draw_tooltip()
            
        self.previous_state = 'hovered'
    
    def handle_hover_end_events(self):
        """
        Handle the end of the hover state.
        """
        if not self.on_screen:
            return
        
        self.slider_hover_start_timer = 0
        self.slider_hover_end_animation()
     
        self.animate_hover_surface_transition()
        self.hover_timer -= self.Timing.frame_delta_time
     
        if self.hover_timer <= 0:
            self.hover_timer = 0
            self.hover_surface_alpha = 0
            self.previous_state = None
        
    def handle_pressed_start_events(self):
        """
        Handle the start of the pressed state.
        """
        if not self.on_screen:
            return
        
        self.slider_pressed_end_timer = 0
        self.slider_pressed_start_animation()

        self.animate_pressed_surface_transition()
        self.pressed_timer += self.Timing.frame_delta_time
        
        if self.pressed_timer >= self.pressed_surface_transition_time:
            self.pressed_timer = self.pressed_surface_transition_time
            
        self.previous_state = 'pressed'
    
    def handle_pressed_end_events(self):
        """
        Handle the end of the pressed state.
        """
        if not self.on_screen:
            return
        
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
        """
        Reset the state of the button.
        """
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
        """
        Animate the transition into the hover surface.
        """
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        if self.style is None:
            return
        
        if self.hover_surface_transition_time > 0:
            self.hover_surface_alpha = max(0, min(255, smoothstep(self.hover_timer / self.hover_surface_transition_time) * 255))
   
        if self.hover_timer == 0:
            return
        
        if self.hover_surface_alpha == 0:
            return
        
        self.hover_surface.set_alpha(self.hover_surface_alpha)
        self.surface.blit(self.hover_surface, self.rect.topleft)
    
    def animate_pressed_surface_transition(self):
        """
        Animate the transition into the pressed surface.
        """
        if self.do_menu_enter_transition or self.do_menu_leave_transition:
            return
        
        if self.style is None:
            return
        
        if self.pressed_surface_transition_time > 0:
            self.pressed_surface_alpha = max(0, min(255, smoothstep(self.pressed_timer / self.pressed_surface_transition_time) * 255))
        
        if self.pressed_timer == 0:
            return
        
        if self.pressed_surface_alpha == 0:
            return
        
        self.pressed_surface.set_alpha(self.pressed_surface_alpha)
        self.surface.blit(self.pressed_surface, self.rect.topleft)
    
    # ----------------------------------- Slider animations -----------------------------------
    
    def animate_slider(self, timer, duration, start_position, end_position, direction, shadow_offset):
        """
        Animate the slider element in a given direction.
        
            timer (float): Current animation timer.
            duration (float): Total animation duration.
            start_position (float): Starting position.
            end_position (float): Ending position.
            direction (str): Direction of the slider.
            shadow_offset (float): Offset for shadow calculations.
        """
        timer += self.Timing.frame_delta_time
        timer = min(timer, duration)

        progress = timer / duration
        progress = max(0, min(1, progress)) 

        if direction == 'right':
            new_pos = smoothstep_interpolate(start_position, end_position, progress)
        elif direction == 'up':
            new_pos = smoothstep_interpolate(start_position, end_position, progress)
        elif direction == 'left':
            new_pos = smoothstep_interpolate(start_position, end_position, progress)
        elif direction == 'down':
            new_pos = smoothstep_interpolate(start_position, end_position, progress)
           
        if direction == 'left':
            self.x_position = new_pos
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y) 
            self.shadow_rect.topleft = (self.x_position - shadow_offset, self.y_position - shadow_offset + self.scroll_y)
        elif direction == 'right':
            self.x_position = new_pos
            self.rect.topright = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topright = (self.x_position + shadow_offset, self.y_position - shadow_offset + self.scroll_y)
        elif direction == 'up':
            self.y_position = new_pos
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topleft = (self.rect.topleft[0] - shadow_offset, self.rect.topleft[1] - shadow_offset + self.scroll_y)
        elif direction == 'down':
            self.y_position = new_pos
            self.rect.topleft = (self.x_position, self.y_position + self.scroll_y)
            self.shadow_rect.topleft = (self.rect.topleft[0] - shadow_offset, self.rect.topleft[1] - shadow_offset + self.scroll_y)

        return timer, progress

    def slider_hover_start_animation(self):
        """
        Animate the slider when the button is hovered.
        """
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
        """
        Animate the slider when the button is no longer hovered.
        """
        if self.slider is None:
            return
        
        if self.slider == 'left' or self.slider == 'right':
            self.slider_hover_end_timer, progress = self.animate_slider(
                self.slider_hover_end_timer,
                self.hover_slider_end_length,
                self.x_position,
                self.default_x_position,
                self.slider,
                self.shadow_radius * 2,
            )
        elif self.slider == 'up' or self.slider == 'down':
            self.slider_hover_end_timer, progress = self.animate_slider(
                self.slider_hover_end_timer,
                self.hover_slider_end_length,
                self.y_position,
                self.default_y_position,
                self.slider,
                self.shadow_radius * 2,
            )

    def slider_pressed_start_animation(self):
        """
        Animate the slider when the button is pressed.
        """
        if self.slider is None:
            return
         
        if self.slider == 'left' or self.slider == 'right':
            self.slider_pressed_start_timer, progress = self.animate_slider(
                self.slider_pressed_start_timer,
                self.pressed_slider_start_length,
                self.x_position,
                self.pressed_x_position,
                self.slider,
                self.shadow_radius * 2,
            )
        elif self.slider == 'up' or self.slider == 'down':
            self.slider_pressed_start_timer, progress = self.animate_slider(
                self.slider_pressed_start_timer,
                self.pressed_slider_start_length,
                self.y_position,
                self.pressed_y_position,
                self.slider,
                self.shadow_radius * 2,
            )

    def slider_pressed_end_animation(self):
        """
        Animate the slider when the button is no longer pressed.
        """
        if self.slider is None:
            return
        
        if self.slider == 'left' or self.slider == 'right':
            self.slider_pressed_end_timer, progress = self.animate_slider(
                self.slider_pressed_end_timer,
                self.pressed_slider_end_length,
                self.x_position,
                self.default_x_position,
                self.slider,
                self.shadow_radius * 2,
            )
        elif self.slider == 'up' or self.slider == 'down':
            self.slider_pressed_end_timer, progress = self.animate_slider(
                self.slider_pressed_end_timer,
                self.pressed_slider_end_length,
                self.y_position,
                self.default_y_position,
                self.slider,
                self.shadow_radius * 2,
            )
    
    # ----------------------------------- Menu transition animations -----------------------------------
       
    def do_menu_enter_transition_animation(self):
        """
        Start the menu enter transition animation.
        """
        self.do_menu_enter_transition = True
    
    def do_menu_leave_transition_animation(self):
        """
        Start the menu leave transition animation.
        """
        self.do_menu_leave_transition = True
    
    def animate_menu_enter_transition(self):
        """
        Animate the menu transition when entering the menu.
        """
        if not self.do_menu_enter_transition:
            return
        
        self.animate_menu_transition(True)
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_enter_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_leave_transition(self):
        """
        Animate the menu transition when leaving the menu.
        """
        if not self.do_menu_leave_transition:
            return
        
        self.animate_menu_transition(False)
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_leave_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_transition(self, is_enter):
        """
        Animate the menu transition.
        
        args:
            is_enter (bool): Whether the transition is entering or leaving the menu.
        """
        if not (self.do_menu_enter_transition or self.do_menu_leave_transition):
            return
    
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
        
        if self.state != 'pressed':
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
        else:
            self.menu_transition_timer += self.Timing.frame_delta_time
            self.menu_transition_timer = min(self.menu_transition_timer, self.menu_transition_time)

            progress = self.menu_transition_timer / self.menu_transition_time
            progress = max(0, min(1, progress))
            
        self.animate_menu_transition_alpha(progress, is_enter)

    def animate_menu_transition_alpha(self, progress, is_enter):
        """
        Animate the alpha of the button surface during a menu transition.
        
            progress (float): Progress percentage of the animation.
            is_enter (bool): Whether the transition is entering or leaving the menu.
        """
        p = smoothstep(progress)
        alpha = ((p) * 255) if is_enter else (((1 - p)) * 255)
        alpha = max(0, min(255, alpha))
        
        self.button_surface.set_alpha(alpha)
        self.hover_surface.set_alpha(alpha)
        self.pressed_surface.set_alpha(alpha)
        self.shadow_surface.set_alpha(alpha)
    
    def check_if_on_screen(self):
        """
        Check if the panel is on screen
        """
        if self.rect.bottom > 0 and self.rect.top < self.on_screen_rect.height:
            self.on_screen = True
            return
        self.on_screen = False
        self.reset_state()
    
    # ------------------------------------------------- TOOLTIPS -------------------------------------------------
    
    def init_tooltip(self, definition):
        if definition is None:
            return
        
        if self.ToolTips is None:
            return
        
        if 'tooltip' not in definition:
            return
        
        self.tooltip = definition['tooltip']
        self.ToolTips.add_tooltip(self.tooltip)
    
    def draw_tooltip(self):
        if self.tooltip is None:
            return
        
        if self.ToolTips is None:
            return
        
        self.ToolTips.draw_tooltip(self.tooltip)
        
    def play_hover_sound(self):
        if self.Sound is None:
            return
        
        if self.hover_sound is None:
            return
        
        if self.previous_state is not None:
            return
        
        self.Sound.sfx_queue.append(self.hover_sound)
    
    def play_click_sound(self):
        if self.Sound is None:
            return
        
        if self.click_sound is None:
            return
        
        self.Sound.sfx_queue.append(self.click_sound)