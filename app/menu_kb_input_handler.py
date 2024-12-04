from enum import Enum, auto

class UIAction(Enum):
    
    MENU_LEFT = auto()
    MENU_RIGHT = auto()
    MENU_UP = auto()
    MENU_DOWN = auto()
    MENU_CONFIRM = auto()
    MENU_BACK = auto()
    
    MENU_DEBUG = auto()
    WINDOW_FULLSCREEN = auto()
    
class MenuKeyboardInputHandler():
    def __init__(self, Keyboard, key_bindings, Timing, PRINT_WARNINGS):
        
        self.Keyboard = Keyboard
        self.actions_to_queue = [] 
        
        self.Timing = Timing
        self.PRINT_WARNINGS = PRINT_WARNINGS
         
        self.key_bindings = key_bindings
        self.actions = self.__get_empty_actions()
        self.key_states = self.__get_empty_key_states()
           
        self.done_tap = False
        self.do_repeat_input = False
            
        self.Keyboard.DAS_delay = 167
        self.Keyboard.ARR_delay = 33
        self.Keyboard.DAS_counter = 0
        self.Keyboard.ARR_counter = 0
        self.Keyboard.DAS_remainder = 0
        self.Keyboard.ARR_remainder = 0
        
    def __get_empty_key_states(self):
        return {
            key: {'current': False, 'previous': False}
            for action, keys in self.key_bindings.items()
            for key in keys
        }
        
    def __get_empty_actions(self):
        return {action: {'state': False} for action in UIAction}
    
    def __forward_key_states(self):
        """
        Forward the key states for comaprison in the future (allows for toggle/hold detection)
        """
        for k in self.key_states:
            self.key_states[k]['previous'] = self.key_states[k]['current']
    
    def tick(self):
        self.__get_key_states()
        self.__perform_action_tests()
        self.__forward_key_states()
        
    def __get_key_states(self):
        if not self.Keyboard.key_states_queue.empty():
            key_states = self.Keyboard.key_states_queue.queue[0]
        else:
            return

        for key in key_states:
            try:
                self.key_states[key]['current'] = key_states[key]['current']
            
            except KeyError:
                pass
          
    def __perform_action_tests(self):
        
        self.current_time = self.Timing.current_frame_time
        self.delta_time = self.Timing.frame_delta_time
        
        self.__do_DAS_tick()
        
        self.__test_actions(UIAction.MENU_LEFT, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_RIGHT, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_UP, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_DOWN, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_CONFIRM, self.__is_action_toggled)
        
        self.__test_actions(UIAction.MENU_BACK, self.__is_action_toggled)
        
        self.__test_actions(UIAction.MENU_DEBUG, self.__is_action_toggled)
        
        self.__test_actions(UIAction.WINDOW_FULLSCREEN, self.__is_action_toggled)
        
        self.__get_actions()
        
        self.prev_time = self.current_time
    
    def __is_action_down(self, action):
        return all(self.key_states[key]['current'] for key in self.key_bindings[action])
        
    def __is_action_toggled(self, action):
        return all(self.key_states[key]['current'] and not self.key_states[key]['previous'] for key in self.key_bindings[action])
    
    def __test_actions(self, action, check):
        if check(action):
            self.__set_action_state(action, True)
        else:
            self.__set_action_state(action, False)
    
    def __set_action_state(self, action, state):
        self.actions[action]['state'] = state
        
    def __get_actions(self):
        
        self.actions_to_queue = []
        
        for action in self.actions:
            if self.actions[action]['state']:
                if action is UIAction.MENU_LEFT or action is UIAction.MENU_RIGHT or action is UIAction.MENU_DOWN or action is UIAction.MENU_UP:
                    self.__get_DAS_actions(action)
                else:
                    self.__queue_actions(action)
    
        self.Keyboard.menu_actions_queue.put(self.actions_to_queue)
        
    def __queue_actions(self, action):
        self.actions_to_queue.append(action)
        
    def __reset_DAS(self): 
        self.Keyboard.DAS_counter = 0
        self.Keyboard.DAS_remainder = 0
        self.Keyboard.ARR_counter = 0
        self.Keyboard.ARR_remainder = 0
        self.done_tap = False
    
    def __get_DAS_actions(self, action):
        if self.do_repeat_input:
            self.do_repeat_input = False
            self.__queue_actions(action)
    
    def __do_DAS_tick(self):
        
        if self.__is_action_down(UIAction.MENU_LEFT) or self.__is_action_down(UIAction.MENU_RIGHT) or self.__is_action_down(UIAction.MENU_DOWN) or self.__is_action_down(UIAction.MENU_UP):
            
            if self.Keyboard.DAS_counter % self.Keyboard.DAS_delay == 0 or self.Keyboard.DAS_counter >= self.Keyboard.DAS_delay:
                self.__do_ARR_tick()
            
            if self.Keyboard.DAS_counter >= self.Keyboard.DAS_delay:
                self.Keyboard.DAS_counter = self.Keyboard.DAS_delay
            
            else:
                q, r = divmod((self.current_time - self.prev_time) + self.Keyboard.DAS_remainder, self.delta_time)
                self.Keyboard.DAS_remainder = r
                self.Keyboard.DAS_counter += q
        
        else:
            self.__reset_DAS()

    def __do_ARR_tick(self):
        
        if not self.done_tap or self.Keyboard.ARR_counter >= self.Keyboard.ARR_delay:
            
            self.done_tap = True
            self.do_repeat_input = True
            self.Keyboard.ARR_counter = 0
            
        if self.Keyboard.DAS_counter >= self.Keyboard.DAS_delay:
            q, r = divmod((self.current_time - self.prev_time) + self.Keyboard.ARR_remainder, self.delta_time)
            self.Keyboard.ARR_remainder = r
            self.Keyboard.ARR_counter += q
            