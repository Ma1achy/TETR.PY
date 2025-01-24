from dataclasses import dataclass, field
import queue

@dataclass
class Sound():
    music_queue: queue.Queue = field(default_factory = queue.Queue)
    sfx_queue: queue.Queue = field(default_factory = queue.Queue)