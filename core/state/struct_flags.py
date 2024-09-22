from dataclasses import dataclass, field
from typing import Dict
from enum import Enum, auto


class FLAG(Enum):
    DANGER = auto()
    GAME_OVER = auto()


@dataclass
class StructFlags():
    FLAGS: Dict[FLAG, bool] = field(default_factory = lambda: {
        FLAG.DANGER: False,
        FLAG.GAME_OVER: False
    })
    
def create_property(flag):
    def getter(self):
        return self.FLAGS[flag]

    def setter(self, value):
        self.FLAGS[flag] = value

    return property(getter, setter)

def set_flag_attr():
    for flag in FLAG:
        setattr(StructFlags, flag.name, create_property(flag))