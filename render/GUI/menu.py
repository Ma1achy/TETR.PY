import pygame
import json
from render.GUI.menu_elements.header import Header
from render.GUI.menu_elements.footer import Footer
from render.GUI.main_body import MainBody
from render.GUI.buttons.footer_button import FooterButton
from render.GUI.font import Font
import re

class Menu():
    def __init__(self, surface, Timing, Mouse, RenderStruct, button_functions, menu_definition):
        """
        A menu object
        
        args:
            surface (pygame.Surface): The surface to draw the menu on
            Timing (Timing): The Timing object
            Mouse (Mouse): The Mouse object
            button_functions (dict): The functions for the buttons
            menu_definition (str): The path to the definition file for the menu
        """
        self.surface = surface
        self.Timing = Timing
        self.Mouse = Mouse
        self.RenderStruct = RenderStruct
        self.RENDER_SCALE = self.RenderStruct.RENDER_SCALE
        self.button_functions = button_functions
        
        self.header_height = 0
        self.footer_height = 0
        
        self.footer_widgets = []

        self.__open_definition(menu_definition)
        self.__init_elements()
        
        self.transition_animation_timer = 0
        self.doing_transition_animation = False
        
    def __open_definition(self, path):
        """
        Open the definition file for the menu
        
        args:
            path (str): The path to the definition file
        """
        with open(path, 'r') as f:
            self.definition = json.load(f)
               
    def __init_elements(self):
        """
        Initialise the elements of the menu
        """
        self.__init__tooltips()
        self.__init_header()
        self.__init_footer()  
        self.__init_menu_body()
        self.__init_footer_widgets()
    
    def __init_header(self):
        """
        Initialise the header of the menu
        """
        if 'menu_header' not in self.definition:
            return
        
        self.header_height = int(70 * self.RENDER_SCALE) if 'height' not in self.definition['menu_header'] else int(self.definition['menu_header']['height'] * self.RENDER_SCALE)
        self.menu_header = Header(self.surface.get_rect(), self.header_height, self.definition['menu_header'], image = self.__init_header_image(), RENDER_SCALE = self.RENDER_SCALE)
    
    def __init_footer(self):
        """
        Initialise the footer of the menu
        """
        if 'menu_footer' not in self.definition:
            return
        
        self.footer_height = int(55 * self.RENDER_SCALE) if 'height' not in self.definition['menu_footer'] else int(self.definition['menu_footer']['height'] * self.RENDER_SCALE)
        self.menu_footer = Footer(self.surface.get_rect(), self.footer_height, self.definition['menu_footer'], image = self.__init_footer_image(), RENDER_SCALE = self.RENDER_SCALE)
    
    def __init_footer_image(self):
        """
        Get the image for the footer
        """
        if 'image' in self.definition['menu_footer']:
            return self.definition['menu_footer']['image']
        return None
    
    def __init_header_image(self):
        """
        Get the image for the header
        """
        if 'image' in self.definition['menu_header']:
            return self.definition['menu_header']['image']
        return None
    
    def __init_menu_body(self):
        """
        Initialise the body of the menu
        """
        if 'menu_body' not in self.definition:
            return
            
        self.main_body_rect = pygame.Rect(0, self.header_height, self.surface.get_width(), self.surface.get_height() - self.footer_height - self.header_height)
        self.main_body = MainBody(self.Mouse, self.Timing, self.ToolTips, self.main_body_rect, self.button_functions, self.definition['menu_body'], parent = None, RENDER_SCALE = self.RENDER_SCALE)
    
    def __init__tooltips(self):
        if 'menu_body' not in self.definition:
            return
        
        if 'tooltips' not in self.definition['menu_body']:
            self.ToolTips = None
            return
    
        if not self.definition['menu_body']['tooltips']:
            self.ToolTips = None
            return
        
        self.ToolTips = ToolTips(self.Mouse, self.Timing, self.surface, self.RENDER_SCALE)
        
    def __init_footer_widgets(self):
        """
        Initialise the footer widgets of the menu
        """
        if "footer_widgets" not in self.definition:
            return
            
        for element in self.definition["footer_widgets"]['elements']:
            if element['type'] == 'footer_button':
                func = self.button_functions[element['function']]
                self.footer_widgets.append(FooterButton(self.Timing, func, self.Mouse, self.surface, self.surface.get_rect(), element, parent = None, RENDER_SCALE = self.RENDER_SCALE))
    
    def update_tooltips(self):
        if self.ToolTips is None:
            return
        
        self.ToolTips.update()
           
    def update(self, in_dialog):
        """
        Update the menu
        
        args:
            in_dialog (bool): Whether the menu is in a dialog
        """
        self.count_transition_animation()
        self.main_body.update(in_dialog)
        self.draw(self.surface)
        self.update_footer_widgets(in_dialog)
        self.update_tooltips()
            
    def handle_window_resize(self):
        """
        Handle the window resize
        """
        self.__header_resize()
        self.__footer_resize()
        self.__menu_body_resize()
        self.__footer_widgets_resize()

    def __header_resize(self):
        """
        Resize the header
        """
        if 'menu_header' not in self.definition:
            return
        
        self.menu_header.container = self.surface.get_rect()
        self.menu_header.handle_window_resize()
    
    def __footer_resize(self):
        """
        Resize the footer
        """
        if 'menu_footer' not in self.definition:
            return
        
        self.menu_footer.container = self.surface.get_rect()
        self.menu_footer.handle_window_resize()
    
    def __menu_body_resize(self):
        """
        Resize the body of the menu
        """
        if 'menu_body' not in self.definition:
            return
        
        self.main_body.rect = pygame.Rect(0, self.header_height, self.surface.get_width(), self.surface.get_height() - self.footer_height - self.header_height)
        
        if self.main_body.rect.height <= 0: # to prevent crash
            self.main_body.rect.height = 1
        
        if self.main_body.rect.width <= 0:
            self.main_body.rect.width = 1
                 
        self.main_body.handle_window_resize()
    
    def __footer_widgets_resize(self):
        """
        Resize the footer widgets
        """
        if "footer_widgets" not in self.definition:
            return 
        
        for widget in self.footer_widgets:
            widget.container = self.surface.get_rect()
            widget.handle_window_resize()
    
    def update_footer_widgets(self, in_dialog):
        """
        Update the footer widgets
        
        args:
            in_dialog (bool): Whether the menu is in a dialog
        """
        if "footer_widgets" not in self.definition:
            return
        
        for widget in self.footer_widgets:
            widget.update(in_dialog)
    
    def reset_state(self):
        """
        Reset the state of the menu
        """
        if 'menu_body' in self.definition:
            self.main_body.reset_buttons()
        
        if 'footer_widgets' in self.definition:
            for widget in self.footer_widgets:
                widget.reset_state()
          
    def draw(self, surface):
        """
        Draw the menu
        
        args:
            surface (pygame.Surface): The surface to draw the menu on
        """ 
        if 'menu_body' in self.definition:
            self.main_body.draw(surface)
        
        if 'menu_footer' in self.definition:
            self.menu_footer.draw(surface)
        
        if 'menu_header' in self.definition:    
            self.menu_header.draw(surface)
        
        surface.blit(self.surface, (0, 0))
        
    def do_menu_enter_transition_animation(self, animate_back_button, animate_footer_widgets):
        """
        Start the menu enter transition animation
        
        args:
            animate_back_button (bool): Whether to animate the back button
            animate_footer_widgets (bool): Whether to animate the footer widgets
        """
        if 'menu_body' in self.definition:
            self.main_body.do_menu_enter_transition_animation(animate_back_button)
        
        if 'footer_widgets' in self.definition and animate_footer_widgets:
            for widget in self.footer_widgets:
                widget.do_menu_enter_transition_animation()
                
        self.doing_transition_animation = True
    
    def do_menu_leave_transition_animation(self, animate_back_button, animate_footer_widgets):
        """
        Start the menu leave transition animation
        
        args:
            animate_back_button (bool): Whether to animate the back button
            animate_footer_widgets (bool): Whether to animate the footer widgets
        """
        if 'menu_body' in self.definition:
            self.main_body.do_menu_leave_transition_animation(animate_back_button)
        
        if 'footer_widgets' in self.definition and animate_footer_widgets:
            for widget in self.footer_widgets:
                widget.do_menu_leave_transition_animation()
                
        self.doing_transition_animation = True
 
    def count_transition_animation(self):
        """
        Count the transition animation
        """
        if not self.doing_transition_animation:
            return
        
        self.transition_animation_timer += self.Timing.frame_delta_time
            
        if self.transition_animation_timer >= 0.19 - self.Timing.frame_delta_time:
                
            self.doing_transition_animation = False
            self.transition_animation_timer = 0

