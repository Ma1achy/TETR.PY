import pygame
from pygame_config import PyGameConfig
from handling import Action, Handling, GetEmptyActions

# TODO: IMPLEMENT BASIC INPUT HANDLING AGAIN

class PyGameInstance():
    def __init__(self):
        
        self.config = PyGameConfig
        self.window = self.__init_window()
        self.actions = GetEmptyActions()
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.update_interval = 1/self.config.FPS
        self.exited = False
        
        self.key_bindings = Handling.key_bindings
        
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
    
    def __initialise(self):
        """
        Initalise the game
        """
        pygame.init()
        pygame.font.init()
        
    def __init_window(self):
        """
        Create the window
        """
        pygame.display.set_caption(self.config.CAPTION)
        return pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
    
    def before_loop_hook(self):
        self.__get_actions() # has to be before the key states are forwarded or toggled actions will not be detected (can't belive this took 2 hours to figure out)
        self.__forward_key_states() 
        return self.actions
        
    def run(self, four):
        
        self.__initialise()
        
        while not self.exited:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__exit()
                
                elif event.type == pygame.KEYDOWN:
                    self.__on_key_press(event.key)
                
                elif event.type == pygame.KEYUP:
                    self.__on_key_release(event.key)
                
            self.dt += self.clock.get_time()
            
            if self.dt > self.update_interval:
                four.loop()
                _ , self.dt = divmod(self.dt, self.update_interval)

            self.clock.tick(self.config.FPS)
    
    def __get_actions(self):
        self.__test_actions(Action.MOVE_LEFT, self.__is_action_down)
        
        self.__test_actions(Action.MOVE_RIGHT, self.__is_action_down)
        
        self.__test_actions(Action.ROTATE_CLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_COUNTERCLOCKWISE, self.__is_action_toggled)
        
        self.__test_actions(Action.ROTATE_180, self.__is_action_toggled)
        
        self.__test_actions(Action.HARD_DROP, self.__is_action_toggled)
        
        self.__test_actions(Action.SOFT_DROP, self.__is_action_down)
        
        self.__test_actions(Action.HOLD, self.__is_action_toggled)
            
    def __forward_key_states(self):
        for k in self.key_states:
            self.key_states[k]['previous'] = self.key_states[k]['current']
      
    def __is_action_toggled(self, action:Action):      
        return self.key_states[self.key_bindings[action]]['current'] and not self.key_states[self.key_bindings[action]]['previous']
    
    def __is_action_down(self, action:Action):
        return self.key_states[self.key_bindings[action]]['current']
    
    def __test_actions(self, action, check):
        
        if check(action):
            self.actions[action] = True
        else:
            self.actions[action] = False
        
    def __get_key_info(self, key):
        
        try:
            k = key.char
            
        except AttributeError:
            k = key
        
        return k
                           
    def __on_key_press(self, key):
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = True
             
        except KeyError:
            return
    
    def __on_key_release(self, key):
        
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = False
             
        except KeyError:
            return  
           
    def play_sound(self, sound:str):
        match sound:
            case 'hard drop':
                pass
            case 'lock':
                pass
            case 'single':
                pass
            case 'double':
                pass	
            case 'triple':
                pass
            case 'quadruple':
                pass
            case 't spin':
                pygame.mixer.music.load("SE/t_spin.wav")
                pygame.mixer.music.set_volume(0.20)
                pygame.mixer.music.play()
            case 'hold':
                pass
            case 'pre-rotate':
                pass
            case 'slide left':
                pass
            case 'slide right':
                pass
            case 'warning':
                pass
    
    def __exit(self):
        """
        Exit the game
        """
        self.exited = True
        pygame.quit()