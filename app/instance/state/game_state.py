from dataclasses import dataclass
from app.utils import Vec2
from instance.engine.four import Queue
from instance.engine.matrix import Matrix

@dataclass
class GameState():
    
    spawn_pos = Vec2(4, 18)
    held_tetromino: str = None 
    current_tetromino: str = None
    next_tetromino: str = None
    on_floor: bool = False
    
    queue:Queue = None
    matrix:Matrix = None
    
    gravity: float = 1/60
    G_units_in_ticks: int = 0
    gravity_counter: int = 0
    move_down: bool= False

    soft_dropping: bool = False
    soft_drop_factor: int = 1

    lock_delay: int = 60
    lock_delay_in_ticks: int = 0
    can_hold: bool = True
    
    lowest_pivot_position: int = 0
    
    cleared_blocks: list = None
    cleared_idxs: list = None
    lines_cleared: int = None

    is_on_floor: bool = False
    is_in_buffer_zone: bool = False