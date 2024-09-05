from config import Config
import pygame

def get_screen_size():
    info = pygame.display.Info()
    return info.current_w, info.current_h

class PyGameConfig():

    CAPTION = 'Four'
    WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 900
    FOUR_INSTANCE_WIDTH, FOUR_INSTANCE_HEIGHT = 800, 900
    BORDER_WIDTH = 4
    
    UNCAPPED_FPS = False
    FPS = 60
    TPS = 128 # Subframes per second

    ARR = 33 # Auto repeat rate: The speed at which tetrominoes move when holding down the movement keys (ms)
    DAS = 167 # Delayed Auto Shift: The time between the inital key press and the automatic repeat movement (ms)
    DCD = 0 # DAS Cut Delay: If none-zero, any ongoing DAS movement will pause for a set amount of time after dropping/rorating a piece (ms)
    SDF = 6 # Soft Drop Facor: The factor the soft dropping scales the current gravity by
    
    COLOUR_MAP = {
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
    GRID_SIZE = FOUR_INSTANCE_WIDTH // 25
    MATRIX_WIDTH = Config.MATRIX_WIDTH
    MATRIX_HEIGHT = Config.MATRIX_HEIGHT
    MATRIX_SURFACE_WIDTH = Config.MATRIX_WIDTH * GRID_SIZE
    MATRIX_SURFACE_HEIGHT = Config.MATRIX_HEIGHT // 2 * GRID_SIZE
    MATRIX_SCREEN_CENTER_X = (FOUR_INSTANCE_WIDTH - MATRIX_SURFACE_WIDTH) // 2
    MATRIX_SCREEN_CENTER_Y = (FOUR_INSTANCE_HEIGHT - MATRIX_SURFACE_HEIGHT) // 2