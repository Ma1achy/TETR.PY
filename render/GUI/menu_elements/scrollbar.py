import pygame
from utils import draw_solid_colour, draw_border, apply_gaussian_blur_with_alpha

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