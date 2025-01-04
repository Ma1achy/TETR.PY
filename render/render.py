import pygame
from dataclasses import dataclass, field
import ctypes
import platform
from typing import Dict, Tuple

class Render():
    def __init__(self, Timing, RenderStruct, Debug, GameInstances, MenuManager):
        """
        args:
            self.window (pygame.Surface): the window to render the game onto
        """
        
        self.Timing = Timing
        self.Debug = Debug
        self.RenderStruct = RenderStruct
        self.GameInstances = GameInstances
        self.MenuManager = MenuManager
        
        self.display_info = pygame.display.Info()
        self.monitor_width = self.display_info.current_w
        self.monitor_height = self.display_info.current_h
        
        self.icon = pygame.image.load('resources/icon.png')
        self.__init_window()
        self.MenuManager.init_menus(self.window)
        
        self.background_image_path = 'resources/background/b1.jpg'
        self.__load_background_image()
        self.__get_darken_overlay()
        self.darken_overlay_layer_alpha = 200
        
        self.fullscreen = self.RenderStruct.fullscreen
    
    # ---------------------------------------------- WINDOW CREATION ----------------------------------------------
    def __get_available_display_area(self):
        """
        Get the monitor size excluding taskbar and other system UI elements.
        """
        if platform.system() == 'Windows':
            user32 = ctypes.windll.user32
            work_area = ctypes.wintypes.RECT()
            user32.SystemParametersInfoW(48, 0, ctypes.byref(work_area), 0)
            monitor_width = work_area.right - work_area.left
            monitor_height = work_area.bottom - work_area.top - 35
        else:
            monitor_width = self.monitor_width
            monitor_height = self.monitor_height - 80
        return monitor_width, monitor_height
                
    def __init_window(self):
        """
        Create the window to draw to.
        """
        self.__set_taskbar_icon_windows()
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption(self.RenderStruct.CAPTION)

        if not self.RenderStruct.USE_RENDER_SCALE:
            self.RenderStruct.RENDER_SCALE = 1
            width, height = self.__get_available_display_area()
        else:
            width, height = 1500, 900

        self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT = width, height
        
        self.RenderStruct.RENDER_WIDTH = int(self.RenderStruct.WINDOW_WIDTH * self.RenderStruct.RENDER_SCALE)
        self.RenderStruct.RENDER_HEIGHT = int(self.RenderStruct.WINDOW_HEIGHT * self.RenderStruct.RENDER_SCALE)

        flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        
        if self.RenderStruct.fullscreen:
            flags |= pygame.FULLSCREEN

        if self.RenderStruct.USE_RENDER_SCALE:
            flags |= pygame.SCALED
            width, height = self.RenderStruct.RENDER_WIDTH, self.RenderStruct.RENDER_HEIGHT
            
        self.window = pygame.display.set_mode((width, height), flags)
        self.__set_dark_mode()
    
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
    
    # ---------------------------------------------- WINDOW RESIZING ----------------------------------------------
    
    def handle_window_resize(self):
        self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT = self.window.get_size()
        
        if not self.RenderStruct.USE_RENDER_SCALE:
            self.RenderStruct.RENDER_WIDTH = int(self.RenderStruct.WINDOW_WIDTH * self.RenderStruct.RENDER_SCALE)
            self.RenderStruct.RENDER_HEIGHT = int(self.RenderStruct.WINDOW_HEIGHT * self.RenderStruct.RENDER_SCALE)
    
        self.__load_background_image()
        self.__get_darken_overlay()
        self.MenuManager.handle_window_resize()
    
    def __check_if_fullscreen_toggled(self):
        """
        Toggles the fullscreen mode while adjusting window and render sizes appropriately.
        """
        if self.fullscreen == self.RenderStruct.fullscreen:
            return 

        self.fullscreen = self.RenderStruct.fullscreen

        self.__recreate_window()
        self.handle_window_resize()
        
    def __recreate_window(self):
        if self.RenderStruct.fullscreen:
            width, height = self.monitor_width, self.monitor_height
        else:
            if not self.RenderStruct.USE_RENDER_SCALE:
                self.RenderStruct.RENDER_SCALE = 1
                width, height = self.__get_available_display_area()
            else:
                width, height = 1500, 900

        self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT = width, height
        
        if self.RenderStruct.APPLY_RENDER_SCALE_TO_FULLSCREEN or not self.RenderStruct.USE_RENDER_SCALE: # recalculate render size when fullscreen is toggled (makes ui appear the same size on screen but are rendered at a different resolution)
            self.RenderStruct.RENDER_WIDTH = int(self.RenderStruct.WINDOW_WIDTH * self.RenderStruct.RENDER_SCALE)
            self.RenderStruct.RENDER_HEIGHT = int(self.RenderStruct.WINDOW_HEIGHT * self.RenderStruct.RENDER_SCALE)

        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        
        if self.RenderStruct.fullscreen:
            flags |= pygame.FULLSCREEN
            
        if self.RenderStruct.USE_RENDER_SCALE:
            flags |= pygame.SCALED
            width, height = self.RenderStruct.RENDER_WIDTH, self.RenderStruct.RENDER_HEIGHT
        else:
            flags |= pygame.RESIZABLE # somhow i can create a scaled resizable window when i start pygame but when i try to recreate it after a fullscreen end event it crashes ????????????????????????
        
        self.window = pygame.display.set_mode((width, height), flags)
    
    # ---------------------------------------------- RENDERING TO WINDOW ----------------------------------------------
        
    def __load_background_image(self):
        self.image = pygame.image.load(self.background_image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.RenderStruct.RENDER_WIDTH, self.RenderStruct.RENDER_HEIGHT))
    
    def __get_darken_overlay(self):
        self.darken_overlay_layer = pygame.Surface((self.RenderStruct.RENDER_WIDTH, self.RenderStruct.RENDER_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)
             
    def draw_frame(self):
        
        self.__check_if_fullscreen_toggled()
        
        self.window.blit(self.image, (0, 0))
        self.MenuManager.tick()
        
        pygame.display.flip()
        
@dataclass
class StructRender():
    
    CAPTION = 'TETR.PY'
    WINDOW_WIDTH = 1500 
    WINDOW_HEIGHT = 900
    
    USE_RENDER_SCALE = True
    APPLY_RENDER_SCALE_TO_FULLSCREEN = True
    RENDER_SCALE = 1
    
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
        
        self.RENDER_WIDTH = int(self.WINDOW_WIDTH * self.RENDER_SCALE)
        self.RENDER_HEIGHT = int(self.WINDOW_HEIGHT * self.RENDER_SCALE)
        
        self.GRID_SIZE = int(self.WINDOW_WIDTH / 48)
        self.BORDER_WIDTH = int(self.GRID_SIZE / 6)

