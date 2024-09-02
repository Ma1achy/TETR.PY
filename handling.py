from enum import Enum, auto
import pygame as pygame

class Action(Enum):
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    ROTATE_CLOCKWISE = auto()
    ROTATE_COUNTERCLOCKWISE = auto()
    ROTATE_180 = auto()
    HARD_DROP = auto()
    SOFT_DROP = auto()
    HOLD = auto()

class Handling():
    key_bindings = {
        Action.MOVE_LEFT:                   pygame.K_LEFT,
        Action.MOVE_RIGHT:                  pygame.K_RIGHT,
        Action.ROTATE_CLOCKWISE:            pygame.K_x,
        Action.ROTATE_COUNTERCLOCKWISE:     pygame.K_z,
        Action.ROTATE_180:                  pygame.K_SPACE,
        Action.HARD_DROP:                   pygame.K_DOWN,
        Action.SOFT_DROP:                   pygame.K_UP,
        Action.HOLD:                        pygame.K_c
    }
    
    
def GetEmptyActions():
    return {
        Action.MOVE_LEFT:                   False,
        Action.MOVE_RIGHT:                  False,
        Action.ROTATE_CLOCKWISE:            False,
        Action.ROTATE_COUNTERCLOCKWISE:     False,
        Action.ROTATE_180:                  False,
        Action.HARD_DROP:                   False,
        Action.SOFT_DROP:                   False,
        Action.HOLD:                        False,
    }