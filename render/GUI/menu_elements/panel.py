import pygame
import re
from utils import draw_border, draw_solid_colour, apply_gaussian_blur_with_alpha, smoothstep, smoothstep_interpolate
from render.GUI.menu_elements.button_list import ButtonList
from render.GUI.menu_elements.nested_element import NestedElement
from render.GUI.menu_elements.config_slider import ConfigSlider
from render.GUI.buttons.checkbox_button import CheckboxButton
from render.GUI.buttons.start_button import StartButton
from render.GUI.font import Font
from render.GUI.buttons.generic_button import GenericButton
from render.GUI.buttons.music_selector_button import MusicSelectorButton
from app.core.config_manager import VideoSettings

class Panel(NestedElement):
    def __init__(self, button_functions, Timing, Mouse, Sound, surface, container, definition, y_position, parent, RENDER_SCALE = 1, ToolTips = None):
        super().__init__(parent = parent)
        """
        A panel that can contain other elements.
        
        args:
            Timing (Timing): the Timing object
            Mouse (Mouse): the Mouse object
            surface (pygame.Surface): the surface to draw the panel on
            container (pygame.Rect): the container the panel is in
            definition (dict): the definition of the panel
            y_position (int): the y position of the panel
            parent (Object): the parent UI element
        """
        self.button_functions = button_functions
        self.RENDER_SCALE = RENDER_SCALE
        self.ToolTips = ToolTips
        
        self.Timing = Timing
        self.Mouse = Mouse
        self.Sound = Sound
        
        self.surface = surface
        self.container = container
        self.definition = definition
        
        self.scroll_y = 0
        self.y_position = y_position
        self.x_position = self.container.width // 6
    
        self.elements = []
        
        self.width = self.container.width - self.container.width // 3
        self.height = int(200 * self.RENDER_SCALE)
        
        self.shadow_radius = int(5 * self.RENDER_SCALE)
        
        self.title_font = Font('d_din_bold', int(45 * self.RENDER_SCALE))
        self.body_font = Font('hun2', int(22 * self.RENDER_SCALE))
        
        self.title_text = None
        self.title_colour = None
        
        self.body_text_lines = []
        self.body_text = None
        self.body_colour = None
        
        self.__get_body()
        self.__get_title()
        self.__get_height()
        self.__get_rect_and_surface()
        self.__init_elements()
        self.render()
        
        self.default_x_position = self.container.width // 6
        
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
        self.menu_transition_timer = 0
        self.menu_transition_time = 0.2
        
        self.on_screen = False
        
        self.currently_hovered = False
        self.previous_hovered = False
        self.use_cached_image = False
        
        self.on_screen_rect = self.surface.get_rect()
        self.create_inital_cached_image()
        
        if 'always_update' in self.definition and self.definition['always_update']:
            self.always_update = True
        else:
            self.always_update = False
        
    def get_local_position(self):
        """
        Get the position of the panel relative to the container it is in for collision detection.
        """
        return self.rect.topleft
    
    def __get_rect_and_surface(self):
        """
        Get the rects and surfaces for the panel
        """
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
        self.panel_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.element_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.shadow_rect = pygame.Rect(self.x_position - self.shadow_radius * 2, self.y_position - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE|pygame.SRCALPHA)
        
        self.collision_rect = pygame.Rect(self.get_screen_position(), (self.width, self.height))
        
        self.cached_surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE|pygame.SRCALPHA)
    
    def __get_title(self):
        if 'title' not in self.definition:
            return
        
        self.title_text = self.definition['title']['display_text']
        self.title_colour = self.definition['title']['colour']
    
    def __get_body(self):
        if 'body_text' not in self.definition:
            return
        
        self.body_text = self.definition['body_text']['display_text']
        self.body_colour = self.definition['body_text']['colour']
        
        self.body_text_lines = self.__wrap_text(self.body_text, self.body_font.font, self.width - int(50 * self.RENDER_SCALE))
          
    def __get_height(self):
        """
        Get the height of the panel based on the elements in it
        """
        self.__get_rect_and_surface()
        height = self.__init_elements()
        self.height = height
        
    def __init_elements(self):
        """
        Initialise the elements in the panel
        """
        self.elements = []
         
        y = 0
        
        if 'title' in self.definition:
            y += int(70 * self.RENDER_SCALE)
            
        for line in self.body_text_lines:
            y += self.body_font.font.size(line)[1] + int(2 * self.RENDER_SCALE)
        
        for element in self.definition['elements']:
            
            if element['type'] == "button_list":
                button_list = ButtonList(self.button_functions, self.Timing, self.Mouse, self.Sound, self.element_surface, self.rect, element, y_position = y, parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                self.elements.append(button_list)
                y += button_list.height
            
            elif element['type'] == "config_slider":
                config_slider = ConfigSlider(self.button_functions, self.Timing, self.Mouse, self.Sound, self.element_surface, self.rect, element, y_position = y, parent = self, RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                self.elements.append(config_slider)
                y += config_slider.height
            
            elif element['type'] ==  "checkbox":
                checkbox = CheckboxButton(self.button_functions, self.Timing, self.Mouse, self.Sound, self.element_surface, self.rect, element, y_position = y, parent = self, background_colour = self.definition['background']['colour'], RENDER_SCALE = self.RENDER_SCALE, ToolTips = self.ToolTips)
                self.elements.append(checkbox)
                y += checkbox.height - int(12 * self.RENDER_SCALE)
            
            elif element['type'] == "start_button":
                function = self.button_functions[element['function']]
                start_button = StartButton(self.Timing, self.Mouse, self.Sound, self.element_surface, self.panel_surface.get_rect(), element, function, self, self.RENDER_SCALE, self.ToolTips)
                self.elements.append(start_button)
                y += start_button.height
                y -= int(25 * self.RENDER_SCALE)
            
            elif element['type'] == "generic_button":
                function = None
                button = GenericButton(self.Timing, self.Mouse, self.Sound, self.element_surface, self.panel_surface.get_rect(), element, function, self, self.RENDER_SCALE, self.ToolTips)
                
                surf = button.shadow_surface
                temp = pygame.Surface((surf.get_width(), surf.get_height()), pygame.HWSURFACE|pygame.SRCALPHA)
                temp.fill(self.definition['background']['colour'])
                temp.blit(surf, (0, 0))
                button.shadow_surface = temp
                
                self.elements.append(button)
                y -= int(10 * self.RENDER_SCALE)   
            
            elif element['type'] == "music_selector_button":
                function = self.button_functions[element['function']]
                music_selector_button = MusicSelectorButton(self.Timing, self.Mouse, self.Sound, self.element_surface, self.panel_surface.get_rect(), element, function, self, self.RENDER_SCALE, self.ToolTips)
                self.elements.append(music_selector_button)
                y -= int(10 * self.RENDER_SCALE)
                
            y += int(10 * self.RENDER_SCALE)
    
        y += int(15 * self.RENDER_SCALE)
        
        return y   
      
    def render(self):
        """
        Render the panel and its shadow
        """
        self.render_shadow()
        self.render_panel()
    
    def render_panel(self):
        """
        Render the panel
        """
        draw_solid_colour(self.panel_surface, self.definition['background']['colour'], self.panel_surface.get_rect())
        draw_border(self.panel_surface, self.definition['border'], self.panel_surface.get_rect(), self.RENDER_SCALE)
        self.draw_title()
        self.draw_body()
    
    def draw_title(self):
        """
        Draw the title of the panel
        """
        if self.title_text is None:
            return
        
        self.title_font.draw(self.panel_surface, self.title_text, self.title_colour, 'left_top', h_padding = int(25 * self.RENDER_SCALE), v_padding = int(0 * self.RENDER_SCALE))
    
    def draw_body(self):
        """
        Draw the body of the panel
        """
        if self.body_text is None:
            return
        
        title_offset = int(70 * self.RENDER_SCALE) if self.title_text is not None else 0
        
        for i, line in enumerate(self.body_text_lines):
            self.body_font.draw(self.panel_surface, line, self.body_colour, 'left_top', h_padding = int(25 * self.RENDER_SCALE), v_padding =  title_offset + i * (self.body_font.font.size(line)[1] + int(2 * self.RENDER_SCALE)))
                   
    def render_shadow(self):
        """
        Render the shadow of the panel
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
        self.shadow_surface.fill((0, 0, 0, 0), rect=[0, 0, self.shadow_surface.get_width(), self.shadow_radius * 2]) # remove the area the panel takes up from the shadow
        pygame.draw.rect(self.shadow_surface, (0, 0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.width, self.height))
              
    def draw(self):
        """
        Draw the panel and its shadow
        """                
        if not self.on_screen:
            return
        
        if self.use_cached_image:
            self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
            self.surface.blit(self.cached_surface, self.rect.topleft)
            return
        
        if VideoSettings.BACKGROUND_VISIBILITY > 0:
            self.surface.blit(self.shadow_surface, self.shadow_rect.topleft)
            
        self.panel_surface.blit(self.element_surface, (0, 0))
        self.surface.blit(self.panel_surface, self.rect.topleft)
         
    def update(self):
        """
        Update the panel
        """
        self.handle_scroll()
        self.check_if_on_screen()
        
        if not self.on_screen:
            return
        
        self.update_hover()
        
        if self.currently_hovered and not self.use_cached_image:
            self.update_elements()  
        
        self.animate_menu_enter_transition()
        self.animate_menu_leave_transition()
    
    def update_elements(self):
        """
        Update the elements in the panel
        """
        self.element_surface.fill((0, 0, 0, 0))
        
        for element in self.elements:
            element.update()
    
    def handle_scroll(self):
        """
        Handle the scrolling of the panel
        """
        self.rect.top = self.y_position + self.scroll_y
        self.shadow_rect.top = self.y_position + self.scroll_y - self.shadow_radius * 2
        self.draw()

    def reset_state(self):
        """
        Reset the state of the panel
        """
        self.menu_transition_timer = 0
        self.do_menu_enter_transition = False
        self.do_menu_leave_transition = False
    
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
        animate the menu enter transition
        """
        if not self.do_menu_enter_transition:
            return
        
        self.animate_menu_transition(True)
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_enter_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_leave_transition(self):
        """
        animate the menu leave transition
        """
        if not self.do_menu_leave_transition:
            return
        
        self.animate_menu_transition(False)
        
        if self.menu_transition_timer >= self.menu_transition_time:
            self.do_menu_leave_transition = False
            self.menu_transition_timer = 0
        
    def animate_menu_transition(self, is_enter):
        """
        Animate the menu transition 
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
            self.shadow_radius * 2
        )
            
        self.animate_menu_transition_alpha(progress, is_enter)
    
    def animate_slide(self, timer, duration, start_pos, end_pos, shadow_offset):
        """
        Animate the sliding of the panel
        
        args:
            timer (float): The timer for the animation
            duration (float): The duration of the animation
            start_pos (float): The starting position of the panel
            end_pos (float): The ending position of the panel
            shadow_offset (float): The offset for the shadow
        """
  
        timer += self.Timing.frame_delta_time
        timer = min(timer, duration)

        progress = timer / duration
        progress = max(0, min(1, progress))
        
        new_pos = smoothstep_interpolate(start_pos, end_pos, progress)

        self.x_position = new_pos
        self.rect.topleft = (self.x_position, self.y_position + self.scroll_y) 
        self.shadow_rect.topleft = (self.x_position - shadow_offset, self.y_position - shadow_offset + self.scroll_y)
       
        return timer, progress
    
    def animate_menu_transition_alpha(self, progress, is_enter):
        """
        Animate the alpha of the panel surface during a menu transition.
        
            progress (float): Progress percentage of the animation.
            is_enter (bool): Whether the transition is entering or leaving the menu.
        """
        p = smoothstep(progress)
        alpha = ((p) * 255) if is_enter else (((1 - p)) * 255)
        alpha = max(0, min(255, alpha))
        
        self.panel_surface.set_alpha(alpha)
        self.shadow_surface.set_alpha(alpha)
        self.cached_surface.set_alpha(alpha)
        self.element_surface.set_alpha(alpha)
    
    def check_if_on_screen(self):
        """
        Check if the panel is on screen
        """
        if self.rect.bottom > 0 and self.rect.top < self.on_screen_rect.height:
            self.on_screen = True
            return
        self.on_screen = False
        
    def check_hover(self):
        """
        Check if the mouse is hovering over the panel.
        """
        self.previous_hovered = self.currently_hovered
        
        if self.Mouse.in_dialog:
            self.currently_hovered = False
            return
        
        if not self.on_screen:
            self.currently_hovered = False
            return
        
        x, y = self.Mouse.position
        
        self.collision_rect.topleft = self.get_screen_position()
        
        if self.collision_rect.collidepoint((x, y)):
            self.currently_hovered = True
            return
        self.currently_hovered = False
    
    def update_hover(self):
        """
        Update the hover state of the panel
        """
        self.check_hover()
        
        if self.always_update:
            self.currently_hovered = True
            self.used_cached_image = False
            return
        
        if self.Mouse.in_dialog:
            self.create_cached_image()
            self.use_cached_image = True
            return
         
        if self.currently_hovered:
            self.use_cached_image = False
            return
        
        if not self.currently_hovered and self.previous_hovered:
            self.create_cached_image()
            self.use_cached_image = True
        
    def create_cached_image(self):
        """
        Create a cached image of the panel
        """
        if self.use_cached_image:
            return
        
        self.cached_surface.fill((0, 0, 0, 0))
        self.element_surface.fill((0, 0, 0, 0))
        
        for element in self.elements:
            element.reset_state()
            element.update()
        
        self.panel_surface.set_alpha(255)
        self.element_surface.set_alpha(255)
        self.cached_surface.blit(self.panel_surface, (0, 0))
        self.cached_surface.blit(self.element_surface, (0, 0))
        
    def create_inital_cached_image(self):
        self.update_elements()
        self.create_cached_image()
        
    def __strip_tags(self, text):
        """
        Strip colour tags from the text
        
        args:
            text (str): The text to strip the tags from
        """
        tag_pattern = r"\[colour=#[0-9A-Fa-f]{6}\]|\[\/colour\]"
        return re.sub(tag_pattern, "", text)

    def __wrap_text(self, text, font, max_width):
        """	
        Wrap text to fit inside a given width
        
        args:
            text (str): The text to wrap
            font (pygame.font.Font): The font to use
            max_width (int): The maximum width of the text
        """
        if text is None:
            return
        
        lines = []
        for paragraph in text.split('\n'):
            words = re.split(r"(\s+)", paragraph)
            current_line = ""

            for word in words:
                stripped_word = self.__strip_tags(current_line + word)
                
                if font.size(stripped_word.strip())[0] > max_width:
                    
                    if font.size(word.strip())[0] > max_width:
                        
                        while font.size(word.strip())[0] > max_width:  # Split the word if it's too long
                            for i in range(1, len(word) + 1):
                                if font.size(word[:i].strip())[0] > max_width - font.size(current_line.strip())[0]:
                                    lines.append(current_line.strip() + word[:i-1])
                                    word = word[i-1:]
                                    current_line = ""
                                    break
                                
                        current_line += word
                    else:
                        lines.append(current_line.strip())   # Add the current line to lines and start a new line with the word
                        current_line = word
                else:
                    current_line += word

            if current_line:
                lines.append(current_line.strip())

        return lines