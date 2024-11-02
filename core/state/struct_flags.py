from dataclasses import dataclass, field
from typing import Dict
from enum import Enum, auto


class FLAG(Enum):
    # game state
    GAME_OVER = auto()
    DANGER = auto()
    
    # handling that is reliant on game state
    DO_PREVENT_ACCIDENTAL_HARD_DROP = auto() 
    DO_DCD = auto() 
    
    # scoring
    LINE_CLEAR = auto()
    
    SOFT_DROP = auto()
    HARD_DROP = auto()

    IS_SPIN = auto()
    IS_MINI = auto()
    
    ALL_CLEAR = auto()
    BACK2BACK = auto()
    COMBO = auto()
    
    # debug
    SHOW_DEBUG_MENU = auto()
    
    SPIN_DIRECTION = auto()
    SPIN_ANIMATION = auto()
    
    PUSH_HORIZONTAL = auto()
    PUSH_VERTICAL = auto()
    CANNOT_FALL = auto()

    HARD_DROP_BOUNCE = auto()
    AUTO_LOCK_SCALE = auto()
    
def generate_flags():
    return {flag: False for flag in FLAG}
@dataclass
class StructFlags():
    FLAGS: Dict[FLAG, bool] = field(default_factory = generate_flags)
    
def create_property(flag):
    def getter(self):
        return self.FLAGS[flag]

    def setter(self, value):
        self.FLAGS[flag] = value

    return property(getter, setter)

def set_flag_attr():
    for flag in FLAG:
        setattr(StructFlags, flag.name, create_property(flag))