from dataclasses import dataclass
from utils import Vec2

@dataclass
class StructGameInstance():
    
    spawn_pos = Vec2(4, 18)
    held_tetromino: str = None 
    current_tetromino: str = None
    on_floor: bool = False

    gravity: float = 1/60
    G_units_in_ticks: int = 0
    gravity_counter: int = 0
    move_down: bool= False

    soft_dropping: bool = True
    soft_drop_factor: int = 1

    lock_delay: int = 30
    lock_delay_in_ticks: int = 0
    lock_delay_counter: int = 0
    max_moves_before_lock: int = 0
    can_hold: bool = True
    
