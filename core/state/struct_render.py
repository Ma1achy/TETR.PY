from dataclasses import dataclass, field
from typing import List
import pygame
from typing import Dict, Tuple

@dataclass
class StructRender():
    surfaces: List[pygame.Surface] = field(default_factory = list)

    # debug rendering flags
    draw_guide_lines: bool = False
    draw_bounding_box: bool = False
    draw_origin: bool = False
    draw_pivot: bool = False
    current_time: float = 0
    
    key_dict: dict = None
    
    COLOUR_MAP: Dict[int, Tuple[int, int, int]] = field(default_factory = lambda: {
        -1: (255, 0, 0),
        0: (0, 0, 0),        # empty
        1: (168, 34, 139),   # T
        2: (99, 177, 0),     # S
        3: (206, 0, 43),     # Z
        4: (219, 87, 0),     # L
        5: (38, 64, 202),    # J 
        6: (221, 158, 0),    # O
        7: (51, 156, 218),   # I
        8: (105, 105, 105),  # garbage
    })
    
    CAPTION = 'Four'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900
    
    BORDER_WIDTH = 7
    
    def  __post_init__(self):
        self.GRID_SIZE = self.WINDOW_WIDTH // 48
        