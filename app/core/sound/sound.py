from dataclasses import dataclass, field
from collections import deque

@dataclass
class Sound():
    music_queue: deque = field(default_factory = deque)
    sfx_queue: deque = field(default_factory = deque)
    
    current_music = None