class ToolTips():
    def __init__(self, Mouse, Timing, surface, RENDER_SCALE):
        """
        Tooltips for the menu
        
        args:
            Mouse (Mouse): The Mouse object
            Timing (Timing): The Timing object
            surface (pygame.Surface): The surface to draw the tooltips on
            RENDER_SCALE (int): The render scale
        """
        self.Mouse = Mouse
        self.Timing = Timing
        self.surface = surface
        self.RENDER_SCALE = RENDER_SCALE
        
        self.tooltips = {}
        self.tooltip_to_draw = None
        
        self.max_width = int(300 * self.RENDER_SCALE)
        
        self.font = Font('cr', int(15 * self.RENDER_SCALE))
        
    def add_tooltip(self, tooltip):
        """
        Add a tooltip
        
        args:
            tooltip (str): The tooltip to add
        """
        if tooltip in self.tooltips:
            return
        
        self.tooltips[tooltip] = self.render_tooltop(tooltip)
        
    def render_tooltop(self, tooltip):
        """
        Render a tooltip
        
        args:
            tooltip (str): The tooltip to render
        """
        text = self.__wrap_text(tooltip, self.font.font, self.max_width)
        
        if text is None:
            return pygame.Surface((1, 1), pygame.HWSURFACE|pygame.SRCALPHA)
        
        width = 0
        height = 0
        
        for line in text:
            width = max(width, self.font.font.size(line)[0])
            height += self.font.font.size(line)[1]
        
        tooltip_surface = pygame.Surface((width + int(10 * self.RENDER_SCALE), height + int(10 * self.RENDER_SCALE)), pygame.HWSURFACE|pygame.SRCALPHA)
        tooltip_surface.fill((32, 32, 32, 200))
        pygame.draw.rect(tooltip_surface, (255, 255, 255, 64), tooltip_surface.get_rect(), int(2 * self.RENDER_SCALE))
        
        for i, line in enumerate(text):
            self.font.draw(tooltip_surface, line, "#ffffff", 'left_top', int(5 * self.RENDER_SCALE), i * self.font.font.size(line)[1] - int(2.5 * self.RENDER_SCALE))
        
        return tooltip_surface

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
        
        words = re.split(r"(\s+)", text)
        lines = []
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
            
    def draw_tooltip(self, tooltip):
        """
        Draw a tooltip
        
        args:
            tooltip (str): The tooltip to draw
        """
        self.tooltip_to_draw = self.tooltips[tooltip]
    
    def update(self):
        """
        Update the tooltips
        """
        if self.tooltip_to_draw is None:
            return
        
        self.draw()
        self.tooltip_to_draw = None
        
    def draw(self):
        pos = self.Mouse.position
        offset = int(12 * self.RENDER_SCALE)

        pos = (pos[0] + offset, pos[1] + offset)
        
        if pos[0] + self.tooltip_to_draw.get_width() > self.surface.get_width():
            pos = (pos[0] - self.tooltip_to_draw.get_width() - 2 * offset, pos[1])
        
        if pos[1] + self.tooltip_to_draw.get_height() > self.surface.get_height():
            pos = (pos[0], pos[1] - self.tooltip_to_draw.get_height() - 2 * offset)
        
        self.surface.blit(self.tooltip_to_draw, pos)
    
       
        
        
    
    
    