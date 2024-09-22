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
    