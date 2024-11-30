from enum import Enum, auto

class UIAction(Enum):
    
    MENU_LEFT = auto()
    MENU_RIGHT = auto()
    MENU_UP = auto()
    MENU_DOWN = auto()
    MENU_CONFIRM = auto()
    MENU_BACK = auto()
    
    MENU_DEBUG = auto()
    
class MenuKeyboardInputHandler():
    def __init__(self, key_states_queue, key_bindings, menu_actions_queue, PRINT_WARNINGS):
        self.key_states_queue = key_states_queue
        self.key_bindings = key_bindings
        self.PRINT_WARNINGS = PRINT_WARNINGS
        self.actions = self.__get_empty_actions()
        self.menu_actions_queue = menu_actions_queue
        self.key_states = self.__get_empty_key_states()

    def __get_empty_key_states(self):
        return {
            key: {'current': False, 'previous': False}
            for action, keys in self.key_bindings.items()
            for key in keys
        }
        
    def __get_empty_actions(self):
        return {action: False for action in UIAction}
    
    def __forward_key_states(self):
        """
        Forward the key states for comaprison in the future (allows for toggle/hold detection)
        """
        for k in self.key_states:
            self.key_states[k]['previous'] = self.key_states[k]['current']
    
    def tick(self):
        self.__get_key_states()
        self.__get_actions()
        self.__forward_key_states()
    
    def __get_key_states(self):
        if not self.key_states_queue.empty():
            key_states = self.key_states_queue.queue[0]
        else:
            key_states = self.__get_empty_key_states()
        
        for key, state in key_states.items():
            if key not in self.key_states:
                return
            
            self.key_states[key]['previous'] = key_states[key]['previous']
            self.key_states[key]['current'] = key_states[key]['current']
            
       
    def __get_actions(self):
        
        self.__test_actions(UIAction.MENU_LEFT, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_RIGHT, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_UP, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_DOWN, self.__is_action_down)
        
        self.__test_actions(UIAction.MENU_CONFIRM, self.__is_action_toggled)
        
        self.__test_actions(UIAction.MENU_BACK, self.__is_action_toggled)
        
        self.__test_actions(UIAction.MENU_DEBUG, self.__is_action_toggled)
        
        self.__queue_actions()
    
    def __is_action_down(self, action):
        return all(self.key_states[key]['current'] for key in self.key_bindings[action])
        
    def __is_action_toggled(self, action):
        return all(self.key_states[key]['current'] and not self.key_states[key]['previous'] for key in self.key_bindings[action])\
    
    def __test_actions(self, action, check):
        if check(action):
            self.__set_action_state(action, True)
        else:
            self.__set_action_state(action, False)
    
    def __set_action_state(self, action, state):
        self.actions[action] = state
        
    def __queue_actions(self):
        self.menu_actions_queue.put(self.actions)
