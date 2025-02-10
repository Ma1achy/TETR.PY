from render.renderstruct import StructRender
import pygame
from utils import hex_to_rgb
from render.GUI.font import Font
import math
from app.core.config_manager import VideoSettings

class GUIFocus():
    def __init__(self, window, RenderStruct:StructRender):
        """
        An overlay that can be used to indicate that the game is out of focus
        
        args:
            window (pygame.Surface): the window to draw the focus overlay on
            RenderStruct (StructRender): the render structure
        """
        self.window = window
        self.RenderStruct = RenderStruct
        
        self.width = int(500 * VideoSettings.RENDER_SCALE)
        self.height = int(180 * VideoSettings.RENDER_SCALE)
        
        self.window_width = self.RenderStruct.RENDER_WIDTH
        self.window_height = self.RenderStruct.RENDER_HEIGHT
        
        self.focus_rect = pygame.Rect(self.RenderStruct.RENDER_WIDTH // 2 - self.width // 2, self.RenderStruct.RENDER_HEIGHT // 2 - self.height // 2, self.width, self.height)
        self.focus_surface = pygame.Surface((self.focus_rect.width, self.focus_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        
        self.main_font = Font('hun2', int(85 * VideoSettings.RENDER_SCALE))
        self.sub_font = Font('hun2', int(36 * VideoSettings.RENDER_SCALE))

        self.render()
        
    def render(self):
        """
        Render the focus overlay
        """
        self.focus_surface.fill((0, 0, 0, 200))
        pygame.draw.rect(self.focus_surface, hex_to_rgb('#FF0000'), (0, 0, self.focus_rect.width, self.focus_rect.height), math.ceil(5 * VideoSettings.RENDER_SCALE))
        pygame.draw.rect(self.focus_surface, hex_to_rgb('#FF0000'), (int(10 * VideoSettings.RENDER_SCALE), int(10 * VideoSettings.RENDER_SCALE), self.focus_rect.width - int(20 * VideoSettings.RENDER_SCALE), self.focus_rect.height - int(20 * VideoSettings.RENDER_SCALE)), math.ceil(2 * VideoSettings.RENDER_SCALE))
        
        self.main_font.draw(
            self.focus_surface,
            'out of focus',
            '#FF0000',
            'top',
            int(0 * VideoSettings.RENDER_SCALE),
            int(30 * VideoSettings.RENDER_SCALE),
        )
        
        self.sub_font.draw(
            self.focus_surface,
            'click to return to TETR.PY',
            '#FFFFFF',
            'bottom',
            int(0 * VideoSettings.RENDER_SCALE),
            int(30 * VideoSettings.RENDER_SCALE),
        )
        
    def draw(self):
        """
        Draw the focus overlay
        """
        self.window.blit(self.focus_surface, self.focus_rect)
        
    def handle_window_resize(self):
        """
        Handle the window resize
        """
        self.focus_rect.topleft = (self.RenderStruct.RENDER_WIDTH // 2 - self.width // 2, self.RenderStruct.RENDER_HEIGHT // 2 - self.height // 2)
        
    def update(self):
        """
        Update the focus overlay
        """
        if not VideoSettings.WARN_WHEN_NOT_FOCUSED:
            return
        
        self.draw()
       