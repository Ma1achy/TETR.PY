import pygame
from utils import smoothstep_interpolate
from render.GUI.buttons.button_bar_main import ButtonBarMain
from render.GUI.buttons.button_bar_sub import ButtonBarSub
from render.GUI.buttons.back_button import BackButton
from render.GUI.buttons.collapsible_panel_header import CollapsiblePanelHeader
from render.GUI.menu_elements.floating_text import FloatingText
from render.GUI.menu_elements.scrollbar import ScrollBar
from render.GUI.menu_elements.logo import Logo

class MainBody():
    def __init__(self, Mouse, Timing, rect, button_functions, definition):
        
        self.Mouse = Mouse
        self.Timing = Timing
        
        self.button_functions = button_functions
        self.definition = definition
        
        self.rect = rect
        self.scroll_speed = 10
        self.scroll_y = 0
        self.y_diff = 0
        self.scollable = False
        self.scroll_bar = None
        self.scroll_timer = 0
        self.scroll_timer_duration = 0.1
        
        self.__get_rect_and_surface()
        self.__init_elements()
        self.render()
       
    def __get_rect_and_surface(self):
        self.body_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE|pygame.SRCALPHA)

    def __init_elements(self):
        self.menu_elements = []
        self.__init_menu_elements()
        self.__init_back_button()
        self.__init_logo()
    
    def __init_menu_elements(self):
        if 'menu' not in self.definition:
            return
        
        y = 35
        
        for idx, element in enumerate(self.definition['menu']['elements']):
            if element['type'] == 'bar_button':
                y += 10
                func = self.button_functions[element['function']]
                button = ButtonBarMain(func, self.Mouse, self.Timing, self.body_surface, self.rect, element, y, height = 120)
                button.y_position = y
                self.menu_elements.append(button)
                y += button.height + 10
                
            elif element['type'] == 'bar_button_sub':
                y += 7
                func = self.button_functions[element['function']]
                button = ButtonBarSub(func, self.Mouse, self.Timing, self.body_surface, self.rect, element, y, height = 90)
                button.y_position = y
                self.menu_elements.append(button)
                y += button.height + 7
                
            elif element['type'] == 'collapsible_panel':
                y += 7
                panel = CollapsiblePanelHeader(self.Timing, self.Mouse, self.body_surface, self.rect, element, y)
                self.menu_elements.append(panel)
                y += panel.height + 7
            
            elif element['type'] == 'floating_text':
                y += 3
                text = FloatingText(self.body_surface, element['content'], y)
                self.menu_elements.append(text)
                y += text.height + 3
        
        if y > self.rect.height:
            self.scollable = True
        else:
            self.scollable = False
        
        self.content_height = y
        self.y_diff = y - self.rect.height

        if self.scollable:
            self.scroll_bar = ScrollBar(self.body_surface, self.scroll_y, self.y_diff, self.scollable)
                        
    def __init_back_button(self):
        if 'back_button' not in self.definition:
            return
        
        func = self.button_functions[self.definition['back_button']['function']]
        self.back_button = BackButton(func, self.Mouse, self.Timing, self.body_surface, self.rect, self.definition['back_button'])
    
    def __init_logo(self):
        if 'logo' not in self.definition:
            return
        
        self.logo = Logo(self.body_surface.get_rect(), self.definition['logo'])
 
    def render(self):
        self.render_logo()
        self.render_menu()
        self.render_back_button()
        
    def render_logo(self):
        if 'logo' not in self.definition:
            return
    
        self.logo.draw(self.body_surface)
    
    def render_menu(self):    
        if 'menu' not in self.definition:
            return
        
        for element in self.menu_elements:
            element.draw()
    
    def render_back_button(self):
        if 'back_button' not in self.definition:
            return
        
        self.back_button.draw()
    
    def draw(self, surface):
        surface.blit(self.body_surface, self.rect.topleft)
        self.body_surface.fill((0, 0, 0, 0))
       
    def handle_window_resize(self):
        self.__get_rect_and_surface()
        self.__init_elements()
        self.render()
    
    def __handle_mouse_scroll(self, in_dialog):
        
        if not self.scollable:
            return
        
        if in_dialog:
            return
        
        events_to_remove = []
        
        for event in self.Mouse.events.queue:
            for button, info in event.items():
                if button == 'scrollwheel':
                    events_to_remove.append(event)
                    self.do_scroll(info, in_dialog)
                    
        self.end_scroll(events_to_remove)

        for event in events_to_remove:
            self.Mouse.events.queue.remove(event)
    
    def do_scroll(self, info, in_dialog):
        if in_dialog:
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
        if len(events_to_remove) != 0:
            return
        
        self.scroll_timer -= self.Timing.frame_delta_time
        progress = self.scroll_timer / self.scroll_timer_duration
        
        if self.scroll_timer < 0:
            self.scroll_timer = 0
            
        self.scroll_speed = smoothstep_interpolate(self.scroll_speed, 10, (1 - progress))
    
    def __update_scroll_position(self):
        if not self.scollable:
            self.scroll_y = 0

        if self.scroll_y > 0:
            self.scroll_y = 0
            
        for element in self.menu_elements:
            element.scroll_y = self.scroll_y
            
    def update(self, in_dialog):
        self.__update_scroll_position()
        self.__handle_mouse_scroll(in_dialog)
        self.__update_logo()
        self.__update_menu(in_dialog)
        self.__update_back_button(in_dialog)
        self.__update_scroll_bar(in_dialog)
        
    def __update_menu(self, in_dialog):
        if 'menu' not in self.definition:
            return
        
        for element in self.menu_elements: # only update elements that are visible
            if element.y_position + self.scroll_y + element.height >= 0 and element.y_position  + self.scroll_y - element.height < self.rect.height:
                element.update(in_dialog)
            
    def __update_back_button(self, in_dialog):
        if 'back_button' not in self.definition:
            return
        
        self.back_button.update(in_dialog)

    def __update_logo(self):
        if 'logo' not in self.definition:
            return

        self.logo.draw(self.body_surface)
    
    def __update_scroll_bar(self, in_dialog):
        if self.scroll_bar is None:
            return
        
        self.scroll_bar.update(self.scroll_y, in_dialog)

    def reset_buttons(self):
        if 'menu' in self.definition:
            for element in self.menu_elements:
                element.reset_state()
        
        if 'back_button' in self.definition:
            self.back_button.reset_state()
