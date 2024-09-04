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
        
        self.debug = True
        self.max_avg_len = 500
        
        self.tick_times = []
        self.sf_idx = 0
        self.worst_tick_time = 0
        
        self.render_times = []
        self.r_idx = 0
        self.worst_render_time = 0
        
        self.tick_time = 0
        self.render_time = 0
        
        self.FPS = []
        self.average_FPS = 0
        self.fps_idx = 0
        self.worst_fps = 0
        
        self.TPS = []
        self.average_TPS = 0
        self.tps_idx = 0
        self.worst_tps = 0
        
        self.df = 0
        self.worst_df = 0
        
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
            
            self.__get_debug_info(four)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__exit()
                
                elif event.type == pygame.KEYDOWN:
                    self.__on_key_press(event.key)
                
                elif event.type == pygame.KEYUP:
                    self.__on_key_release(event.key)
                
            self.dt += self.clock.get_time()
        
            if self.dt > self.update_interval:
                
                self.__do_tick(four)
                
                _ , self.dt = divmod(self.dt, self.update_interval)
                self.df =  self.__calc_df(four)
                
            self.__do_render(four)

            if self.config.UNCAPPED_FPS:
                self.clock.tick()
            else:
                self.clock.tick(self.config.FPS)
    
    def __do_tick(self, four): 
        
        sim_i = time.time()
        four.loop()
        sim_e = time.time()
        self.__calc_tick_time_avg(sim_e - sim_i)
        self.__calc_average_TPS(four)
        
    def __do_render(self, four):
        render_i = time.time()
        self.render.render_frame(four, self.debug_dict)
        render_e = time.time()
        self.__calc_render_time_avg(render_e - render_i)
        self.__calc_average_FPS()
                        
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
    
    def __calc_tick_time_avg(self, time):
        self.tick_times.append(time)
        if time >= self.worst_tick_time:
            self.worst_tick_time = time
        
        if self.sf_idx > self.max_avg_len:
            self.sf_idx = 0
            
        if len(self.tick_times) > self.max_avg_len:
            self.TPS.pop(self.sf_idx)
            
        self.tick_time = sum(self.tick_times)/len(self.tick_times)
        
    def __calc_render_time_avg(self, time):
        self.render_times.append(time)
        if time >= self.worst_render_time:
            self.worst_render_time = time
        
        if self.r_idx > self.max_avg_len:
            self.r_idx = 0
        
        if len(self.render_times) > self.max_avg_len:
            self.render_times.pop(self.r_idx)
            
        self.render_time =  sum(self.render_times)/len(self.render_times)
        
    def __calc_average_TPS(self, four):
        TPS = four.game_clock.get_fps()
        
        self.TPS.append(TPS)
        if TPS < self.worst_tps:
            self.worst_tps = TPS
    
        if self.tps_idx > self.max_avg_len:
            self.tps_idx = 0
        
        if len(self.TPS) > self.max_avg_len:
            self.TPS.pop(self.tps_idx)
        
        self.average_TPS = sum(self.TPS)/len(self.TPS)
    
    def __calc_average_FPS(self):
        FPS = self.clock.get_fps()
        self.FPS.append(FPS)
        if FPS < self.worst_fps:
            self.worst_fps = FPS
       
        if self.fps_idx > self.max_avg_len:
            self.fps_idx = 0
        
        if len(self.FPS) > self.max_avg_len:
            self.FPS.pop(self.fps_idx)
        
        self.average_FPS = sum(self.FPS)/len(self.FPS)
        
    def __calc_df(self, four):
        TPS = four.game_clock.get_fps()
        if int(TPS) > self.config.FPS:
            return 0
        
        df = int(self.config.TPS - TPS)
        
        if df < 0:
            return 0
        
        if df > self.worst_df:
            self.worst_df = df
        
        return df
    
    def __ignore_worst_counts_for_first_frames(self, four):
        if four.tick_counter < self.config.TPS * 16:
            self.worst_tick_time = 0
            self.worst_render_time = 0
            self.worst_fps = self.config.FPS
            self.worst_tps = self.config.TPS
            self.worst_df = 0
    
    def __get_debug_info(self, four):
        if self.debug:
            self.__ignore_worst_counts_for_first_frames(four)
            self.debug_dict = {
                'FPS': self.average_FPS,
                'TPS': self.average_TPS,
                'SIM_T': self.tick_time,
                'REN_T': self.render_time,
                'DF': self.df,
                'TICKCOUNT': four.tick_counter,
                'WORST_SIM_T': self.worst_tick_time,
                'WORST_REN_T': self.worst_render_time,
                'WORST_FPS': self.worst_fps,
                'WORST_TPS': self.worst_tps,
                'WORST_DF': self.worst_df,
            }
        else:
            self.debug_dict = None
def main():
    
    pygame_instance = PyGameInstance()
    four = Four(pygame_instance)  
    pygame_instance.run(four)

if __name__ == "__main__":
    main()