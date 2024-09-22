import pygame
from config import StructConfig
from core.handling import Handling
from render.render import Render
import time
import asyncio
from collections import deque 
from core.handling import Action
from core.state.struct_debug import StructDebug
from core.state.struct_timing import StructTiming
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_flags import StructFlags
from core.state.struct_handling import StructHandling
from core.state.struct_render import StructRender

class Core():
    def __init__(self):
        """
        Manage the game loop, key events, and rendering of the game
        
        methods:
            run(four): Run the instance of four
        """
        self.Config = StructConfig()
        self.StructTiming = StructTiming()
        self.GameInstanceStruct = StructGameInstance()
        self.HandlingStruct = StructHandling()
        self.FlagStruct = StructFlags()
        self.RenderStruct = StructRender()
        self.StructDebug = StructDebug()
        
        self.render_clock = Clock()
        self.window = self.__init_window()
        self.render = Render(self.window, self.Config, self.RenderStruct, self.FlagStruct, self.GameInstanceStruct)
        self.handling = Handling(self.Config, self.HandlingStruct)
        
        self.TPS = self.Config.TPS
        self.FPS = self.Config.FPS
        
        self.exited = False
        self.state_snapshot = None
        
        self.key_dict = None
        
    def __initialise(self, four):
        """
        Initalise the instance of the game
        
        args:
        (Four) four: the instance of the game
        """
        self.start_time = time.perf_counter()
        pygame.init()
        
    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_caption(self.Config.CAPTION)
        return pygame.display.set_mode((self.Config.WINDOW_WIDTH, self.Config.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
    
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
        
        self.StructTiming.start_times[name] = time.perf_counter()
        
        async def monitor():
            while True:
                
                iter_start = time.perf_counter()
                self.StructTiming.elapsed_times[name] = time.perf_counter() - self.StructTiming.start_times[name]
                self.StructTiming.iter_times[name] = time.perf_counter() - iter_start
                
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
                
                self.HandlingStruct.current_time = self.StructTiming.elapsed_times["handle_events"]
                self.HandlingStruct.delta_time += (self.handling.HandlingStruct.current_time - self.handling.HandlingStruct.last_tick_time) / self.handling.polling_tick_time
                self.HandlingStruct.last_tick_time = self.handling.HandlingStruct.current_time
              
                if self.HandlingStruct.do_first_tick:
                    self.__handle_key_events()
                    self.HandlingStruct.do_first_tick = False

                while self.HandlingStruct.delta_time >= 1:
                    self.__handle_key_events()
                    self.HandlingStruct.delta_time -= 1
                
                if self.HandlingStruct.current_time > self.HandlingStruct.poll_counter_last_cleared + 1:
                    self.__get_polling_rate()
                    self.HandlingStruct.poll_tick_counter = 0
                    self.HandlingStruct.poll_counter_last_cleared += 1
            
                await asyncio.sleep(0)
    
    def __handle_key_events(self):
        self.HandlingStruct.poll_tick_counter += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__exit()
                
            elif event.type == pygame.KEYDOWN:
                self.handling.on_key_press(event.key)
                
                if event.key == pygame.K_F3:
                    self.__show_debug_menu()
                
                if event.key == pygame.K_F4:
                    self.RenderStruct.draw_bounding_box = not self.RenderStruct.draw_bounding_box
                if event.key == pygame.K_F5:
                    self.RenderStruct.draw_origin = not self.RenderStruct.draw_origin
                if event.key == pygame.K_F6:
                    self.RenderStruct.draw_pivot = not self.RenderStruct.draw_pivot
                    
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
         
            self.StructTiming.current_time = self.StructTiming.elapsed_times["game_loop"]
            self.StructTiming.delta_time += (self.StructTiming.current_time - self.StructTiming.last_tick_time) / self.StructTiming.time_per_tick
            self.StructTiming.last_tick_time = self.StructTiming.current_time
             
            if self.StructTiming.do_first_tick:
                self.__do_tick(four)
                self.StructTiming.do_first_tick = False
            
            while self.StructTiming.delta_time >= 1:
                self.__do_tick(four)
                self.StructTiming.delta_time -= 1
                
            if self.StructTiming.current_time > self.StructTiming.tick_counter_last_cleared + 1:
                self.__get_tps()
                self.StructTiming.tick_counter = 0
                self.StructTiming.tick_counter_last_cleared += 1
            
            await asyncio.sleep(0)

    async def __render_loop(self):
        """
        The main render loop, updates at a fixed or uncapped frame rate
        """
        while not self.exited:
            
            if self.Config.UNCAPPED_FPS:
                
                self.__do_render()
                
            else:
                self.StructTiming.current_frame_time = self.StructTiming.elapsed_times["render_loop"]
                self.StructTiming.delta_frame_time += (self.StructTiming.current_frame_time - self.StructTiming.last_frame_time) / self.StructTiming.frame_time
                self.StructTiming.last_frame_time = self.StructTiming.current_frame_time
                
                if self.StructTiming.draw_first_frame:
                    self.__do_render()
                    self.StructTiming.draw_first_frame = False
                
                if self.StructTiming.delta_frame_time >= 1:
                    self.__do_render()
                    self.StructTiming.delta_frame_time -= 1
         
            self.__get_fps()
            
            await asyncio.sleep(0)
            
    def __do_tick(self, four):
        """
        Peform one tick of the game logic
        
        args:
        (Four) four: the instance of the game
        """
        self.StructDebug.delta_tick = self.__calc_df()
        four.loop()
        self.StructTiming.tick_counter += 1
    
    def __do_render(self):
        """
        Render a single frame of the game
        """
        self.__get_key_dict()
        self.render.render_frame(self.key_dict, self.StructDebug.debug_dict)
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
        self.TPS = self.StructTiming.tick_counter
    
    def __get_fps(self):
        """
        Update the stored FPS value
        """
        self.StructDebug.FPS = self.render_clock.get_fps()
        
    def __get_polling_rate(self):
        """
        Update the stored polling rate value
        """
        self.StructDebug.POLLING_RATE = self.handling.HandlingStruct.poll_tick_counter

    def __calc_exe_time_avg(self):
        """
        For debug menu, calculate the average execution time of a tick
        """
        
        if self.StructDebug.exe_idx >= self.StructDebug.max_avg_len:
            self.StructDebug.exe_idx = 0
            
        if len(self.StructDebug.tick_times) >= self.StructDebug.max_avg_len:
            self.StructDebug.tick_times.pop(self.StructDebug.exe_idx)
             
        self.StructDebug.tick_times.append(self.StructTiming.iter_times["game_loop"])
            
        self.StructDebug.best_tick_time = min(self.StructDebug.tick_times)
        self.StructDebug.worst_tick_time = max(self.StructDebug.tick_times)
            
        self.StructDebug.exe_idx += 1   
        self.StructDebug.tick_time = sum(self.StructDebug.tick_times)/len(self.StructDebug.tick_times)
        
    def __calc_render_time_avg(self):
        """
        For debug menu, calculate the average time to render a frame
        """
        
        if self.StructDebug.r_idx >= self.StructDebug.max_avg_len:
            self.StructDebug.r_idx = 0
            
        if len(self.StructDebug.render_times) >= self.StructDebug.max_avg_len:
            self.StructDebug.render_times.pop(self.StructDebug.r_idx)
            
        self.StructDebug.render_times.append(self.StructTiming.iter_times["render_loop"])
            
        self.StructDebug.best_render_time = min(self.StructDebug.render_times)
        self.StructDebug.worst_render_time = max(self.StructDebug.render_times)
        
        self.StructDebug.r_idx += 1
        self.render_time_avg =  sum(self.StructDebug.render_times)/len(self.StructDebug.render_times)
        
    def __calc_average_TPS(self):
        """
        For debug menu, calculate the average TPS
        """
        
        if self.TPS == float('inf') or self.TPS == float('-inf'):
            self.TPS = 0

        if self.StructDebug.tps_idx >= self.StructDebug.max_avg_len:
            self.StructDebug.tps_idx = 0
            
        if len(self.StructDebug.TPSs) >= self.StructDebug.max_avg_len:
            self.StructDebug.TPSs.pop(self.StructDebug.tps_idx)
                
        self.StructDebug.TPSs.append(self.TPS)
        
        self.StructDebug.tps_idx += 1
    
        self.StructDebug.worst_tps = min(self.StructDebug.TPSs)
        self.StructDebug.best_tps = max(self.StructDebug.TPSs)
        
        self.StructDebug.average_TPS = sum(self.StructDebug.TPSs) / len(self.StructDebug.TPSs)
        
    def __calc_average_FPS(self):
        """
        For debug menu, calculate the average FPS
        """
    
        if self.StructDebug.fps_idx >= self.StructDebug.max_avg_len:
            self.StructDebug.fps_idx = 0
            
        if len(self.StructDebug.FPSs) >= self.StructDebug.max_avg_len:
            self.StructDebug.FPSs.pop(self.StructDebug.fps_idx)
                        
        self.StructDebug.FPSs.append(self.FPS)
        
        self.StructDebug.fps_idx += 1
        self.StructDebug.average_FPS = sum(self.StructDebug.FPSs)/len(self.StructDebug.FPSs)
    
        self.StructDebug.worst_fps = min(self.StructDebug.FPSs)
        self.StructDebug.best_fps = max(self.StructDebug.FPSs)
        
    def __calc_df(self):
        """
        For debug menu, calculate the delta frame time, how many frames behind or ahead the game is to the desired TPS
        """
        if self.TPS == float('inf') or self.TPS == float('-inf'):
            self.TPS = 0
        
        self.StructDebug.delta_tick = int(self.Config.TPS - self.TPS)
        
        if self.StructDebug.df_idx >= self.StructDebug.max_avg_len - 1:
            self.StructDebug.df_idx = 0
            
        if len(self.StructDebug.dfs) >= self.StructDebug.max_avg_len - 1:
            self.StructDebug.dfs.pop(self.StructDebug.df_idx)
            
        self.StructDebug.dfs.append(self.StructDebug.delta_tick)
        self.StructDebug.average_df = sum(self.StructDebug.dfs)/len(self.StructDebug.dfs)
        
        self.StructDebug.worst_df = max(self.StructDebug.dfs)
        self.StructDebug.best_df = min(self.StructDebug.dfs)
        
        self.StructDebug.df_idx += 1
        
    def __calc_average_polling(self):
        """
        For debug menu, calculate the average polling rate
        """
        if self.StructDebug.polling_idx >= self.StructDebug.max_avg_len:
            self.StructDebug.polling_idx = 0
            
        if len(self.StructDebug.POLLING_RATEs) >= self.StructDebug.max_avg_len:
            self.StructDebug.POLLING_RATEs.pop(self.StructDebug.polling_idx)
            
        self.StructDebug.POLLING_RATEs.append(self.StructDebug.POLLING_RATE)
        
        self.StructDebug.polling_idx += 1
        self.StructDebug.average_polling = sum(self.StructDebug.POLLING_RATEs)/len(self.StructDebug.POLLING_RATEs)
        
        self.StructDebug.worst_polling = min(self.StructDebug.POLLING_RATEs)
        self.StructDebug.best_polling = max(self.StructDebug.POLLING_RATEs)
    
    def __calc_average_polling_t(self):
        """
        For debug menu, calculate the average polling time
        """
        if self.StructDebug.polling_t_idx >= self.StructDebug.max_avg_len:
            self.StructDebug.polling_t_idx = 0
            
        if len(self.StructDebug.POLLING_TIMES) >= self.StructDebug.max_avg_len:
            self.StructDebug.POLLING_TIMES.pop(self.StructDebug.polling_t_idx)
            
        self.StructDebug.POLLING_TIMES.append(self.StructTiming.iter_times["handle_events"])
        
        self.StructDebug.polling_t_idx += 1
        self.StructDebug.average_polling_t = sum(self.StructDebug.POLLING_TIMES)/len(self.StructDebug.POLLING_TIMES)
        
        self.StructDebug.worst_polling_t = max(self.StructDebug.POLLING_TIMES)
        self.StructDebug.best_polling_t = min(self.StructDebug.POLLING_TIMES)
    
    def __show_debug_menu(self):
        """
        Show the debug menu
        """
        self.StructDebug.DEBUG = not self.StructDebug.DEBUG
    
    async def __get_debug_info(self):
        """
        Fetch the debug information for the debug menu
        """
        while not self.exited:
            if self.StructDebug.DEBUG:
                    self.__calc_average_FPS()
                    self.__calc_render_time_avg()
                    
                    self.__calc_average_TPS()
                    self.__calc_exe_time_avg()
                    
                    self.__calc_average_polling()
                    self.__calc_average_polling_t()
                    
                    self.StructDebug.debug_dict = {
                        # fps debug
                        'FPS': self.StructDebug.average_FPS,
                        'FPS_RAW': self.FPS,
                        'BEST_FPS': self.StructDebug.best_fps,
                        'WORST_FPS': self.StructDebug.worst_fps,
                        
                        # render time debug
                        'REN_T': self.render_time_avg,
                        'REN_T_RAW': self.StructTiming.iter_times["render_loop"],
                        'BEST_REN_T': self.StructDebug.best_render_time,
                        'WORST_REN_T': self.StructDebug.worst_render_time,
                        
                        # tps debug
                        'TPS': self.StructDebug.average_TPS,
                        'TPS_RAW': self.TPS,
                        'BEST_TPS': self.StructDebug.best_tps,
                        'WORST_TPS': self.StructDebug.worst_tps,
                        
                        # tick time debug
                        'SIM_T': self.StructDebug.tick_time,
                        'SIM_T_RAW': self.StructTiming.iter_times["game_loop"],
                        'BEST_SIM_T': self.StructDebug.best_tick_time,
                        'WORST_SIM_T': self.StructDebug.worst_tick_time,
                        
                        # delta frame debug
                        'DF': self.StructDebug.average_df,
                        'DF_RAW': self.StructDebug.delta_tick,
                        'BEST_DF': self.StructDebug.best_df,
                        'WORST_DF': self.StructDebug.worst_df,
                        
                        # tick counter
                        'TICKCOUNT': self.StructTiming.tick_counter,

                        'POLLING_RATE': self.StructDebug.average_polling,
                        'POLLING_RATE_RAW': self.StructDebug.POLLING_RATE,
                        'BEST_POLLING_RATE': self.StructDebug.best_polling,
                        'WORST_POLLING_RATE': self.StructDebug.worst_polling,
                        
                        'POLLING_T': self.StructDebug.average_polling_t,
                        'POLLING_T_RAW': self.StructTiming.iter_times["handle_events"],
                        'BEST_POLLING_T': self.StructDebug.best_polling_t,
                        'WORST_POLLING_T': self.StructDebug.worst_polling_t,
                        
                        'DAS_COUNTER': self.handling.HandlingStruct.DAS_counter,
                        'DAS': self.handling.Config.HANDLING_SETTINGS['DAS'],
                        
                        'ARR_COUNTER': self.handling.HandlingStruct.ARR_counter,
                        'ARR': self.handling.Config.HANDLING_SETTINGS['ARR'],
                        
                        'DCD': self.handling.Config.HANDLING_SETTINGS['DCD'],
                        'SDF': self.handling.Config.HANDLING_SETTINGS['SDF'],
                        
                        'DAS_CANCEL': self.handling.Config.HANDLING_SETTINGS['DASCancel'],
                        'PREVHD': self.handling.Config.HANDLING_SETTINGS['PrevAccHD'],
                        'PREFSD': self.handling.Config.HANDLING_SETTINGS['PrefSD'],
                        
                        'GRAVITY': self.GameInstanceStruct.gravity,
                        'GRAV_COUNTER': self.GameInstanceStruct.gravity_counter,
                        'G_IN_TICKS': self.GameInstanceStruct.G_units_in_ticks,
                        'ON_FLOOR': self.GameInstanceStruct.on_floor,
                        'G_MULTI': self.GameInstanceStruct.soft_drop_factor,
                        'LOCK_DELAY': self.GameInstanceStruct.lock_delay,
                        'LOCK_DELAY_COUNTER': self.GameInstanceStruct.lock_delay_counter,
                        'LOCK_DELAY_TICKS': self.GameInstanceStruct.lock_delay_in_ticks,
                        'MAX_MOVES': self.GameInstanceStruct.max_moves_before_lock,
                    }
            else:
                self.StructDebug.debug_dict = None
        
            await asyncio.sleep(0)
        
    def __get_key_dict(self):
        self.key_dict = {
            'KEY_LEFT': self.handling.key_states[self.handling.Config.key_bindings[Action.MOVE_LEFT]]['current'],
            'KEY_RIGHT': self.handling.key_states[self.handling.Config.key_bindings[Action.MOVE_RIGHT]]['current'],
            'KEY_CLOCKWISE': self.handling.key_states[self.handling.Config.key_bindings[Action.ROTATE_CLOCKWISE]]['current'],
            'KEY_COUNTERCLOCKWISE': self.handling.key_states[self.handling.Config.key_bindings[Action.ROTATE_COUNTERCLOCKWISE]]['current'],
            'KEY_180': self.handling.key_states[self.handling.Config.key_bindings[Action.ROTATE_180]]['current'],
            'KEY_HARD_DROP' : self.handling.key_states[self.handling.Config.key_bindings[Action.HARD_DROP]]['current'],
            'KEY_SOFT_DROP': self.handling.key_states[self.handling.Config.key_bindings[Action.SOFT_DROP]]['current'],
            'KEY_HOLD': self.handling.key_states[self.handling.Config.key_bindings[Action.HOLD]]['current'],
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