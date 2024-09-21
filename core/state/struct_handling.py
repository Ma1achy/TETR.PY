from dataclasses import dataclass
from core.handling import Action

@dataclass
class StructHandling():
    current_time: float = 0
    prev_time: float = 0
    delta_time: float = 0
    last_tick_time: float = 0
    do_first_tick: bool = True
    poll_tick_counter: int = 0
    poll_counter_last_cleared: float = 0
    current_direction: Action = None

    buffer_threshold: int = 128 # tick range where old actions are still considered valid
    
    DAS_counter: int = 0
    das_remainder: float = 0
    DAS_charged: bool = False
    
    ARR_counter: int = 0
    arr_remainder: float = 0
    
    do_movement: bool = False 
    instant_movement: bool = False