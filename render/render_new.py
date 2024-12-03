import pygame
from dataclasses import dataclass
from utils import hex_to_rgb

class Render():
    def __init__(self, Config, Timing, RenderStruct, Debug, GameInstances, MenuManager):
        """
        args:
            self.window (pygame.Surface): the window to render the game onto
        """
        
        self.Config = Config
        self.Timing = Timing
        self.Debug = Debug
        self.RenderStruct = RenderStruct
        self.GameInstances = GameInstances
        self.MenuManager = MenuManager
        
        self.icon = pygame.image.load('resources/icon.png')
        self.window = self.__init_window()
        self.MenuManager.init_menus(self.window)
        
        self.background_image_path = 'resources/background/b1.jpg'
        self.load_background_image()
        self.get_darken_overlay()
        self.darken_overlay_layer_alpha = 200
       
    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption(self.RenderStruct.CAPTION)
        return pygame.display.set_mode((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

    def draw_frame(self):
        
        if self.Timing.frame_delta_time <= 0:
            self.dt = 1 / self.Config.FPS
        else:
            self.dt = self.Timing.frame_delta_time
                    
        self.window.blit(self.image, (0, 0))
        self.darken_overlay_layer.fill((0, 0, 0, self.darken_overlay_layer_alpha))
        self.window.blit(self.darken_overlay_layer, (0, 0))
        self.MenuManager.current_menu.update()
        
        if self.MenuManager.debug_overlay:
            self.MenuManager.GUI_debug.draw(self.window)
        
        if not self.MenuManager.is_focused:
            self.MenuManager.GUI_focus.draw(self.window)
            
        pygame.display.flip()
    
    def load_background_image(self):
        self.image = pygame.image.load(self.background_image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT))
    
    def get_darken_overlay(self):
        self.darken_overlay_layer = pygame.Surface((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)
    
    def handle_window_resize(self):
        self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT = self.window.get_size()
        self.load_background_image()
        self.get_darken_overlay()
        self.MenuManager.handle_window_resize()
        
@dataclass
class StructRender():
    CAPTION = 'TETR.PY'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900

