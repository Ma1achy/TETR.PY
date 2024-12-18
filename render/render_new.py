import pygame
from dataclasses import dataclass, field
import ctypes
import platform
from typing import Dict, Tuple

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
        self.__load_background_image()
        self.__get_darken_overlay()
        self.darken_overlay_layer_alpha = 200
        
        self.fullscreen = self.RenderStruct.fullscreen
       
    def __init_window(self):
        """
        Create the window to draw to
        """
        self.__set_taskbar_icon_windows()
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption(self.RenderStruct.CAPTION)
        
        if self.RenderStruct.fullscreen:
            window = pygame.display.set_mode((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
        else:
            window = pygame.display.set_mode((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
            
        self.__set_dark_mode()
        return window

    def draw_frame(self):
        
        if self.Timing.frame_delta_time <= 0:
            self.dt = 1 / self.Config.FPS
        else:
            self.dt = self.Timing.frame_delta_time

        self.__toggle_fullscreen()
        self.window.blit(self.image, (0, 0))
        self.darken_overlay_layer.fill((0, 0, 0, self.darken_overlay_layer_alpha))
        self.window.blit(self.darken_overlay_layer, (0, 0))
                    
        self.MenuManager.current_menu.update(self.MenuManager.in_dialog)
         
        if self.MenuManager.debug_overlay:
            self.MenuManager.GUI_debug.draw(self.window)
        
        if not self.MenuManager.is_focused:
            self.MenuManager.GUI_focus.draw(self.window)
            
        if self.MenuManager.in_dialog:
            try:
                self.darken_overlay_layer.fill((0, 0, 0, min(self.MenuManager.current_dialog.alpha, 200)))
            except Exception as e:
                self.darken_overlay_layer.fill((0, 0, 0, 200))
                
            self.window.blit(self.darken_overlay_layer, (0, 0))
            self.MenuManager.current_dialog.update()
        else:
            self.darken_overlay_layer_alpha = 200
            
        self.MenuManager.copy_to_clipboard_animation()     
        pygame.display.flip()
    
    def __load_background_image(self):
        self.image = pygame.image.load(self.background_image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT))
    
    def __get_darken_overlay(self):
        self.darken_overlay_layer = pygame.Surface((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)

    def handle_window_resize(self):
        self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT = self.window.get_size()
        self.__load_background_image()
        self.__get_darken_overlay()
        self.MenuManager.handle_window_resize()
    
    def __set_taskbar_icon_windows(self):
        if not platform.system() == 'Windows':
            return
        
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('TETR.PY')

    def __set_dark_mode(self):
        if not platform.system() == 'Windows':
            return 
        
        try:
            hwnd = pygame.display.get_wm_info()['window']
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            
        except Exception as e:
            print(f"\033[91mError setting window title bar mode: {e}\033[0m")
    
    def __toggle_fullscreen(self):
        if self.fullscreen == self.RenderStruct.fullscreen:
            return
        
        if self.RenderStruct.fullscreen:
            pygame.display.set_mode((0, 0), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((1500, 900), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        
        self.fullscreen = self.RenderStruct.fullscreen
        self.handle_window_resize()

@dataclass
class StructRender():
    CAPTION = 'TETR.PY'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900
    
    fullscreen = False
    
    # old stuff (might need to be changed)
    
    # debug rendering flags
    draw_guide_lines: bool = False
    draw_bounding_box: bool = False
    draw_origin: bool = False
    draw_pivot: bool = False
    current_time: float = 0
    
    key_dict: dict = None
    
    COLOUR_MAP: Dict[int, Tuple[int, int, int]] = field(default_factory = lambda: {
    
        'Z': (206, 0, 43),     
        'L': (219, 87, 0),     
        'O': (221, 158, 0),    
        'S': (99, 177, 0),     
        'I': (51, 156, 218),   
        'J': (38, 64, 202),    
        'T': (168, 34, 139),   
        
        'Garbage': (105, 105, 105),  
        'Hurry': (32, 32, 32),
        'Locked': (75, 75, 75)
   
    })
    
    COLOUR_MAP_AVG_TEXTURE_COLOUR : Dict[int, Tuple[int, int, int]] = field(default_factory = lambda: {
    
        'Z': (221, 67, 75),
        'L': (221, 125, 67),     
        'O': (221, 209, 67),
        'S': (124, 221, 67),
        'I': (67, 221, 178),
        'J': (92, 67, 221),
        'T': (207, 67, 221),
        
        'Garbage': (75, 75, 75),  
        'Hurry': (43, 43, 43),
        'Locked': (43, 43, 43)
   
    })
    
    TEXTURE_MAP: Dict[int, Tuple[int, int, int]] = field(default_factory = lambda: {
        'Z': 0,     
        'L': 1,     
        'O': 2,    
        'S': 3,     
        'I': 4,   
        'J': 5,    
        'T': 6,   
        
        'Garbage': 7,  
        'Hurry': 8,
        'Locked': 9,
        'Shadow': 10,
        'Warning': 11
    })
    
    # will have to move this to a per instance basis
    spin_type: str = None
    is_mini: bool = False
    
    lines_cleared: bool = False
    cleared_blocks: list = None
    cleared_idxs: list = None
    # ========================
    
    def  __post_init__(self):
        
        self.GRID_SIZE = int(self.WINDOW_WIDTH / 48)
        self.BORDER_WIDTH = int(self.GRID_SIZE / 6)

