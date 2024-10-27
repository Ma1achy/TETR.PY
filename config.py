from dataclasses import dataclass, field
import pygame
from core.handling import Action
from typing import Dict, Tuple
@dataclass
class StructConfig():
    
    key_bindings: Dict[Action, list[int]] = field(default_factory = lambda: {
        Action.MOVE_LEFT:                   [pygame.K_LEFT],
        Action.MOVE_RIGHT:                  [pygame.K_RIGHT],
        Action.ROTATE_CLOCKWISE:            [pygame.K_x],
        Action.ROTATE_COUNTERCLOCKWISE:     [pygame.K_z],
        Action.ROTATE_180:                  [pygame.K_SPACE],
        Action.HARD_DROP:                   [pygame.K_DOWN],
        Action.SOFT_DROP:                   [pygame.K_UP],
        Action.HOLD:                        [pygame.K_c],
    })
    
    HANDLING_SETTINGS: Dict[str, object] = field(default_factory = lambda: {
        'ARR': 33,           # Auto repeat rate (int) in ms: The speed at which tetrominoes move when holding down the movement keys (ms)
        'DAS': 167,          # Delayed Auto Shift (int) in ms: The time between the initial key press and the automatic repeat movement (ms)
        'DCD': 0,            # DAS Cut Delay (int) in ms: If non-zero, any ongoing DAS movement will pause for a set amount of time after dropping/rotating a piece (ms)
        'SDF': 23,           # Soft Drop Factor (int): The factor the soft dropping scales the current gravity by, or 'inf' for instant soft drop
        'PrevAccHD': True,   # Prevent Accidental Hard Drops (bool): When a piece locks on its own, the hard drop action is disabled for a few frames
        'PrevAccHDTime': 3,  # Prevent Accidental Hard Drops Time (int) in frames: The number of frames the hard drop action is disabled for after a piece automatically locks
        'DASCancel': False,  # Cancel DAS When Changing Directions (bool): If true, the DAS timer will reset if the opposite direction is pressed
        'PrefSD': True,      # Prefer Soft Drop Over Movement (bool): At very high speeds, the soft drop action will be performed first if both the soft drop and movement keys are held
        'PrioriDir': True,   # Prioritize the Most Recent Direction (bool): whether to prioritise the most recent direction key over the other when both are held
        'SonicDrop': False   # Sonic Drop (bool): Whether to replace the hard drop action with the sonic drop action
    })
    
    
    UNCAPPED_FPS: bool = True
    FPS: int = 144
    TPS: int = 256
    POLLING_RATE: int = 1000

    def __post_init__(self):
        self.key_bindings[Action.SONIC_LEFT] = self.key_bindings[Action.MOVE_LEFT]
        self.key_bindings[Action.SONIC_RIGHT] = self.key_bindings[Action.MOVE_RIGHT]
        self.key_bindings[Action.SONIC_DROP] = self.key_bindings[Action.HARD_DROP]
        
        self.key_bindings[Action.SONIC_LEFT_DROP] = (self.key_bindings[Action.MOVE_LEFT][0], self.key_bindings[Action.SOFT_DROP][0])
        self.key_bindings[Action.SONIC_RIGHT_DROP] = (self.key_bindings[Action.MOVE_RIGHT][0], self.key_bindings[Action.SOFT_DROP][0])