from enum import Enum, auto
import pygame as pygame
from collections import deque

# TODO:
# - Seperate DAS and ARR timers for left and right movement
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
    
    # ARR == 0 behaviour
    SONIC_LEFT = auto()
    SONIC_RIGHT = auto()
    
    # inf SDF behaviour
    SONIC_DROP = auto()
    
    # ARR == 0 & inf SDF behaviour
    SONIC_LEFT_DROP = auto()
    SONIC_RIGHT_DROP = auto()
    
class Handling():
    def __init__(self, Config, HandlingStruct):
        """
        Handle the key inputs and provide the actions to the game loop in a queue.
        
        args:	
            config (Config): The game configuration
        
        methods:
            before_loop_hook(key): Hook that is called within the game loop before the tick is executed to obtain the current action states to be used in the game loop
            on_key_press(key): Handle the key press event
            on_key_release(key): Handle the key release event
            consume_action(): Consume the oldset action in the queue
        """
        
        self.Config = Config
        self.HandlingStruct = HandlingStruct
        self.polling_tick_time = 1 / self.Config.POLLING_RATE
     
        self.actions = self.__GetEmptyActions()
        self.action_queue = deque()
        
        self.key_states = {
            key: {'current': False, 'previous': False}
            for action, keys in self.Config.key_bindings.items()
            for key in keys
        }
        
        self.direction_of_action = {
            Action.MOVE_LEFT: 'left',
            Action.MOVE_RIGHT: 'right',
            Action.SONIC_LEFT: 'left',
            Action.SONIC_RIGHT: 'right',
            Action.SONIC_LEFT_DROP: 'left',
            Action.SONIC_RIGHT_DROP: 'right'
        }
        
    def __GetEmptyActions(self):
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
            Action.HOLD:                        {'state': False, 'timestamp': 0},
            Action.SONIC_LEFT:                  {'state': False, 'timestamp': 0},
            Action.SONIC_RIGHT:                 {'state': False, 'timestamp': 0},
            Action.SONIC_DROP:                  {'state': False, 'timestamp': 0},
            Action.SONIC_LEFT_DROP:             {'state': False, 'timestamp': 0},
            Action.SONIC_RIGHT_DROP:            {'state': False, 'timestamp': 0}
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
        self.__DAS_LEFT()
        
        self.__DAS_RIGHT()
        
        if self.Config.HANDLING_SETTINGS['SDF'] == 'inf' and self.Config.HANDLING_SETTINGS['ARR'] == 0:     
            if self.HandlingStruct.DAS_LEFT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.__test_actions(Action.SONIC_LEFT_DROP, self.__is_action_down)
                
            elif self.HandlingStruct.DAS_RIGHT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.__test_actions(Action.SONIC_RIGHT_DROP, self.__is_action_down)
        
        if not(self.__is_action_down(Action.SONIC_LEFT_DROP) or self.__is_action_down(Action.SONIC_RIGHT_DROP)) and (self.Config.HANDLING_SETTINGS['SDF'] == 'inf' and self.Config.HANDLING_SETTINGS['PrefSD']):
            self.__test_actions(Action.SONIC_DROP, self.__is_action_down)
        else:
            self.__test_actions(Action.SOFT_DROP, self.__is_action_down)
                
        if not(self.__is_action_down(Action.SONIC_LEFT_DROP) or self.__is_action_down(Action.SONIC_RIGHT_DROP)) and self.Config.HANDLING_SETTINGS['ARR'] == 0:
            if self.HandlingStruct.DAS_LEFT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.__test_actions(Action.SONIC_LEFT, self.__is_action_down)
                
            elif self.HandlingStruct.DAS_RIGHT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.__test_actions(Action.SONIC_RIGHT, self.__is_action_down)  
        else:
            self.__test_actions(Action.MOVE_LEFT, self.__is_action_down)
            self.__test_actions(Action.MOVE_RIGHT, self.__is_action_down)

        self.__test_actions(Action.ROTATE_CLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_COUNTERCLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_180, self.__is_action_toggled)
        
        self.__test_actions(Action.HARD_DROP, self.__is_action_toggled)
        
        self.__test_actions(Action.HOLD, self.__is_action_toggled)
        
        self.__get_action_buffer() # add actions to buffer
        
        self.HandlingStruct.prev_time = self.HandlingStruct.current_time
           
    def __forward_key_states(self):
        """
        Forward the key states for comaprison in the future (allows for toggle/hold detection)
        """
        for k in self.key_states:
            self.key_states[k]['previous'] = self.key_states[k]['current']
    
    def __is_action_toggled(self, action:Action):
        """
        Test if the action is toggled (pressed and released)
        
        args:
            action (Action): The action to be performed
        """
        return all(self.key_states[key]['current'] and not self.key_states[key]['previous'] for key in self.Config.key_bindings[action])
    
    def __is_action_down(self, action:Action):
        """
        Test if the action is down (pressed)
        
        args:
            action (Action): The action to be performed
        returns:
            bool: True if the action is down, False otherwise
        """
        return all(self.key_states[key]['current'] for key in self.Config.key_bindings[action])
    
    def __is_direction_down(self, direction: str) -> bool:
        """
        Test if any of the actions associated with the given direction are down.
        
        Args:
            direction (str): The direction to be tested ('left' or 'right').
            
        Returns:
            bool: True if any action in the given direction is down, False otherwise.
        """
        for action, action_direction in self.direction_of_action.items():
            if action_direction == direction and self.__is_action_down(action):
                return True
        return False
        
    def __set_action_state(self, action:Action, state:bool):
        """
        Set the action state
        
        args:
            action (Action): The action to be performed
            state (bool): The state of the action
        """
        self.actions[action]['state'] = state
        self.actions[action]['timestamp'] = self.HandlingStruct.current_time
        
    def __LeftRightMovementPriority(self, action_1: Action, action_2: Action):
        """
        Prioritise the most recent direction: when both left and right directions are held,
        the more recent key (direction) will be prioritized, or no movement will be performed if the relevant setting is False.

        args:
            action_1 (Action): The first action to compare.
            action_2 (Action): The second action to compare.
        """
        direction_1 = self.direction_of_action[action_1]
        direction_2 = self.direction_of_action[action_2]

        if self.__is_direction_down(direction_1) and self.__is_direction_down(direction_2):
            if self.Config.HANDLING_SETTINGS['PrioriDir']:  # if the setting is true, the most recent key will be prioritised
                if self.HandlingStruct.current_direction == direction_1:
                    self.__set_action_state(action_2, True)
                    self.__set_action_state(action_1, False)
                    
                elif self.HandlingStruct.current_direction == direction_2:
                    self.__set_action_state(action_1, True)
                    self.__set_action_state(action_2, False)
            else:  # if left and right are pressed at the same time, no action is performed
                self.__set_action_state(action_1, False)
                self.__set_action_state(action_2, False)

        elif self.__is_direction_down(direction_1): # if only one direction is pressed, that direction is prioritised
            self.HandlingStruct.current_direction = direction_1
            self.__set_action_state(action_1, True)

        elif self.__is_direction_down(direction_2):
            self.HandlingStruct.current_direction = direction_2
            self.__set_action_state(action_2, True)
      
    def __test_actions(self, action:Action, check:callable):
        """
        Perform the state tests on an action and update the action state
        
        args:
            action (Action): The action to be performed
            check (callable): The function to be called to check the action state
        """
        if check(action):
            if action is Action.MOVE_LEFT:
                self.__LeftRightMovementPriority(action, Action.MOVE_RIGHT)
            elif action is Action.MOVE_RIGHT:
                self.__LeftRightMovementPriority(action, Action.MOVE_LEFT)
            elif action is Action.SONIC_LEFT:
                self.__LeftRightMovementPriority(action, Action.SONIC_RIGHT)
            elif action is Action.SONIC_RIGHT:
                self.__LeftRightMovementPriority(action, Action.SONIC_LEFT)
            elif action is Action.SONIC_LEFT_DROP:
                self.__LeftRightMovementPriority(action, Action.SONIC_RIGHT_DROP)
            elif action is Action.SONIC_RIGHT_DROP:
                self.__LeftRightMovementPriority(action, Action.SONIC_LEFT_DROP)
            else:
                self.__set_action_state(action, True)  
        else:
            self.__set_action_state(action, False)
                     
    def __get_key_info(self, key:pygame.key):
        """
        Get the key info from the key object
        
        args:
            key (pygame.key): The key object
        """
        
        try:
            k = key.char
            
        except AttributeError:
            k = key
        
        return k
                           
    def on_key_press(self, key:pygame.key):
        """
        Handle the key press event
        
        args:
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
    
    def on_key_release(self, key:pygame.key):
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
        
    def __get_action_buffer(self):
        """
        Get the actions that are currently active and add them to the queue.
        """
        for action in self.actions:
            if self.actions[action]['state']:
                if action is Action.MOVE_LEFT:
                    self.__do_DAS_ARR_LEFT(action)
                elif action is Action.MOVE_RIGHT:
                    self.__do_DAS_ARR_RIGHT(action)
                else:
                    self.__queue_action(action)
                                 
    def consume_action(self):
        """
        Consume the oldset action from the queue
        """
        if self.action_queue:
            return self.action_queue.popleft()  
        return None
    
    def __queue_action(self, action:Action):
        """
        Add an action to the queue
        
        args:
            action (Action): The action to add to the queue
        """
        self.action_queue.append(({'action': action, 'timestamp': self.actions[action]['timestamp']}))
        
    def __do_DAS_ARR_LEFT(self, action:Action):
        """
        Perform the Delayed Auto Shift (DAS) and Auto Repeat Rate (ARR)
        
        args:
            action (Action): The action to be performed
        """	
        if self.HandlingStruct.DO_MOVEMENT_LEFT:
            self.HandlingStruct.DO_MOVEMENT_LEFT = False
            print(action)
            self.__queue_action(action)
        
    def __do_DAS_ARR_RIGHT(self, action:Action):
        """
        Perform the Delayed Auto Shift (DAS) and Auto Repeat Rate (ARR)
        
        args:
            action (Action): The action to be performed
        """	
        if self.HandlingStruct.DO_MOVEMENT_RIGHT:
            self.HandlingStruct.DO_MOVEMENT_RIGHT = False
            self.__queue_action(action)
            
    def __DAS_LEFT(self):
        """
        If the Left/Right movement keys are held down, the DAS timer will be incremented until it reaches the DAS threshold (ms). 
        Once charged, the ARR will be performed at the set rate (ms).
        """
        if self.Config.HANDLING_SETTINGS['DASCancel']: # if the opposite direction is pressed, the DAS timer will reset for the previous direction
            self.__DAS_cancel()
      
        if self.__is_direction_down('left'):
           
            if self.HandlingStruct.DAS_LEFT_COUNTER % self.Config.HANDLING_SETTINGS['DAS'] == 0 or self.HandlingStruct.DAS_LEFT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.__ARR_LEFT()
                     
            if self.HandlingStruct.DAS_LEFT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.HandlingStruct.DAS_LEFT_COUNTER = self.Config.HANDLING_SETTINGS['DAS']
                
            else:
                q, r = divmod((self.HandlingStruct.current_time - self.HandlingStruct.prev_time) + self.HandlingStruct.DAS_LEFT_COUNTER_REMAINDER, self.polling_tick_time)
                self.HandlingStruct.DAS_LEFT_COUNTER_REMAINDER = r
                self.HandlingStruct.DAS_LEFT_COUNTER += int(q)
        
        else:
            self.__reset_DAS_ARR('left')
    
    def __DAS_RIGHT(self):
        """
        If the Left/Right movement keys are held down, the DAS timer will be incremented until it reaches the DAS threshold (ms). 
        Once charged, the ARR will be performed at the set rate (ms).
        """
        if self.Config.HANDLING_SETTINGS['DASCancel']:
            self.__DAS_cancel()
            
        if self.__is_direction_down('right'):
            
            if self.HandlingStruct.DAS_RIGHT_COUNTER % self.Config.HANDLING_SETTINGS['DAS'] == 0 or self.HandlingStruct.DAS_RIGHT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.__ARR_RIGHT()
            
            if self.HandlingStruct.DAS_RIGHT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                self.HandlingStruct.DAS_RIGHT_COUNTER = self.Config.HANDLING_SETTINGS['DAS']
            
            else:
                q, r = divmod((self.HandlingStruct.current_time - self.HandlingStruct.prev_time) + self.HandlingStruct.DAS_RIGHT_COUNTER_REMAINDER, self.polling_tick_time)
                self.HandlingStruct.DAS_RIGHT_COUNTER_REMAINDER = r
                self.HandlingStruct.DAS_RIGHT_COUNTER += int(q)
               
        else:
            self.__reset_DAS_ARR('right')

    def __DAS_cancel(self):
        """
        Cancel DAS When Changing Directions: The DAS timer will reset for the previous direction if the opposite direction is pressed
        """
        if self.__is_direction_down('left') and self.__is_direction_down('right'):
            if self.HandlingStruct.current_direction == 'right':
                self.__reset_DAS_ARR('left')
            elif self.HandlingStruct.current_direction == 'left':
                self.__reset_DAS_ARR('right')
    
    def __ARR_LEFT(self):
        """
        If the DAS timer is charged, the ARR timer will be incremented until it reaches the ARR threshold (ms).
        Once charged, the action will be performed and the ARR timer will be reset.
        """ 
        if self.Config.HANDLING_SETTINGS['ARR'] == 0: # to avoid modulo by zero
            self.HandlingStruct.DO_MOVEMENT_LEFT = True
        else:
            if self.HandlingStruct.ARR_LEFT_COUNTER % self.Config.HANDLING_SETTINGS['ARR'] == 0 or self.HandlingStruct.ARR_LEFT_COUNTER >= self.Config.HANDLING_SETTINGS['ARR']:
                self.HandlingStruct.DO_MOVEMENT_LEFT = True  
                self.HandlingStruct.ARR_LEFT_COUNTER = 0
            
            if self.HandlingStruct.DAS_LEFT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                q, r = divmod((self.HandlingStruct.current_time - self.HandlingStruct.prev_time) + self.HandlingStruct.ARR_LEFT_COUNTER_REMAINDER, self.polling_tick_time)
                self.HandlingStruct.ARR_LEFT_COUNTER_REMAINDER = r  
                self.HandlingStruct.ARR_LEFT_COUNTER += int(q)
                
    def __ARR_RIGHT(self):
        """
        If the DAS timer is charged, the ARR timer will be incremented until it reaches the ARR threshold (ms).
        Once charged, the action will be performed and the ARR timer will be reset.
        """ 
        if self.Config.HANDLING_SETTINGS['ARR'] == 0:
            self.HandlingStruct.DO_MOVEMENT_RIGHT = True
        else:
            if self.HandlingStruct.ARR_RIGHT_COUNTER % self.Config.HANDLING_SETTINGS['ARR'] == 0 or self.HandlingStruct.ARR_RIGHT_COUNTER >= self.Config.HANDLING_SETTINGS['ARR']:
                self.HandlingStruct.DO_MOVEMENT_RIGHT = True
                self.HandlingStruct.ARR_RIGHT_COUNTER = 0
                
            if self.HandlingStruct.DAS_RIGHT_COUNTER >= self.Config.HANDLING_SETTINGS['DAS']:
                q, r = divmod((self.HandlingStruct.current_time - self.HandlingStruct.prev_time) + self.HandlingStruct.ARR_RIGHT_COUNTER_REMAINDER, self.polling_tick_time)
                self.HandlingStruct.ARR_RIGHT_COUNTER_REMAINDER = r
                self.HandlingStruct.ARR_RIGHT_COUNTER += int(q)
                
    def __reset_DAS_ARR(self, direction:str = None):
        """
        Reset DAS once the action has been performed
        """
        if direction == 'left':
            self.HandlingStruct.DAS_LEFT_COUNTER = 0
            self.HandlingStruct.DAS_LEFT_COUNTER_REMAINDER = 0
            self.HandlingStruct.ARR_LEFT_COUNTER = 0
            self.HandlingStruct.ARR_LEFT_COUNTER_REMAINDER = 0

        elif direction == 'right':
            self.HandlingStruct.DAS_RIGHT_COUNTER = 0
            self.HandlingStruct.DAS_RIGHT_COUNTER_REMAINDER = 0
            self.HandlingStruct.ARR_RIGHT_COUNTER = 0 
            self.HandlingStruct.ARR_RIGHT_COUNTER_REMAINDER = 0
        else:
            self.__reset_DAS_ARR('left')
            self.__reset_DAS_ARR('right')