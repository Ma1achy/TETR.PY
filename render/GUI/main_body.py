import pygame
from utils import hex_to_rgb, load_image, draw_linear_gradient, draw_solid_colour, draw_border, brightness, align_top_edge, align_bottom_edge, align_right_edge, align_left_edge, align_centre, align_bottom_left, align_bottom_right, align_top_right, align_top_left
from utils import smoothstep_interpolate, apply_gaussian_blur_with_alpha
from render.GUI.font import Font
from render.GUI.buttons.button_bar_main import ButtonBarMain
from render.GUI.buttons.button_bar_sub import ButtonBarSub
from render.GUI.buttons.back_button import BackButton
from render.GUI.buttons.collapsible_panel_header import CollapsiblePanelHeader
from render.GUI.menu_elements.floating_text import FloatingText

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

class Logo():
    def __init__(self, container, definition):
        self.container = container
        self.definition = definition
        self.width = self.container.width // 8.5
        
        self.__init_image()
        self.__align_image()
        self.image.set_alpha(self.definition['opacity'])
    
    def __init_image(self):
        self.image = load_image(self.definition['image'])  
        
        aspect_ratio = self.image.get_width() / self.image.get_height()
        new_height = int(self.width / aspect_ratio)

        self.image = pygame.transform.smoothscale(self.image, (self.width, new_height))

    def __align_image(self):
        if self.definition['alignment'] == 'bottom_left':
            self.rect = align_bottom_left(self.container, self.image.get_width(), self.image.get_height(), self.definition['padding'][0], self.definition['padding'][1])
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class ScrollBar:
    def __init__(self, container, y_scroll, y_diff, scrollable):
        self.container = container
        self.y_scroll = y_scroll 
        self.y_diff = y_diff  
        self.scrollable = scrollable  

        self.width = 30
        self.shadow_radius = 5
        self.height = container.get_rect().height

        self.get_rect_and_surface()
        self.bar = Bar(self.rect, self.y_scroll, self.y_diff, self.scrollable)
        self.render()

    def get_rect_and_surface(self):
        self.surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE | pygame.SRCALPHA)
        self.rect = pygame.Rect(
            self.container.get_rect().right - self.width,
            self.container.get_rect().top,
            self.width,
            self.height
        )
        
        self.shadow_rect = pygame.Rect(self.rect.x - self.shadow_radius * 2, self.rect.y - self.shadow_radius * 2, self.rect.width + self.shadow_radius * 4, self.rect.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE | pygame.SRCALPHA)

    def render(self):
        draw_solid_colour(self.surface, '#111111', self.surface.get_rect())
        draw_border(self.surface, {'right': [2, '#222222']}, self.surface.get_rect())
        self.render_shadow()
        
    def render_shadow(self):
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - self.shadow_radius * 4, self.shadow_rect.height - self.shadow_radius * 4))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
    def draw(self):
        self.container.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.container.blit(self.surface, self.rect.topleft)

    def update(self, y_scroll, in_dialog):
        if in_dialog:
            self.draw()
            self.bar.draw(self.container)
            return
        
        self.y_scroll = y_scroll
        self.draw()
        self.bar.update(y_scroll, self.container)

class Bar:
    def __init__(self, scrollbar_rect, y_scroll, y_diff, scrollable):
        self.scrollbar_rect = scrollbar_rect
        self.y_scroll = y_scroll
        self.y_diff = y_diff
        self.scrollable = scrollable

        self.width = scrollbar_rect.width - 12
        self.min_height = 10
        self.height = self.calculate_height()
        self.x = scrollbar_rect.x + 5
        self.y = self.calculate_position()

        self.shadow_radius = 2
        
        self.get_rect_and_surface()
        self.render()
    
    def get_rect_and_surface(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE | pygame.SRCALPHA) 
        
        self.shadow_rect = pygame.Rect(self.x - self.shadow_radius * 2, self.y - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE | pygame.SRCALPHA)
    
    def calculate_height(self):
        visible_ratio = self.scrollbar_rect.height / (self.scrollbar_rect.height + self.y_diff)
        return max(self.min_height, visible_ratio * self.scrollbar_rect.height)

    def render(self):
        self.render_shadow()
        draw_solid_colour(self.surface, '#242424', self.surface.get_rect())
        draw_border(self.surface, {'left': [2, '#3d3d3d']}, self.surface.get_rect())
        draw_border(self.surface, {'right': [2, '#181818']}, self.surface.get_rect())
        draw_border(self.surface, {'top': [2, '#3d3d3d']}, self.surface.get_rect())
        draw_border(self.surface, {'bottom': [2, '#0e0e0e']}, self.surface.get_rect())
        
    def render_shadow(self):
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
    def calculate_position(self):
        if self.y_scroll > 0:
            return 0
        
        scroll_ratio = abs(self.y_scroll) / self.y_diff  
        scroll_ratio = max(0, min(1, scroll_ratio)) 
        
        return scroll_ratio * (self.scrollbar_rect.height - self.height)
        
    def draw(self, surface):
        surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        surface.blit(self.surface, self.rect.topleft)
        
    def update(self, y_scroll, surface):
        self.y_scroll = y_scroll    
        self.y = self.calculate_position()
        self.rect.update(self.x, self.y, self.width, self.height)
        self.shadow_rect.update(self.x - self.shadow_radius * 2, self.y - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.draw(surface)


