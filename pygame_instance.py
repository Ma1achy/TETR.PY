import pygame
from pygame_config import PyGameConfig
from handling import Action, Handling, GetEmptyActions
from four import Four
from render import Render
import time, math

# TODO: IMPLEMENT BASIC INPUT HANDLING AGAIN

class PyGameInstance():
    def __init__(self):
        
        self.config = PyGameConfig
        self.window = self.__init_window()
        self.actions = GetEmptyActions()
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.update_interval = 1000/self.config.TPS
        self.exited = False
        self.render = Render(self.window)
        
        self.subframe_times = []
        self.render_times = []
        
        self.subframe_time = 0
        self.render_time = 0
        
        self.FPS = []
        self.average_FPS = 0
        self.TPS = []
        self.average_TPS = 0
        
        self.df = 0
        
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
    
    def run(self, four, DEBUG = True):
        
        self.__initialise()
        
        while not self.exited:
            
            if DEBUG:
                debug_dict = {
                    'FPS': self.average_FPS,
                    'TPS': self.average_TPS,
                    'SIM_T': self.subframe_time,
                    'REN_T': self.render_time,
                    'DF': self.df
                }
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__exit()
                
                elif event.type == pygame.KEYDOWN:
                    self.__on_key_press(event.key)
                
                elif event.type == pygame.KEYUP:
                    self.__on_key_release(event.key)
                
            self.dt += self.clock.get_time()
        
            if self.dt > self.update_interval:
                
                self.__do_subframe(four)
                
                _ , self.dt = divmod(self.dt, self.update_interval)
                self.df =  self.__calc_df(four)
                
            render_i = time.time()/1000
            self.render.render_frame(four, debug_dict)
            render_e = time.time()/1000
            self.__calc_render_time_avg(render_e - render_i)
            self.__calc_average_FPS()
            
            if self.config.UNCAPPED_FPS:
                self.clock.tick()
            else:
                self.clock.tick(self.config.FPS)
    
    def __do_subframe(self, four): 
        
        sim_i = time.time()/1000
        four.loop()
        sim_e = time.time()/1000
        self.__calc_subframe_time_avg(sim_e - sim_i)
        self.__calc_average_TPS(four)
                        
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
    
    def __get_fps(self):
        return self.clock.get_fps()
    
    def __get_tick_rate(self, four):
        return four.game_clock.get_fps()
    
    def __calc_subframe_time_avg(self, time):
        self.subframe_times.append(time)
        
        if len(self.subframe_times) > 60:
            half = len(self.subframe_times) // 2
            self.subframe_times = self.subframe_times[half:]
            
        self.subframe_time = sum(self.subframe_times)/len(self.subframe_times)
        
    def __calc_render_time_avg(self, time):
        self.render_times.append(time)
        
        if len(self.render_times) > 60:
            half = len(self.render_times) // 2
            self.render_times = self.render_times[half:]
            
        self.render_time =  sum(self.render_times)/len(self.render_times)
        
    def __calc_average_TPS(self, four):
        self.TPS.append(four.game_clock.get_fps())
    
        if len(self.TPS) > 60:
            half = len(self.TPS) // 2
            self.TPS = self.TPS[half:]
        
        self.average_TPS = sum(self.TPS)/len(self.TPS)
    
    def __calc_average_FPS(self):
        self.FPS.append(self.clock.get_fps())
       
        if len(self.FPS) > 60:
            half = len(self.FPS) // 2
            self.FPS = self.FPS[half:]
        
        self.average_FPS = sum(self.FPS)/len(self.FPS)
        
    def __calc_df(self, four):
        TPS = four.game_clock.get_fps()
        if int(TPS) > self.config.FPS:
            return 0
        
        df = int(self.config.TPS - TPS)
        
        if df < 0:
            return 0
        
        return df
    
        
def main():
    
    pygame_instance = PyGameInstance()
    four = Four(pygame_instance)  
    pygame_instance.run(four)

if __name__ == "__main__":
    main()