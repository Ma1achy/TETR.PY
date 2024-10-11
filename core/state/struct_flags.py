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
    SINGLE = auto()
    DOUBLE = auto()
    TRIPLE = auto()
    QUADRUPLE = auto()
    
    SOFT_DROP = auto()
    HARD_DROP = auto()
    
    IS_SPIN = auto()
    TSPIN = auto()
    TSPIN_MINI = auto()
    
    ALL_CLEAR = auto()
    BACK2BACK = auto()
    COMBO = auto()
    
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