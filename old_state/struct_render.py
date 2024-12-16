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
    
    spin_type: str = None
    is_mini: bool = False
    
    lines_cleared: bool = False
    cleared_blocks: list = None
    cleared_idxs: list = None
    
    CAPTION = 'Four'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900

    def  __post_init__(self):
        
        self.GRID_SIZE = int(self.WINDOW_WIDTH / 48)
        self.BORDER_WIDTH = int(self.GRID_SIZE / 6)
