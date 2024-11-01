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
    dir_priority = None

    buffer_threshold: int = 128 # tick range where old actions are still considered valid
    
    DAS_LEFT_COUNTER: int = 0
    DAS_LEFT_COUNTER_REMAINDER: float = 0
    
    ARR_LEFT_COUNTER: int = 0
    ARR_LEFT_COUNTER_REMAINDER: float = 0
    
    DO_MOVEMENT_LEFT: bool = False 
      
    DAS_RIGHT_COUNTER: int = 0
    DAS_RIGHT_COUNTER_REMAINDER: float = 0
    
    ARR_RIGHT_COUNTER: int = 0
    ARR_RIGHT_COUNTER_REMAINDER: float = 0
    
    DO_MOVEMENT_RIGHT: bool = False
    
    PREV_ACC_HD_COUNTER: int = 0

    key_dict = None # dict of keys that are currently pressed
    
    DONE_TAP_LEFT: bool = False
    DONE_TAP_RIGHT: bool = False