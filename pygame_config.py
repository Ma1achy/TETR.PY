from config import Config
import pygame

class PyGameConfig():
    def __init__(self):
        self.CAPTION = 'Four'
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 1500, 900
        self.FOUR_INSTANCE_WIDTH, self.FOUR_INSTANCE_HEIGHT = 800, 900
        self.BORDER_WIDTH = 5
        
        self.UNCAPPED_FPS = True
        self.FPS = 144
        self.TPS = 256 # Subframes per second
    
        self.COLOUR_MAP = {
            -1: (255, 0, 0),
            0: (0, 0, 0), # empty
            1: (168, 34, 139), # T
            2: (99, 177, 0), # S
            3: (206, 0, 43), # Z
            4: (219, 87, 0), # L
            5: (38, 64, 202), # J 
            6: (221, 158, 0), # O
            7: (51, 156, 218), # I
            8: (105, 105, 105), # garbage
        }
        
        # Rendering constants
        self.GRID_SIZE = self.FOUR_INSTANCE_WIDTH // 25
        self.MATRIX_WIDTH = Config.MATRIX_WIDTH
        self.MATRIX_HEIGHT = Config.MATRIX_HEIGHT
        self.MATRIX_SURFACE_WIDTH = Config.MATRIX_WIDTH * self.GRID_SIZE
        self.MATRIX_SURFACE_HEIGHT = Config.MATRIX_HEIGHT // 2 * self.GRID_SIZE
        self.MATRIX_SCREEN_CENTER_X = (self.FOUR_INSTANCE_WIDTH - self.MATRIX_SURFACE_WIDTH) // 2
        self.MATRIX_SCREEN_CENTER_Y = (self.FOUR_INSTANCE_HEIGHT - self.MATRIX_SURFACE_HEIGHT) // 2
    
    def get_screen_size(self):
        info = pygame.display.Info()
        return info.current_w, info.current_h