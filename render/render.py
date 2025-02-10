import pygame
import ctypes
import platform
from app.core.config_manager import VideoSettings

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
        
        self.fullscreen = VideoSettings.FULLSCREEN
    
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
        pygame.display.set_caption(self.RenderStruct.CAPTION, icontitle = self.RenderStruct.CAPTION)

        if VideoSettings.RENDER_SCALE_MODE == "OFF":
            VideoSettings.RENDER_SCALE = 1
            if VideoSettings.FULLSCREEN:
                width, height = self.monitor_width, self.monitor_height
            else:
                #width, height = self.__get_available_display_area()
                width, height = 1500, 900
        else:
            if VideoSettings.FULLSCREEN and VideoSettings.RENDER_SCALE_MODE == "DYNAMIC":
                width, height = self.monitor_width, self.monitor_height
            else:
                width, height = 1500, 900

        self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT = width, height
        
        self.RenderStruct.RENDER_WIDTH = int(self.RenderStruct.WINDOW_WIDTH * VideoSettings.RENDER_SCALE)
        self.RenderStruct.RENDER_HEIGHT = int(self.RenderStruct.WINDOW_HEIGHT * VideoSettings.RENDER_SCALE)

        flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        
        if VideoSettings.FULLSCREEN:
            flags |= pygame.FULLSCREEN

        if VideoSettings.RENDER_SCALE_MODE == "LOCKED" or VideoSettings.RENDER_SCALE_MODE == "DYNAMIC":
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
        
        if VideoSettings.RENDER_SCALE_MODE == "OFF":
            self.RenderStruct.RENDER_WIDTH = int(self.RenderStruct.WINDOW_WIDTH * VideoSettings.RENDER_SCALE)
            self.RenderStruct.RENDER_HEIGHT = int(self.RenderStruct.WINDOW_HEIGHT * VideoSettings.RENDER_SCALE)
    
        self.__load_background_image()
        self.__get_darken_overlay()
        self.MenuManager.handle_window_resize()
    
    def __check_if_fullscreen_toggled(self):
        """
        Toggles the fullscreen mode while adjusting window and render sizes appropriately.
        """
        if self.fullscreen == VideoSettings.FULLSCREEN:
            return 

        self.fullscreen = VideoSettings.FULLSCREEN

        self.__recreate_window()
        self.handle_window_resize()
        
    def __recreate_window(self):
        self.__set_taskbar_icon_windows()
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption(self.RenderStruct.CAPTION, icontitle = self.RenderStruct.CAPTION)
        
        if VideoSettings.FULLSCREEN:
            width, height = self.monitor_width, self.monitor_height
        else:
            if VideoSettings.RENDER_SCALE_MODE == "OFF":
                VideoSettings.RENDER_SCALE = 1
                #width, height = self.__get_available_display_area()
                width, height = 1500, 900
            else:
                width, height = 1500, 900

        self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT = width, height
        
        if VideoSettings.RENDER_SCALE_MODE == "OFF" or VideoSettings.RENDER_SCALE_MODE == "DYNAMIC": # recalculate render size when fullscreen is toggled (makes ui appear the same size on screen but are rendered at a different resolution)
            self.RenderStruct.RENDER_WIDTH = int(self.RenderStruct.WINDOW_WIDTH * VideoSettings.RENDER_SCALE)
            self.RenderStruct.RENDER_HEIGHT = int(self.RenderStruct.WINDOW_HEIGHT * VideoSettings.RENDER_SCALE)

        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        
        if VideoSettings.FULLSCREEN:
            flags |= pygame.FULLSCREEN
            
        if VideoSettings.RENDER_SCALE_MODE == "LOCKED" or VideoSettings.RENDER_SCALE_MODE == "DYNAMIC":
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
        
        self.window.fill((0, 0, 0))
        self.__check_if_fullscreen_toggled()
        
        if VideoSettings.DRAW_BACKGROUND:
            self.image.set_alpha(255 * VideoSettings.BACKGROUND_VISIBILITY)
            self.window.blit(self.image, (0, 0))
        
        self.MenuManager.tick()
        
        pygame.display.flip()

