from dataclasses import dataclass, field
from collections import deque

@dataclass
class Sound():
    music_queue: deque = field(default_factory = deque)
    sfx_queue: deque = field(default_factory = deque)
    
    current_music = None
    
    music_volume = 0.1
    sfx_volume = 1.0