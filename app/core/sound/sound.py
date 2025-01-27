from dataclasses import dataclass, field
from collections import deque
from app.core.sound.music import Music
@dataclass
class Sound():
    music_queue: deque = field(default_factory = deque)
    sfx_queue: deque = field(default_factory = deque)
    
    current_music: Music = None
    music_room_listening: bool = False
    
    music_volume: float = 0.05
    sfx_volume: float = 1.0