from dataclasses import dataclass, field
import queue

@dataclass
class Mouse():
    
    position: tuple[int, int] = (0, 0)
    events: queue.Queue = field(default_factory = queue.Queue)