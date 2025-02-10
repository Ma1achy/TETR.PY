import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha
from render.GUI.menu_elements.nested_element import NestedElement
from app.core.config_manager import VideoSettings

class ScrollBar(NestedElement):
    def __init__(self, Mouse, container, y_scroll, y_diff, scrollable):
        """
        A scrollbar for a scrollable area
        
        args:
            container (pygame.Surface): the container the scrollbar is in
            y_scroll (int): the y scroll of the container
            y_diff (int): the difference between the height of the container and the height of the scrollable area
            scrollable (bool): whether the current menu is scrollable
        """
        super().__init__(parent = None)
        
        self.Mouse = Mouse
        
        self.container = container
        self.y_scroll = y_scroll 
        self.y_diff = y_diff  
        self.scrollable = scrollable  

        self.width = int(30 * VideoSettings.RENDER_SCALE)
        self.shadow_radius = int(5 * VideoSettings.RENDER_SCALE)
        self.height = container.get_rect().height

        self.get_rect_and_surface()
        self.bar = Bar(self.rect, self.y_scroll, self.y_diff, self.scrollable, VideoSettings.RENDER_SCALE)
        self.render()

    def get_local_position(self):
        """
        Get the position of the scrollbar relative to the container it is in for collision detection.
        """
        return self.rect.topleft
    
    def get_rect_and_surface(self):
        """
        Get the rects and surfaces for the scrollbar
        """
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
        """
        Render the scrollbar container and its shadow
        """
        draw_solid_colour(self.surface, '#111111', self.surface.get_rect())
        draw_border(self.surface, {'left': [2, '#1a1a1a']}, self.surface.get_rect(), VideoSettings.RENDER_SCALE)
        self.render_shadow()
        
    def render_shadow(self):
        """
        Render the shadow of the scrollbar container
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - self.shadow_radius * 4, self.shadow_rect.height - self.shadow_radius * 4))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
    def draw(self):
        """
        Draw the scrollbar container and its shadow
        """
        self.container.blit(self.shadow_surface, self.shadow_rect.topleft)
        self.container.blit(self.surface, self.rect.topleft)

    def update(self, y_scroll):
        """
        Update the scrollbar
        """
        if self.Mouse.in_dialog:
            self.draw()
            self.bar.draw(self.container)
            return
        
        self.y_scroll = y_scroll
        self.draw()
        self.bar.update(y_scroll, self.container)

class Bar():
    def __init__(self, scrollbar_rect, y_scroll, y_diff, scrollable, RENDER_SCALE = 1):
        
        VideoSettings.RENDER_SCALE = RENDER_SCALE
        
        self.scrollbar_rect = scrollbar_rect
        self.y_scroll = y_scroll
        self.y_diff = y_diff
        self.scrollable = scrollable

        self.width = scrollbar_rect.width - int(12 * VideoSettings.RENDER_SCALE)
        self.min_height = int(10 * VideoSettings.RENDER_SCALE)
        
        self.height = self.calculate_height()
        self.x = scrollbar_rect.x + int(7 * VideoSettings.RENDER_SCALE)
        self.y = self.calculate_position()

        self.shadow_radius = int(5 * VideoSettings.RENDER_SCALE)
        
        self.get_rect_and_surface()
        self.render()
    
    def get_rect_and_surface(self):
        """
        Get the rects and surfaces for the scrollbar
        """
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.surface = pygame.Surface((self.width, self.height), pygame.HWSURFACE | pygame.SRCALPHA) 
        
        self.shadow_rect = pygame.Rect(self.x - self.shadow_radius * 2, self.y - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.HWSURFACE | pygame.SRCALPHA)
    
    def calculate_height(self):
        """
        Calculate the height of the scrollbar based on the height of the container and the height of the scrollable area
        """
        visible_ratio = self.scrollbar_rect.height / (self.scrollbar_rect.height + self.y_diff)
        return max(self.min_height, visible_ratio * self.scrollbar_rect.height)

    def render(self):
        """
        Render the scrollbar and its shadow
        """
        self.render_shadow()
        draw_solid_colour(self.surface, '#242424', self.surface.get_rect())
        draw_border(self.surface, {'left': [2, '#3d3d3d']}, self.surface.get_rect(), VideoSettings.RENDER_SCALE)
        draw_border(self.surface, {'right': [2, '#181818']}, self.surface.get_rect(), VideoSettings.RENDER_SCALE)
        draw_border(self.surface, {'top': [2, '#3d3d3d']}, self.surface.get_rect(), VideoSettings.RENDER_SCALE)
        draw_border(self.surface, {'bottom': [2, '#0e0e0e']}, self.surface.get_rect(), VideoSettings.RENDER_SCALE)
        
    def render_shadow(self):
        """
        Render the shadow of the scrollbar
        """
        pygame.draw.rect(self.shadow_surface, (0, 0, 0), pygame.Rect(self.shadow_radius * 2, self.shadow_radius * 2, self.shadow_rect.width - 4 * self.shadow_radius, self.shadow_rect.height - 4 * self.shadow_radius))
        self.shadow_surface = apply_gaussian_blur_with_alpha(self.shadow_surface, self.shadow_radius)
        
    def calculate_position(self):
        """
        Calculate the position of the scrollbar based on the scrollable area
        """
        if self.y_scroll > 0:
            return 0
        
        scroll_ratio = abs(self.y_scroll) / self.y_diff  
        scroll_ratio = max(0, min(1, scroll_ratio)) 
        
        return scroll_ratio * (self.scrollbar_rect.height - self.height)
        
    def draw(self, surface):
        """
        Draw the scrollbar and its shadow
        """
        surface.blit(self.shadow_surface, self.shadow_rect.topleft)
        surface.blit(self.surface, self.rect.topleft)
        
    def update(self, y_scroll, surface):
        """
        Update the scrollbar
        """
        self.y_scroll = y_scroll    
        self.y = self.calculate_position()
        self.rect.update(self.x, self.y, self.width, self.height)
        self.shadow_rect.update(self.x - self.shadow_radius * 2, self.y - self.shadow_radius * 2, self.width + self.shadow_radius * 4, self.height + self.shadow_radius * 4)
        self.draw(surface)