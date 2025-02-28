from dataclasses import dataclass, field
from collections import deque
from app.sound.music import Music

@dataclass
class Sound():
    music_queue: deque = field(default_factory = deque)
    sfx_queue: deque = field(default_factory = deque)
    
    current_music: Music = None
    music_room_listening: bool = False