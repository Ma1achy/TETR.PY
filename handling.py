from enum import Enum, auto
import pygame as pygame
from collections import deque

# TODO:
# - Implement key priority for left/right movement, i.e if right is held and ten left is pressed, the left action should be prioritized (most recent action)
class Action(Enum):
    """
    Actions that can be performed
    """
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
        """
        Handle the key inputs and provide the actions to the game loop in a queue.
        
        args:	
        pgconfig (PyGameConfig): The pygame configuration
        """
        
        self.pgconfig = pgconfig
        self.current_time = 0
        self.dt = 0
        self.delta_tick = 0
        
        self.buffer_threshold = 128 # tick range where old actions are still considered valid
        self.action_queue = deque()
        
        self.done_one_move = False
        self.DAS_timer = 0
        self.ARR_timer = 0
        
        self.prev_time = 0
    
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
            'ARR' :0,           # Auto repeat rate: The speed at which tetrominoes move when holding down the movement keys (ms)
            'DAS' :70,          # Delayed Auto Shift: The time between the inital key press and the automatic repeat movement (ms)
            'DCD' :0,           # DAS Cut Delay: If none-zero, any ongoing DAS movement will pause for a set amount of time after dropping/rorating a piece (ms)
            'SDF' :6,           # Soft Drop Facor: The factor the soft dropping scales the current gravity by
            'PrevAccHD': True,  # Prevent Accidental Hard Drops: When a piece locks on its own, the harddrop action is disabled for a few frames
            'DASCancel': False, # Cancel DAS When Changing Directions: If true, the DAS timer will reset if the opposite direction is pressed
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
        
    def GetEmptyActions(self):
        """
        Return an empty actions dictionary
        """
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
        """
        Hook that is called within the game loop before the tick is executed to obtain the current action states to be used in the game loop
        """
        self.__get_actions() # has to be before the key states are forwarded or toggled actions will not be detected (can't belive this took 2 hours to figure out)
        self.__forward_key_states()     
        return self.action_queue
    
    def __get_actions(self):
        """
        Get the actions from the key states and add them to the action buffer
        """
        self.__test_actions(Action.MOVE_LEFT, self.__is_action_down)
        
        self.__test_actions(Action.MOVE_RIGHT, self.__is_action_down)
        
        self.__test_actions(Action.ROTATE_CLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_COUNTERCLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_180, self.__is_action_toggled)
        
        self.__test_actions(Action.HARD_DROP, self.__is_action_toggled)
        
        self.__test_actions(Action.SOFT_DROP, self.__is_action_down)
        
        self.__test_actions(Action.HOLD, self.__is_action_toggled)
        
        self.__DAS()
        
        self.get_action_buffer() # add actions to buffer
        
        self.prev_time = self.current_time
        
    def __forward_key_states(self):
        """
        Forward the key states for comaprison in the future (allows for toggle/hold detection)
        """
        for k in self.key_states:
            self.key_states[k]['previous'] = self.key_states[k]['current']
    
    def __is_action_toggled(self, action:Action):
        """
        Test if the action is toggled (pressed and released)
        """
        return self.key_states[self.key_bindings[action]]['current'] and not self.key_states[self.key_bindings[action]]['previous']
    
    def __is_action_down(self, action:Action):
        """
        Test if the action is down (pressed)
        """
        return self.key_states[self.key_bindings[action]]['current']
    
    def __test_actions(self, action, check):
        """
        Perform the state tests on an action and update the action state
        """
        
        if check(action):
            self.actions[action]['state'] = True
            self.actions[action]['timestamp'] = self.current_time
            
        else:
            self.actions[action]['state'] =  False,
            self.actions[action]['timestamp'] = self.current_time
                 
    def __get_key_info(self, key):
        """
        Get the key info from the key object
        """
        
        try:
            k = key.char
            
        except AttributeError:
            k = key
        
        return k
                           
    def on_key_press(self, key):
        """
        Handle the key press event
        
        key (pygame.key): The key object
        """
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = True
          
        except KeyError:
            return
    
    def on_key_release(self, key):
        """
        Handle the key release event
        
        args:
        key (pygame.key): The key object
        """
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = False
             
        except KeyError:
            return  
        
    def get_action_buffer(self):
        """
        Get the actions that are currently active and add them to the queue.
        """
        
        for action in self.actions:
            if self.actions[action]['state'] is True:
                if action is Action.MOVE_LEFT or action is Action.MOVE_RIGHT:
                    self.__do_DAS_ARR(action)
                else:
                    self.action_queue.append(({'action': action, 'timestamp': self.actions[action]['timestamp']}))       
                    
    def consume_action(self):
        """
        Consume the action from the queue
        """
        if self.action_queue:
            return self.action_queue.popleft()  
        return None
    
    def __do_DAS_ARR(self, action):
        if not self.done_one_move: # only add the action once if DAS is not done to allow for tapping
            self.action_queue.append(({'action': action, 'timestamp': self.actions[action]['timestamp']}))
            self.done_one_move = True
            
        if self.do_ARR:
            if self.handling_settings['ARR'] == 0: # arr of 0 gives instant movement to the sides (inf repeat)
                self.__instant_movement(action)
            else:
                self.action_queue.append(({'action': action, 'timestamp': self.actions[action]['timestamp']}))
                self.__reset_ARR() 

    def __instant_movement(self, action):
        for _ in range(0, self.pgconfig.MATRIX_WIDTH):
            self.action_queue.append(({'action': action, 'timestamp': self.actions[action]['timestamp']}))
            
    def __DAS(self):
        """
        If the Left/Right movement keys are held down, the DAS timer will be incremented until it reaches the DAS threshold (ms). 
        Once charged, the ARR will be performed at the set rate (ms).
        """

        if self.handling_settings['DASCancel']:
            self.__DAS_cancel()
    
        if (self.key_states[self.key_bindings[Action.MOVE_LEFT]]['current'] and self.key_states[self.key_bindings[Action.MOVE_LEFT]]['previous']) or (self.key_states[self.key_bindings[Action.MOVE_RIGHT]]['current'] and self.key_states[self.key_bindings[Action.MOVE_RIGHT]]['previous']):
            self.DAS_timer += self.current_time - self.prev_time
            
            if self.DAS_timer >= self.handling_settings['DAS'] / 1000 :
                self.DAS_timer = self.handling_settings['DAS'] / 1000
                self.__ARR()
                
        else: # reset DAS/ARR if key is released
            self.DAS_timer = 0
            self.done_one_move = False
            self.__reset_ARR()

    def __DAS_cancel(self):
        """
        Cancel DAS When Changing Directions: The DAS timer will reset if the opposite direction is pressed
        """
        if (self.key_states[self.key_bindings[Action.MOVE_LEFT]]['current'] and self.key_states[self.key_bindings[Action.MOVE_RIGHT]]['previous']) or (self.key_states[self.key_bindings[Action.MOVE_RIGHT]]['current'] and self.key_states[self.key_bindings[Action.MOVE_LEFT]]['previous']):
            self.DAS_timer = 0
            self.ARR_timer = 0
        
    def __ARR(self):
        """
        If the DAS timer is charged, the ARR timer will be incremented until it reaches the ARR threshold (ms).
        Once charged, the action will be performed and the ARR timer will be reset.
        """
        if self.ARR_timer >= self.handling_settings['ARR'] /1000:
            self.ARR_timer = 0
            self.do_ARR = True
            
        elif self.DAS_timer >= self.handling_settings['DAS'] /1000:
            self.ARR_timer += self.current_time - self.prev_time
            
    def __reset_ARR(self):
        """
        Reset ARR
        """
        self.do_ARR = False
        self.ARR_timer = 0

    
    
    
                    
                
        
                