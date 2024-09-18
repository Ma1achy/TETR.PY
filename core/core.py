import pygame
from config import Config
from core.handling import Handling
from render.render import Render
import time
import asyncio
from collections import deque 
from core.handling import Action

class Core():
    def __init__(self):
        """
        Manage the game loop, key events, and rendering of the game
        
        methods:
            run(four): Run the instance of four
        """
        self.config = Config()
        
        self.window = self.__init_window()
        self.render = Render(self.window)
        self.handling = Handling(self.config)
        
        self.render_clock = Clock()
        
        self.current_time = 0
        self.last_tick_time = 0
        self.delta_time = 0
        self.time_per_tick = 1 / self.config.TPS
        self.do_first_tick = True
        self.tick_counter = 0
        self.tick_counter_last_cleared = 0
        
        self.current_frame_time = 0
        self.last_frame_time = 0
        self.delta_frame_time = 0
        self.frame_time = 1 / self.config.FPS
        self.draw_first_frame = True
         
        self.exited = False
        self.state_snapshot = None
        
        self.DEBUG = False
        
        self.debug_dict = None
        self.key_dict = None
        self.max_avg_len = 500
        
        self.tick_times = []
        self.exe_idx = 0
        self.worst_tick_time = 0
        self.best_tick_time = 0
        
        self.render_times = []
        self.r_idx = 0
        self.worst_render_time = 0
        self.best_render_time = 0
        
        self.tick_time = 0
        self.render_time_raw = 0
        
        self.FPSs = []
        self.FPS = self.config.FPS
        self.average_FPS = 0
        self.fps_idx = 0
        self.worst_fps = 0
        self.best_fps = 0
        
        self.TPSs = []
        self.TPS = self.config.TPS
        self.average_TPS = 0
        self.tps_idx = 0
        self.worst_tps = 0
        self.best_tps = 0
        
        self.dfs = []
        self.df_idx = 0
        self.average_df = 0
        self.delta_tick = 0
        self.worst_df = 0
        self.best_df = 0
        
        self.POLLING_RATEs = []
        self.POLLING_RATE = 0
        self.polling_idx = 0
        self.average_polling = 0
        self.worst_polling = 0
        self.best_polling = 0
        
        self.POLLING_TIMES = []
        self.POLLING_T = 0
        self.polling_t_idx = 0
        self.average_polling_t = 0
        self.worst_polling_t = 0
        self.best_polling_t = 0
        
        self.next_polling_time = 0
        
        self.start_times = {
            'handle_events': 0,
            'game_loop': 0,
            'get_debug_info': 0,
            'render_loop': 0
        }
        
        self.elapsed_times = {
            'handle_events': 0,
            'game_loop': 0,
            'get_debug_info': 0,
            'render_loop': 0
        }
        
        self.iter_times = {
            'handle_events': 1,
            'game_loop': 1,
            'get_debug_info': 1,
            'render_loop': 1
        }
        
    def __initialise(self, four):
        """
        Initalise the instance of the game
        
        args:
        (Four) four: the instance of the game
        """
        self.state_snapshot = four.forward_state()
        self.start_time = time.perf_counter()
        pygame.init()
        
    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_caption(self.config.CAPTION)
        return pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
    
    def __exit(self):
        """
        Exit the game
        """
        self.exited = True
        pygame.quit()
           
    async def run(self, four):
        """
        Run the game
    
        args:
        (Four) four: the instance of the game
        """
        self.__initialise(four)
        
        await asyncio.gather(
            self.__timing_wrapper("handle_events", self.__handle_events()),
            self.__timing_wrapper("game_loop", self.__game_loop(four)),
            self.__timing_wrapper("get_debug_info", self.__get_debug_info()),
            self.__timing_wrapper("render_loop", self.__render_loop()),
        )

    async def __timing_wrapper(self, name, coro):
        """
        Wrapper function to time coroutines of the game, 
        used to time the game loop, render loop and event handling loop
        
        args:
        (str) name: the name of the coroutine
        (coro) coro: the coroutine to time
        """
        
        self.start_times[name] = time.perf_counter()
        
        async def monitor():
            while True:
                
                iter_start = time.perf_counter()
                self.elapsed_times[name] = time.perf_counter() - self.start_times[name]
                self.iter_times[name] = time.perf_counter() - iter_start
                
                await asyncio.sleep(0) 
        
        monitor_task = asyncio.create_task(monitor())
        
        try:
            await coro
        finally:
            monitor_task.cancel()  

    async def __handle_events(self):
        """
        Handle pygame key events and pass them to the handling object, updates at an uncapped rate
        """
        while not self.exited:
                
                self.handling.current_time = self.elapsed_times["handle_events"]
                self.handling.delta_time += (self.handling.current_time - self.handling.last_tick_time) / self.handling.polling_tick_time
                self.handling.last_tick_time = self.handling.current_time
              
                if self.handling.do_first_tick:
                    self.__handle_key_events()
                    self.handling.do_first_tick = False

                while self.handling.delta_time >= 1:
                    self.__handle_key_events()
                    self.handling.delta_time -= 1
                
                if self.handling.current_time > self.handling.poll_counter_last_cleared + 1:
                    self.__get_polling_rate()
                    self.handling.poll_tick_counter = 0
                    self.handling.poll_counter_last_cleared += 1
            
                await asyncio.sleep(0)
    
    def __handle_key_events(self):
        self.handling.poll_tick_counter += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__exit()
                
            elif event.type == pygame.KEYDOWN:
                self.handling.on_key_press(event.key)
                
                if event.key == pygame.K_F3:
                    self.__show_debug_menu()
                    
                if event.key == pygame.K_ESCAPE:
                    self.__exit()
                
            elif event.type == pygame.KEYUP:
                self.handling.on_key_release(event.key)
    
    async def __game_loop(self, four):
        """
        The main game loop, updates at a fixed tick rate
        
        args:
        (Four) four: the instance of the game
        """
        while not self.exited:
         
            self.current_time = self.elapsed_times["game_loop"]
            self.delta_time += (self.current_time - self.last_tick_time) / self.time_per_tick
            self.last_tick_time = self.current_time
             
            if self.do_first_tick:
                self.__do_tick(four)
                self.do_first_tick = False
            
            while self.delta_time >= 1:
                self.__do_tick(four)
                self.delta_time -= 1
                
            if self.current_time > self.tick_counter_last_cleared + 1:
                self.__get_tps()
                self.tick_counter = 0
                self.tick_counter_last_cleared += 1
            
            await asyncio.sleep(0)

    async def __render_loop(self):
        """
        The main render loop, updates at a fixed or uncapped frame rate
        """
        while not self.exited:
            
            if self.config.UNCAPPED_FPS:
                
                self.__do_render()
                
            else:
                self.current_frame_time = self.elapsed_times["render_loop"]
                self.delta_frame_time += (self.current_frame_time - self.last_frame_time) / self.frame_time
                self.last_frame_time = self.current_frame_time
                
                if self.draw_first_frame:
                    self.__do_render()
                    self.draw_first_frame = False
                
                if self.delta_frame_time >= 1:
                    self.__do_render()
                    self.delta_frame_time -= 1
         
            self.__get_fps()
            
            await asyncio.sleep(0)
            
    def __do_tick(self, four):
        """
        Peform one tick of the game logic
        
        args:
        (Four) four: the instance of the game
        """
        self.delta_tick = self.__calc_df()
        four.loop(self.current_time, self.last_frame_time)
        self.state_snapshot = four.forward_state()
        self.tick_counter += 1
    
    def __do_render(self):
        """
        Render a single frame of the game
        """
        self.__get_key_dict()
        self.render.render_frame(self.state_snapshot, self.key_dict, self.debug_dict)
        self.render_clock.tick()
               
    def __exit(self):
        """
        Exit the game
        """
        self.exited = True
        pygame.quit()
        
    def __get_tps(self):
        """
        Update the stored TPS value
        """
        self.TPS = self.tick_counter
    
    def __get_fps(self):
        """
        Update the stored FPS value
        """
        self.FPS = self.render_clock.get_fps()
        
    def __get_polling_rate(self):
        """
        Update the stored polling rate value
        """
        self.POLLING_RATE = self.handling.poll_tick_counter

    def __calc_exe_time_avg(self):
        """
        For debug menu, calculate the average execution time of a tick
        """
        
        if self.exe_idx >= self.max_avg_len:
            self.exe_idx = 0
            
        if len(self.tick_times) >= self.max_avg_len:
            self.tick_times.pop(self.exe_idx)
             
        self.tick_times.append(self.iter_times["game_loop"])
            
        self.best_tick_time = min(self.tick_times)
        self.worst_tick_time = max(self.tick_times)
            
        self.exe_idx += 1   
        self.tick_time = sum(self.tick_times)/len(self.tick_times)
        
    def __calc_render_time_avg(self):
        """
        For debug menu, calculate the average time to render a frame
        """
        
        if self.r_idx >= self.max_avg_len:
            self.r_idx = 0
            
        if len(self.render_times) >= self.max_avg_len:
            self.render_times.pop(self.r_idx)
            
        self.render_times.append(self.iter_times["render_loop"])
            
        self.best_render_time = min(self.render_times)
        self.worst_render_time = max(self.render_times)
        
        self.r_idx += 1
        self.render_time_avg =  sum(self.render_times)/len(self.render_times)
        
    def __calc_average_TPS(self):
        """
        For debug menu, calculate the average TPS
        """
        
        if self.TPS == float('inf') or self.TPS == float('-inf'):
            self.TPS = 0

        if self.tps_idx >= self.max_avg_len:
            self.tps_idx = 0
            
        if len(self.TPSs) >= self.max_avg_len:
            self.TPSs.pop(self.tps_idx)
                
        self.TPSs.append(self.TPS)
        
        self.tps_idx += 1
    
        self.worst_tps = min(self.TPSs)
        self.best_tps = max(self.TPSs)
        
        self.average_TPS = sum(self.TPSs) / len(self.TPSs)
        
    def __calc_average_FPS(self):
        """
        For debug menu, calculate the average FPS
        """
    
        if self.fps_idx >= self.max_avg_len:
            self.fps_idx = 0
            
        if len(self.FPSs) >= self.max_avg_len:
            self.FPSs.pop(self.fps_idx)
                        
        self.FPSs.append(self.FPS)
        
        self.fps_idx += 1
        self.average_FPS = sum(self.FPSs)/len(self.FPSs)
    
        self.worst_fps = min(self.FPSs)
        self.best_fps = max(self.FPSs)
        
    def __calc_df(self):
        """
        For debug menu, calculate the delta frame time, how many frames behind or ahead the game is to the desired TPS
        """
        if self.TPS == float('inf') or self.TPS == float('-inf'):
            self.TPS = 0
        
        self.delta_tick = int(self.config.TPS - self.TPS)
        
        if self.df_idx >= self.max_avg_len - 1:
            self.df_idx = 0
            
        if len(self.dfs) >= self.max_avg_len - 1:
            self.dfs.pop(self.df_idx)
            
        self.dfs.append(self.delta_tick)
        self.average_df = sum(self.dfs)/len(self.dfs)
        
        self.worst_df = max(self.dfs)
        self.best_df = min(self.dfs)
        
        self.df_idx += 1
        
    def __calc_average_polling(self):
        """
        For debug menu, calculate the average polling rate
        """
        if self.polling_idx >= self.max_avg_len:
            self.polling_idx = 0
            
        if len(self.POLLING_RATEs) >= self.max_avg_len:
            self.POLLING_RATEs.pop(self.polling_idx)
            
        self.POLLING_RATEs.append(self.POLLING_RATE)
        
        self.polling_idx += 1
        self.average_polling = sum(self.POLLING_RATEs)/len(self.POLLING_RATEs)
        
        self.worst_polling = min(self.POLLING_RATEs)
        self.best_polling = max(self.POLLING_RATEs)
    
    def __calc_average_polling_t(self):
        """
        For debug menu, calculate the average polling time
        """
        if self.polling_t_idx >= self.max_avg_len:
            self.polling_t_idx = 0
            
        if len(self.POLLING_TIMES) >= self.max_avg_len:
            self.POLLING_TIMES.pop(self.polling_t_idx)
            
        self.POLLING_TIMES.append(self.iter_times["handle_events"])
        
        self.polling_t_idx += 1
        self.average_polling_t = sum(self.POLLING_TIMES)/len(self.POLLING_TIMES)
        
        self.worst_polling_t = max(self.POLLING_TIMES)
        self.best_polling_t = min(self.POLLING_TIMES)
    
    def __show_debug_menu(self):
        """
        Show the debug menu
        """
        self.DEBUG = not self.DEBUG
    
    async def __get_debug_info(self):
        """
        Fetch the debug information for the debug menu
        """
        while not self.exited:
            if self.DEBUG:
                    self.__calc_average_FPS()
                    self.__calc_render_time_avg()
                    
                    self.__calc_average_TPS()
                    self.__calc_exe_time_avg()
                    
                    self.__calc_average_polling()
                    self.__calc_average_polling_t()
                    
                    self.debug_dict = {
                        # fps debug
                        'FPS': self.average_FPS,
                        'FPS_RAW': self.FPS,
                        'BEST_FPS': self.best_fps,
                        'WORST_FPS': self.worst_fps,
                        
                        # render time debug
                        'REN_T': self.render_time_avg,
                        'REN_T_RAW': self.iter_times["render_loop"],
                        'BEST_REN_T': self.best_render_time,
                        'WORST_REN_T': self.worst_render_time,
                        
                        # tps debug
                        'TPS': self.average_TPS,
                        'TPS_RAW': self.TPS,
                        'BEST_TPS': self.best_tps,
                        'WORST_TPS': self.worst_tps,
                        
                        # tick time debug
                        'SIM_T': self.tick_time,
                        'SIM_T_RAW': self.iter_times["game_loop"],
                        'BEST_SIM_T': self.best_tick_time,
                        'WORST_SIM_T': self.worst_tick_time,
                        
                        # delta frame debug
                        'DF': self.average_df,
                        'DF_RAW': self.delta_tick,
                        'BEST_DF': self.best_df,
                        'WORST_DF': self.worst_df,
                        
                        # tick counter
                        'TICKCOUNT': self.tick_counter,

                        'POLLING_RATE': self.average_polling,
                        'POLLING_RATE_RAW': self.POLLING_RATE,
                        'BEST_POLLING_RATE': self.best_polling,
                        'WORST_POLLING_RATE': self.worst_polling,
                        
                        'POLLING_T': self.average_polling_t,
                        'POLLING_T_RAW': self.iter_times["handle_events"],
                        'BEST_POLLING_T': self.best_polling_t,
                        'WORST_POLLING_T': self.worst_polling_t,
                        
                        'DAS_COUNTER': self.handling.DAS_counter,
                        'DAS': self.handling.handling_settings['DAS'],
                        
                        'ARR_COUNTER': self.handling.ARR_counter,
                        'ARR': self.handling.handling_settings['ARR'],
                        
                        'DCD': self.handling.handling_settings['DCD'],
                        'SDF': self.handling.handling_settings['SDF'],
                        
                        'DAS_CANCEL': self.handling.handling_settings['DASCancel'],
                        'PREVHD': self.handling.handling_settings['PrevAccHD'],
                        'PREFSD': self.handling.handling_settings['PrefSD'],
                    }
            else:
                self.debug_dict = None
        
            await asyncio.sleep(0)
        
    def __get_key_dict(self):
        self.key_dict = {
            'KEY_LEFT': self.handling.key_states[self.handling.key_bindings[Action.MOVE_LEFT]]['current'],
            'KEY_RIGHT': self.handling.key_states[self.handling.key_bindings[Action.MOVE_RIGHT]]['current'],
            'KEY_CLOCKWISE': self.handling.key_states[self.handling.key_bindings[Action.ROTATE_CLOCKWISE]]['current'],
            'KEY_COUNTERCLOCKWISE': self.handling.key_states[self.handling.key_bindings[Action.ROTATE_COUNTERCLOCKWISE]]['current'],
            'KEY_180': self.handling.key_states[self.handling.key_bindings[Action.ROTATE_180]]['current'],
            'KEY_HARD_DROP' : self.handling.key_states[self.handling.key_bindings[Action.HARD_DROP]]['current'],
            'KEY_SOFT_DROP': self.handling.key_states[self.handling.key_bindings[Action.SOFT_DROP]]['current'],
            'KEY_HOLD': self.handling.key_states[self.handling.key_bindings[Action.HOLD]]['current'],
        }
class Clock:
    def __init__(self, max_entries = 10):
        """
        Custom clock object as pygames inbuilt clock is trash for timing microsecond processes (has a resolution of 10ms????)
        Instead use clock with highest resolution possible (time.perf_counter) and calculate the FPS from the average time between ticks
        (literally a copy of pygame.time.Clock but with time.perf_counter)
        
        args:
        (int) max_entries: the maximum number of entries to store in the clock
        """
        self.max_entries = max_entries
        self.times = deque(maxlen = max_entries)
        self.last_time = time.perf_counter()
        self.fps = 0
        self.dt = 0

    def tick(self):
        """
        Tick the clock once, and calculate the average time between ticks to calculate the FPS
        """
        current_time = time.perf_counter()
        self.dt = current_time - self.last_time
        self.last_time = current_time
        self.times.append(self.dt)
        
        if len(self.times) > 1:
            average_time = sum(self.times) / len(self.times)
            self.fps = 1 / average_time
        else:
            self.fps = 0  
    
    def get_fps(self):
        """
        Return the FPS of the clock
        """
        return self.fps    
    
    def get_time(self):
        return time.perf_counter()
    
    def get_dt(self):
        """
        Return the delta time of the clock
        """
        return self.dt