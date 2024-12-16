from dataclasses import dataclass, field
import queue

@dataclass
class Keyboard():
    
    key_states = {}
    key_states_queue: queue.Queue = field(default_factory = queue.Queue)
    menu_actions_queue: queue.Queue = field(default_factory = queue.Queue)
    
    # DAS and ARR for menu navigation etc, seperate from game DAS and ARR
    DAS_delay: int = 167
    ARR_delay: int = 33
    
    DAS_counter: float = 0
    ARR_counter: float = 0
    
    DAS_remainder: float = 0
    ARR_remainder: float = 0