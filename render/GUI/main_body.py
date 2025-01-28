import pygame
from utils import smoothstep_interpolate, draw_linear_gradient, draw_solid_colour, smoothstep_interpolate
from render.GUI.buttons.button_bar_main import ButtonBarMain
from render.GUI.buttons.button_bar_sub import ButtonBarSub
from render.GUI.buttons.back_button import BackButton
from render.GUI.buttons.collapsible_panel_header import CollapsiblePanelHeader
from render.GUI.menu_elements.floating_text import FloatingText
from render.GUI.menu_elements.scrollbar import ScrollBar
from render.GUI.menu_elements.logo import Logo
from app.input.mouse.mouse import MouseEvents
from render.GUI.menu_elements.collapsible_panel import CollapsiblePanel
from render.GUI.menu_elements.nested_element import NestedElement
from render.GUI.menu_elements.panel import Panel

class MainBody(NestedElement):
    def __init__(self, Mouse, Timing, ToolTips, Sound, rect, button_functions, dialog_resources, definition, parent, RENDER_SCALE = 1):
        super().__init__(parent)
        """
        The main body of the menu
        
        args:
            Mouse (Mouse): the Mouse object
            Timing (Timing): the Timing object
            rect (pygame.Rect): the rect of the main body
            button_functions (dict): the functions of the buttons
            definition (dict): the definition of the main body
            parent (Object): the parent UI element
        """
        self.Mouse = Mouse
        self.Timing = Timing
        self.ToolTips = ToolTips
        self.Sound = Sound
        
        self.RENDER_SCALE = RENDER_SCALE
        
        self.button_functions = button_functions
        self.dialog_resources = dialog_resources
        self.definition = definition
        
        self.rect = rect
        
        self.scroll_speed = 10
        self.scroll_y = 0
        self.y_diff = 0
        
        self.old_content_height = 0
        self.content_height = 0
        
        self.scrollable = False
        self.scroll_bar = None
        self.scroll_started = False
        self.scroll_timer = 0
        self.scroll_timer_duration = 0.1
        
        self.doing_transition_animation = False
        self.do_reset_scroll_animation = False
        self.animation_timer = 0
        self.reset_scroll_timer = 0
        self.reset_scroll_length = 0.35
        
        self.back_button = None
        
        if 'dropdown' in definition:
            self.dropdown = self.definition['dropdown']
        else:
            self.dropdown = False
         
        self.__get_rect_and_surface()
        self.__init_elements()
        self.render()
    
    def get_local_position(self):
        """
        Get the position of the panel relative to the container it is in for collision detection.
        """
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the panel
        """
        if self.rect.width <=0:
            self.rect.width = 1
            
        if self.rect.height <= 0:
            self.rect.height = 1
            
        self.body_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)

    def __init_elements(self):
        """
        Initialize the elements of the panel
        """
        self.menu_elements = []
        self.__init_menu_elements()
        self.__init_back_button()
        self.__init_logo()
    
    def __init_menu_elements(self):
        """
        Initialize the elements of the menu
        """
        if 'menu' not in self.definition:
            return
        
        y = int(35 * self.RENDER_SCALE)
        
        if self.dropdown:
            y += int(70 * self.RENDER_SCALE)
        
        for idx, element in enumerate(self.definition['menu']['elements']):
            if element['type'] == 'bar_button':
                y += int(10 * self.RENDER_SCALE)
                func = self.button_functions[element['function']]
                button = ButtonBarMain(func, self.Mouse, self.Timing, self.Sound, self.body_surface, self.rect, element, y, height = int(120 * self.RENDER_SCALE), parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                button.y_position = y
                self.menu_elements.append(button)
                y += button.height + int(10 * self.RENDER_SCALE)
                
            elif element['type'] == 'bar_button_sub':
                y += int(7 * self.RENDER_SCALE)
                func = self.button_functions[element['function']] 
                button = ButtonBarSub(func, self.Mouse, self.Timing, self.Sound, self.body_surface, self.rect, element, y, height = int(90 * self.RENDER_SCALE), parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                button.y_position = y
                self.menu_elements.append(button)
                y += button.height + int(7 * self.RENDER_SCALE)
            
            elif element['type'] == 'panel':
                y += int(7 * self.RENDER_SCALE)
                panel = Panel(self.button_functions, self.Timing, self.Mouse, self.Sound, self.body_surface, self.rect, element, y_position = y, parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                self.menu_elements.append(panel)
                
                y += panel.height + int(7 * self.RENDER_SCALE)
                
            elif element['type'] == 'collapsible_panel_header':
                y += int(7 * self.RENDER_SCALE)
                panel = CollapsiblePanelHeader(self.Timing, self.Mouse, self.Sound, self.body_surface, self.rect, element, y, parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                self.menu_elements.append(panel)
                y += panel.height + int(7 * self.RENDER_SCALE)
            
            elif element['type'] == 'collapsible_panel':
       
                panel = CollapsiblePanel(self.button_functions, self.dialog_resources, self.Timing, self.Mouse, self.Sound, self.body_surface, self.rect, element, y_position = y, linked_header = self.menu_elements[idx - 1], parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                self.menu_elements.append(panel)
            
            elif element['type'] == 'floating_text':
                y += int(3 * self.RENDER_SCALE)
                text = FloatingText(self.Timing, self.body_surface, element['content'], y, RENDER_SCALE = self.RENDER_SCALE)
                self.menu_elements.append(text)
                y += text.height + int(3 * self.RENDER_SCALE)
        
        self.content_height = y
        self.y_diff = y - self.rect.height
        self.scrollable = self.y_diff > 0

        if self.scrollable:
            self.scroll_bar = ScrollBar(self.Mouse, self.body_surface, self.scroll_y, self.y_diff, self.scrollable, self.RENDER_SCALE)
                        
    def __init_back_button(self):
        """
        Initialize the back button
        """
        if 'back_button' not in self.definition:
            return
        
        func = self.button_functions[self.definition['back_button']['function']]
        self.back_button = BackButton(func, self.Mouse, self.Timing, self.Sound, self.body_surface, self.rect, self.definition['back_button'], parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
    
    def __init_logo(self):
        """
        Initialize the logo
        """
        if 'logo' not in self.definition:
            return
        
        self.logo = Logo(self.body_surface.get_rect(), self.definition['logo'], self.RENDER_SCALE)
 
    def render(self):
        """
        Render the panel
        """
        self.render_logo()
        self.render_menu()
        self.render_back_button()
        
    def render_logo(self):
        """
        Render the logo
        """
        if 'logo' not in self.definition:
            return
    
        self.logo.draw(self.body_surface)
    
    def render_menu(self):    
        """
        Render the menu
        """
        if 'menu' not in self.definition:
            return
        
        for element in self.menu_elements:
            element.draw()
    
    def render_back_button(self):
        """
        Render the back button
        """
        if 'back_button' not in self.definition:
            return
        
        self.back_button.draw()
    
    def draw_background(self):
        """
        Draw the background of the panel
        """
        if 'background' not in self.definition:
            return
        
        if self.definition['background']['style'] == 'linear_gradient':
            draw_linear_gradient(self.body_surface, self.definition['background']['colours'][0], self.definition['background']['colours'][1], self.body_surface.get_rect())
        elif self.definition['background']['style'] == 'solid':
            draw_solid_colour(self.body_surface, self.definition['background']['colour'], self.body_surface.get_rect())
                
    def draw(self, surface):
        """
        Draw the panel
        
        args:
            surface: Surface to draw the panel on
        """
        surface.blit(self.body_surface, self.rect.topleft)
        self.body_surface.fill((0, 0, 0, 0))
        self.draw_background()
       
    def handle_window_resize(self):
        """
        Handle the window being resized
        """
        self.__get_rect_and_surface()
        self.__init_elements()
        self.render()

    def __handle_mouse_scroll(self):
        """
        Handle the mouse scroll event
        """
        if not self.scrollable:
            return
        
        if self.Mouse.in_dialog:
            return
        
        if self.Mouse.in_dropdown and not self.dropdown:
            return
        
        events_to_remove = []
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button is MouseEvents.SCROLLWHEEL:
                    events_to_remove.append(event)
                    self.scroll_started = True
                    self.Mouse.ignore_events = True
                    self.do_scroll(info)
                    
        self.end_scroll(events_to_remove)

        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def do_scroll(self, info):
        """
        Do the mouse scroll event
        
        args:
            info (dict): The information about the scroll event
        """
        if self.Mouse.in_dialog:
            return
        
        if self.Mouse.in_dropdown and not self.dropdown:
            return
        
        if self.doing_transition_animation or self.do_reset_scroll_animation:
            return
        
        self.scroll_timer += self.Timing.frame_delta_time
        self.scroll_speed += 50

        if self.scroll_speed >= 1000:
            self.scroll_speed = 1000

        dir = info['y'] if not info['inverted'] else -info['y']
        
        if self.scroll_y <= -self.y_diff - 10 and dir < 0:
            return
        
        self.scroll_y += (dir) * (self.scroll_speed)
        
    def end_scroll(self, events_to_remove):
        """
        End the mouse scroll event
        """
        if not self.scroll_started:
            return
        
        self.scroll_timer -= self.Timing.frame_delta_time
        progress = self.scroll_timer / self.scroll_timer_duration
        
        if self.scroll_timer < 0:
            self.scroll_timer = 0
            self.scroll_started = False
            self.Mouse.ignore_events = False
            
        self.scroll_speed = smoothstep_interpolate(self.scroll_speed, 10, (1 - progress))    
        
    def __update_scroll_position(self):
        """
        Update the scroll position
        """
        if not self.scrollable:
            self.scroll_y = 0  # Reset scroll position if not scrollable
            return

        if self.scroll_y > 0:
            self.scroll_y = 0
            
        elif self.scroll_y < -self.y_diff - 35:
            self.scroll_y = -self.y_diff - 35  # Clamp scroll position to valid range
        
    def update(self):
        """
        Update the panel
        """
        self.__update_scroll_position()
        self.__update_y_positions()
        self.__handle_mouse_scroll()
        self.__update_logo()
        self.__update_menu()
        self.__update_back_button()
        self.__update_scroll_bar()
        self.__do_reset_scroll_animation()
    
    def __update_y_positions(self):
        """
        Update the y positions of the elements
        """
        self.old_content_height = self.content_height
        y = int(35 * self.RENDER_SCALE) 
        
        if self.dropdown:
            y += int(70 * self.RENDER_SCALE)
            
        for element in self.menu_elements:
            element.scroll_y = self.scroll_y
            
            if isinstance(element, ButtonBarMain):
                y += int(10 * self.RENDER_SCALE)
                element.y_position = y 
                y += element.height + int(10 * self.RENDER_SCALE)
            
            elif isinstance(element, ButtonBarSub):
                y += int(7 * self.RENDER_SCALE)
                element.y_position = y
                y += element.height + int(7 * self.RENDER_SCALE)
            
            elif isinstance(element, Panel):
                y += int(7 * self.RENDER_SCALE)
                element.y_position = y 
                y += element.height + int(7 * self.RENDER_SCALE)
                
            elif isinstance(element, CollapsiblePanelHeader):
                y += int(7 * self.RENDER_SCALE)
                element.y_position = y 
                y += element.height + int(7 * self.RENDER_SCALE)
            
            elif isinstance(element, CollapsiblePanel):
                if element.open:
                    y -= int(10 * self.RENDER_SCALE)
                    element.y_position = y
                    y += element.height + int(7 * self.RENDER_SCALE)
            
            elif isinstance(element, FloatingText):
                y += int(3 * self.RENDER_SCALE)
                element.y_position = y 
                y += element.height + int(3 * self.RENDER_SCALE)
             
        self.content_height = y
        self.y_diff = y - self.body_surface.get_rect().height
        self.scrollable = self.y_diff > 0 

        if self.old_content_height != self.content_height and self.scrollable:
            self.scroll_bar = ScrollBar(self.Mouse, self.body_surface, self.scroll_y, self.y_diff, self.scrollable, self.RENDER_SCALE)
        
        elif not self.scrollable:
            self.scroll_bar = None
            
    def __update_menu(self):
        """
        Update the menu elementsg
        """
        if 'menu' not in self.definition:
            return
        
        for element in self.menu_elements: 
            element.update()
            
    def __update_back_button(self):
        """
        Update the back button
        """
        if 'back_button' not in self.definition:
            return
        
        self.back_button.update()

    def __update_logo(self):
        """
        Update the logo
        """
        if 'logo' not in self.definition:
            return

        self.logo.draw(self.body_surface)
    
    def __update_scroll_bar(self):
        """
        Update the scroll bar
        """
        if self.scroll_bar is None:
            return
        
        self.scroll_bar.update(self.scroll_y)

    def reset_buttons(self):
        """
        Reset the buttons
        """
        if 'menu' in self.definition:
            for element in self.menu_elements:
                element.reset_state()
        
        if 'back_button' in self.definition:
            self.back_button.reset_state()
    
    def do_menu_enter_transition_animation(self, animate_back_button):
        """
        Start the menu enter transition animation
        
        args:
            animate_back_button (bool): Whether to animate the back button
        """
        if 'menu' in self.definition:
            for element in self.menu_elements:
                element.do_menu_enter_transition_animation()
        
        if 'back_button' in self.definition and animate_back_button:
            self.back_button.do_menu_enter_transition_animation()
                 
    def do_menu_leave_transition_animation(self, animate_back_button):
        """
        Start the menu leave transition animation
        
        args:
            animate_back_button (bool): Whether to animate the back button
        """
        if 'menu' in self.definition:
            for element in self.menu_elements:
                element.do_menu_leave_transition_animation()
        
        if 'back_button' in self.definition and animate_back_button:
            self.back_button.do_menu_leave_transition_animation()
            
    def menu_enter_reset_scroll(self):
        """
        Reset the scroll position
        """
        self.do_reset_scroll_animation = True
    
    def __do_reset_scroll_animation(self):
        if self.scroll_y == 0:
            self.do_reset_scroll_animation = False
            self.animation_timer = 0
            self.reset_scroll_timer = 0
            return
        
        if self.do_reset_scroll_animation:
            self.animation_timer += self.Timing.frame_delta_time
            
            if self.animation_timer <= 0.2:
                return
            
            if self.reset_scroll_timer >= self.reset_scroll_length:
                self.scroll_y = 0
                self.animation_timer = 0
                self.reset_scroll_timer = 0
                self.do_reset_scroll_animation = False
                
            self.reset_scroll_timer += self.Timing.frame_delta_time
            progress = self.reset_scroll_timer / self.reset_scroll_length
            progress = max(0, min(1, progress))
            self.scroll_y = smoothstep_interpolate(self.scroll_y, 0, progress)
    
    
        
        
        
                    
                
                