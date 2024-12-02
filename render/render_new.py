import pygame
from dataclasses import dataclass
from utils import hex_to_rgb
from render.GUI.debug_overlay import GUIDebug
from render.GUI.focus_overlay import GUIFocus

class Render():
    def __init__(self, Config, Timing, Debug, GameInstances, MenuManager):
        """
        args:
            self.window (pygame.Surface): the window to render the game onto
        """
        
        self.Config = Config
        self.Timing = Timing
        self.Debug = Debug
        self.RenderStruct =  StructRender()
        self.GameInstances = GameInstances
        self.MenuManager = MenuManager
        
        self.GUI_debug = GUIDebug(self.Config, self.RenderStruct, self.Debug)
        self.GUI_focus = GUIFocus(self.RenderStruct)
        
        self.icon = pygame.image.load('resources/icon.png')
        self.window = self.__init_window()
        self.MenuManager.init_menus(self.window)
        
        self.image_path = 'resources/background/b1.jpg'
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT))
        
        self.darken_overlay_layer = pygame.Surface((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.SRCALPHA)
        self.darken_overlay_layer_alpha = 200
       
    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption(self.RenderStruct.CAPTION)
        return pygame.display.set_mode((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)

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
            self.GUI_debug.draw(self.window)
        
        if not self.MenuManager.is_focused:
            self.GUI_focus.draw(self.window)
            
        pygame.display.flip()
    
@dataclass
class StructRender():
    CAPTION = 'TETR.PY'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900

