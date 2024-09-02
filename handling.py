from enum import Enum, auto
class Action(Enum):
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    ROTATE_CLOCKWISE = auto()
    ROTATE_COUNTERCLOCKWISE = auto()
    HARD_DROP = auto()
    SOFT_DROP = auto()
    HOLD = auto()
