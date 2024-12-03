from render.render_new import StructRender
import pygame
from utils import hex_to_rgb
from render.GUI.font import Font

class GUIFocus():
    def __init__(self, RenderStruct:StructRender):
        
        self.RenderStruct = RenderStruct
        self.width = 500
        self.height = 180
        
        self.window_width = self.RenderStruct.WINDOW_WIDTH
        self.window_height = self.RenderStruct.WINDOW_HEIGHT
        
        self.focus_rect = pygame.Rect(self.RenderStruct.WINDOW_WIDTH//2 - self.width // 2, self.RenderStruct.WINDOW_HEIGHT//2 - self.height // 2, self.width, self.height)
        self.focus_surface = pygame.Surface((self.focus_rect.width, self.focus_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        
        self.main_font = Font('hun2', 85)
        self.sub_font = Font('hun2', 36)
        
    def draw(self, surface):
        self.focus_surface.fill((0, 0, 0, 200))
        pygame.draw.rect(self.focus_surface, hex_to_rgb('#FF0000'), (0, 0, self.focus_rect.width, self.focus_rect.height), 5)
        pygame.draw.rect(self.focus_surface, hex_to_rgb('#FF0000'), (10, 10, self.focus_rect.width - 20, self.focus_rect.height - 20), 2)
        
        self.main_font.draw(
            self.focus_surface,
            'out of focus',
            '#FF0000',
            'top',
            0,
            30,
        )
        
        self.sub_font.draw(
            self.focus_surface,
            'click to return to TETR.PY',
            '#FFFFFF',
            'bottom',
            0,
            30,
        )
        
        surface.blit(self.focus_surface, self.focus_rect)
        
    def handle_window_resize(self):
        self.focus_rect.topleft = (self.RenderStruct.WINDOW_WIDTH//2 - self.width // 2, self.RenderStruct.WINDOW_HEIGHT//2 - self.height // 2)
       