from dataclasses import dataclass, field
from typing import List
import pygame

@dataclass
class StructRender():
    surfaces: List[pygame.Surface] = field(default_factory = list)
    
    # debug rendering flags
    draw_bounding_box: bool = False
    draw_origin: bool = False
    draw_pivot: bool = False
    current_time: float = 0