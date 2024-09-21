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
            self.Config.key_bindings[Action.MOVE_LEFT]:                     {'current': False, 'previous': False},
            self.Config.key_bindings[Action.MOVE_RIGHT]:                    {'current': False, 'previous': False},
            self.Config.key_bindings[Action.ROTATE_CLOCKWISE]:              {'current': False, 'previous': False},
            self.Config.key_bindings[Action.ROTATE_COUNTERCLOCKWISE]:       {'current': False, 'previous': False},
            self.Config.key_bindings[Action.ROTATE_180]:                    {'current': False, 'previous': False},
            self.Config.key_bindings[Action.HARD_DROP]:                     {'current': False, 'previous': False},
            self.Config.key_bindings[Action.SOFT_DROP]:                     {'current': False, 'previous': False},
            self.Config.key_bindings[Action.HOLD]:                          {'current': False, 'previous': False},
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
        return self.key_states[self.Config.key_bindings[action]]['current'] and not self.key_states[self.Config.key_bindings[action]]['previous']
    
    def __is_action_down(self, action:Action):
        """
        Test if the action is down (pressed)
        
        args:
            action (Action): The action to be performed
        returns:
            bool: True if the action is down, False otherwise
        """
        return self.key_states[self.Config.key_bindings[action]]['current']
    
    def __set_action_state(self, action:Action, state:bool):
        """
        Set the action state
        
        args:
            action (Action): The action to be performed
            state (bool): The state of the action
        """
        self.actions[action]['state'] = state
        self.actions[action]['timestamp'] = self.HandlingStruct.current_time
        
    def __LeftRightMovementPriority(self, action:Action):
        """
        Prioritise the Most Recent Direction: when both the left and right keys are held the more recent key to be held will be prioritised
        or no movement will be performed if the relevant setting is False.
        
        args:
            action (Action): The action to be performed
        """
        if self.__is_action_down(Action.MOVE_LEFT) and self.__is_action_down(Action.MOVE_RIGHT) :
            if self.Config.HANDLING_SETTINGS['PrioriDir']: # if the setting is true, the most recent key will be prioritised
                if self.HandlingStruct.current_direction is Action.MOVE_LEFT:
                    self.__set_action_state(Action.MOVE_RIGHT, True)
                    self.__set_action_state(Action.MOVE_LEFT, False)
                else:
                    self.__set_action_state(Action.MOVE_LEFT, True)
                    self.__set_action_state(Action.MOVE_RIGHT, False)
            else:
                self.__set_action_state(action, False) # if left and right are pressed at the same time, no action is performed
            
        elif self.__is_action_down(Action.MOVE_LEFT):
            self.HandlingStruct.current_direction = action
            self.__set_action_state(Action.MOVE_LEFT, True)
            
        elif self.__is_action_down(Action.MOVE_RIGHT):
            self.HandlingStruct.current_direction = action
            self.__set_action_state(Action.MOVE_RIGHT, True) 
      
    def __test_actions(self, action:Action, check:callable):
        """
        Perform the state tests on an action and update the action state
        
        args:
            action (Action): The action to be performed
            check (callable): The function to be called to check the action state
        """
        if check(action):
            if action is Action.MOVE_LEFT or action is Action.MOVE_RIGHT:
                self.__LeftRightMovementPriority(action)
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
            if self.actions[action]['state'] is True:
                if action is Action.MOVE_LEFT or action is Action.MOVE_RIGHT:
                    self.__do_DAS_ARR(action)
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
        
    def __do_DAS_ARR(self, action:Action):
        """
        Perform the Delayed Auto Shift (DAS) and Auto Repeat Rate (ARR)
        
        args:
            action (Action): The action to be performed
        """	
        if self.HandlingStruct.do_movement:
            self.HandlingStruct.do_movement = False
            self.__queue_action(action)
            
        if self.HandlingStruct.instant_movement: # handle ARR of 0 separately
            self.HandlingStruct.instant_movement = False
            self.__instant_movement(action)      
             
    def __instant_movement(self, action:Action):
        """
        Instantly move the tetromino to the left or right without any delay (ARR = 0)
        
        args:
            action (Action): The action to be performed
        """
        for _ in range(0, self.Config.MATRIX_WIDTH):
            self.__queue_action(action)
            
    def __DAS(self):
        """
        If the Left/Right movement keys are held down, the DAS timer will be incremented until it reaches the DAS threshold (ms). 
        Once charged, the ARR will be performed at the set rate (ms).
        """
        if self.Config.HANDLING_SETTINGS['DASCancel']:
            self.__DAS_cancel()
      
        if self.__is_action_down(Action.MOVE_LEFT) or self.__is_action_down(Action.MOVE_RIGHT):
           
            if self.HandlingStruct.DAS_counter % self.Config.HANDLING_SETTINGS['DAS'] == 0 or self.HandlingStruct.DAS_counter >= self.Config.HANDLING_SETTINGS['DAS']:
                self.__ARR()
                     
            if self.HandlingStruct.DAS_counter >= self.Config.HANDLING_SETTINGS['DAS']:
                self.HandlingStruct.DAS_counter = self.Config.HANDLING_SETTINGS['DAS']
                
            else:
                q, r = divmod((self.HandlingStruct.current_time - self.HandlingStruct.prev_time) + self.HandlingStruct.das_remainder, self.polling_tick_time)
                self.HandlingStruct.das_remainder = r
                self.HandlingStruct.DAS_counter += int(q)
               
        else: # reset DAS & ARR if key is released
            self.__reset_DAS_ARR()

    def __DAS_cancel(self):
        """
        Cancel DAS When Changing Directions: The DAS timer will reset if the opposite direction is pressed
        """
        if self.__is_action_down(Action.MOVE_LEFT) and self.__is_action_down(Action.MOVE_RIGHT):
            self.__reset_DAS_ARR()
        
    def __ARR(self):
        """
        If the DAS timer is charged, the ARR timer will be incremented until it reaches the ARR threshold (ms).
        Once charged, the action will be performed and the ARR timer will be reset.
        """ 
        if self.Config.HANDLING_SETTINGS['ARR'] == 0: # to avoid modulo by zero
            self.HandlingStruct.do_movement = True
            if self.HandlingStruct.DAS_counter >= self.Config.HANDLING_SETTINGS['DAS']:
                self.HandlingStruct.instant_movement = True # when ARR = 0, the movement is instant (no delay since inf repeat rate)
        else:
            if self.HandlingStruct.ARR_counter % self.Config.HANDLING_SETTINGS['ARR'] == 0 or self.HandlingStruct.ARR_counter >= self.Config.HANDLING_SETTINGS['ARR']:
                self.HandlingStruct.do_movement = True  
                self.HandlingStruct.ARR_counter = 0
            
            if self.HandlingStruct.DAS_counter >= self.Config.HANDLING_SETTINGS['DAS']:
                q, r = divmod((self.HandlingStruct.current_time - self.HandlingStruct.prev_time) + self.HandlingStruct.arr_remainder, self.polling_tick_time)
                self.HandlingStruct.arr_remainder = r  
                self.HandlingStruct.ARR_counter += int(q)
                
    def __reset_DAS_ARR(self):
        """
        Reset DAS once the action has been performed
        """
        self.HandlingStruct.DAS_counter = 0
        self.done_inital_ARR_movement = False
        self.done_one_move = False
        self.HandlingStruct.DAS_charged = False
        self.HandlingStruct.instant_movement = False
        self.HandlingStruct.ARR_counter = 0
    