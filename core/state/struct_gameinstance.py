from dataclasses import dataclass
from utils import Vec2
from instance.four import Queue
from instance.matrix import Matrix

@dataclass
class StructGameInstance():
    
    spawn_pos = Vec2(4, 18)
    held_tetromino: str = None 
    current_tetromino: str = None
    on_floor: bool = False
    
    queue:Queue = None
    matrix:Matrix = None
    
    gravity: float = 1/60
    G_units_in_ticks: int = 0
    gravity_counter: int = 0
    move_down: bool= False

    soft_dropping: bool = True
    soft_drop_factor: int = 1

    lock_delay: int = 30
    lock_delay_in_ticks: int = 0
    can_hold: bool = True
    
    lowest_pivot_position: int = 0
    
