from dataclasses import dataclass, field
from typing import Dict, List
import pygame

@dataclass
class StructRender():
    surfaces: List[pygame.Surface] = field(default_factory = list)
    
    