from dataclasses import dataclass, field
import queue
from enum import Enum, auto

@dataclass
class Mouse():
    
    position: tuple[int, int] = (0, 0)
    motion: tuple[int, int] = (0, 0)
    events: queue.Queue = field(default_factory = queue.Queue)

class MouseEvents(Enum):
    MOUSEBUTTON1 = auto()
    MOUSEBUTTON2 = auto()
    MOUSEBUTTON3 = auto()
    MOUSEBUTTON4 = auto()
    MOUSEBUTTON5 = auto()
    MOUSEBUTTON6 = auto()
    MOUSEBUTTON7 = auto()
    MOUSEBUTTON8 = auto()
    MOUSEBUTTON9 = auto()
    MOUSEBUTTON10 = auto() # icl if you have more than this many buttons you need to touch grass
    
    SCROLLWHEEL = auto()