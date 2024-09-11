from enum import Enum, auto
import pygame as pygame
from collections import deque

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
    def __init__(self, pgconfig):
        
        self.pgconfig = pgconfig
        
        self.key_bindings = {
            Action.MOVE_LEFT:                   pygame.K_LEFT,
            Action.MOVE_RIGHT:                  pygame.K_RIGHT,
            Action.ROTATE_CLOCKWISE:            pygame.K_x,
            Action.ROTATE_COUNTERCLOCKWISE:     pygame.K_z,
            Action.ROTATE_180:                  pygame.K_SPACE,
            Action.HARD_DROP:                   pygame.K_DOWN,
            Action.SOFT_DROP:                   pygame.K_UP,
            Action.HOLD:                        pygame.K_c
        }
        
        self.handling_settings = {
            'ARR' :33,          # Auto repeat rate: The speed at which tetrominoes move when holding down the movement keys (ms)
            'DAS' :167,         # Delayed Auto Shift: The time between the inital key press and the automatic repeat movement (ms)
            'DCD' :0,           # DAS Cut Delay: If none-zero, any ongoing DAS movement will pause for a set amount of time after dropping/rorating a piece (ms)
            'SDF' :6,           # Soft Drop Facor: The factor the soft dropping scales the current gravity by
            'PrevAccHD': True,  # Prevent Accidental Hard Drops: When a piece locks on its own, the harddrop action is disabled for a few frames
            'DASCancel': False, # Cancel Das When Changing Directions: If true, the DAS counter will reset if the opposite direction is pressed
            'PrefSD': True,     # Prefer Soft Drop Over Movement: At very high speeds, the soft drop action will be prioritized over movement
        }
        
        self.actions = self.GetEmptyActions()
        self.key_bindings = self.key_bindings
        
        self.key_states = {
            self.key_bindings[Action.MOVE_LEFT]:                     {'current': False, 'previous': False},
            self.key_bindings[Action.MOVE_RIGHT]:                    {'current': False, 'previous': False},
            self.key_bindings[Action.ROTATE_CLOCKWISE]:              {'current': False, 'previous': False},
            self.key_bindings[Action.ROTATE_COUNTERCLOCKWISE]:       {'current': False, 'previous': False},
            self.key_bindings[Action.ROTATE_180]:                    {'current': False, 'previous': False},
            self.key_bindings[Action.HARD_DROP]:                     {'current': False, 'previous': False},
            self.key_bindings[Action.SOFT_DROP]:                     {'current': False, 'previous': False},
            self.key_bindings[Action.HOLD]:                          {'current': False, 'previous': False},
        }
        
        self.current_time = 0
        self.delta_tick = 0
        
        self.buffer_threshold = 128 # tick range where old actions are still considered valid
        self.actions_buffer = deque()
        
        self.DAS_counter = 0
        self.ARR_counter = 0
        
        self.clock = pygame.time.Clock()
            
    def GetEmptyActions(self):
        return {
            Action.MOVE_LEFT:                   {'state': False, 'timestamp': 0}, 
            Action.MOVE_RIGHT:                  {'state': False, 'timestamp': 0},
            Action.ROTATE_CLOCKWISE:            {'state': False, 'timestamp': 0},
            Action.ROTATE_COUNTERCLOCKWISE:     {'state': False, 'timestamp': 0},
            Action.ROTATE_180:                  {'state': False, 'timestamp': 0},
            Action.HARD_DROP:                   {'state': False, 'timestamp': 0},
            Action.SOFT_DROP:                   {'state': False, 'timestamp': 0},
            Action.HOLD:                        {'state': False, 'timestamp': 0}
        }
    
    def before_loop_hook(self):
        self.__get_actions() # has to be before the key states are forwarded or toggled actions will not be detected (can't belive this took 2 hours to figure out)
        self.__forward_key_states()     
        return self.actions_buffer
    
    def __get_actions(self):
    
        self.__test_actions(Action.MOVE_LEFT, self.__is_action_down)
        
        self.__test_actions(Action.MOVE_RIGHT, self.__is_action_down)
        
        self.__test_actions(Action.ROTATE_CLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_COUNTERCLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_180, self.__is_action_toggled)
        
        self.__test_actions(Action.HARD_DROP, self.__is_action_toggled)
        
        self.__test_actions(Action.SOFT_DROP, self.__is_action_down)
        
        self.__test_actions(Action.HOLD, self.__is_action_toggled)
        
        self.get_action_buffer() # add actions to buffer
        
    def __forward_key_states(self):
        for k in self.key_states:
            self.key_states[k]['previous'] = self.key_states[k]['current']
    
    def __is_action_toggled(self, action:Action):  
        return self.key_states[self.key_bindings[action]]['current'] and not self.key_states[self.key_bindings[action]]['previous']
    
    def __is_action_down(self, action:Action):
        return self.key_states[self.key_bindings[action]]['current']
    
    def __test_actions(self, action, check):
        
        if check(action):
            self.actions[action]['state'] = True
            self.actions[action]['timestamp'] = self.current_time
            
        else:
            self.actions[action]['state'] =  False,
            self.actions[action]['timestamp'] = self.current_time
            
            
    def __get_key_info(self, key):
        
        try:
            k = key.char
            
        except AttributeError:
            k = key
        
        return k
                           
    def on_key_press(self, key):
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = True
          
        except KeyError:
            return
    
    def on_key_release(self, key):
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = False
             
        except KeyError:
            return  
        
    def get_action_buffer(self):
        
        for action in self.actions:
            if self.actions[action]['state'] == True:
                self.actions_buffer.append(({'action': action, 'timestamp': self.actions[action]['timestamp']}))
                
   
    def consume_action(self):
        if self.actions_buffer:
            return self.actions_buffer.popleft()  
        return None
    
    # TODO: DAS AND ARR LOGIC
    # IF LEFT OR RIGHT IS HELD, INCREMENT DAS COUNTER UNTIL CHARGED THEN DO ARR COUNTER
    # IF DAS IS CHARGED INCREMENT ARR COUNTER
    
                    
                
        
                