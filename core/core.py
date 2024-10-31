import pygame
from config import StructConfig
from core.handling import Handling
from core.debug import Debug
from render.render import Render
import time
import asyncio
from collections import deque 
from core.state.struct_debug import StructDebug
from core.state.struct_timing import StructTiming
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_flags import StructFlags, set_flag_attr
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
        self.TimingStruct = StructTiming()
        self.GameInstanceStruct = StructGameInstance()
        self.HandlingStruct = StructHandling()
        self.FlagStruct = StructFlags()
        self.RenderStruct = StructRender()
        self.DebugStruct = StructDebug()
        
        self.render_clock = Clock()
        
        self.Debug = Debug(self.Config, self.TimingStruct, self.HandlingStruct, self.GameInstanceStruct, self.FlagStruct, self.RenderStruct, self.DebugStruct)
        self.handling = Handling(self.Config, self.HandlingStruct)
          
        self.TPS = self.Config.TPS
        self.FPS = self.Config.FPS
        self.time_per_tick = 1 / self.Config.TPS
        self.frame_time = 1 / self.Config.FPS
        
        self.exited = False
         
    def __initialise(self):
        """
        Initalise the instance of the game
        
        args:
        (Four) four: the instance of the game
        """
        set_flag_attr() # set the flag attributes
        self.render = Render(self.Config, self.RenderStruct, self.FlagStruct, self.GameInstanceStruct, self.TimingStruct, self.DebugStruct)
        self.start_time = time.perf_counter()
        pygame.init()
        
    def __exit(self):
        """
        Exit the game
        """
        self.exited = True
        pygame.quit()
    
    # =========================================== CORE PROCESSES ===========================================
    
    async def run(self, four):
        """
        Run the game
    
        args:
        (Four) four: the instance of the game
        """
        self.__initialise()
        
        await asyncio.gather(
            self.__timing_wrapper("handle_events", self.__handling_loop()),
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
        
        self.TimingStruct.start_times[name] = time.perf_counter()
        
        async def monitor():
            pass
            await asyncio.sleep(0) 
        
        monitor_task = asyncio.create_task(monitor())
        
        try:
            await coro
        finally:
            monitor_task.cancel()  
            
    # ------------------------------------------- HANDLING LOOP -------------------------------------------
    
    async def __handling_loop(self):
        """
        Handle pygame key events and pass them to the handling object
        """
        while not self.exited:
                
                self.HandlingStruct.current_time = time.perf_counter() - self.TimingStruct.start_times["handle_events"] 
                self.TimingStruct.elapsed_times["handle_events"] = self.HandlingStruct.current_time
                
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
        """
        Handle pygame key events
        """
        iter_start = time.perf_counter()
        
        self.HandlingStruct.poll_tick_counter += 1
        self.handling.get_key_dict()
        
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
        
        iter_end = time.perf_counter()
        self.TimingStruct.iter_times["handle_events"] = iter_end - iter_start
    
    # ------------------------------------------- GAME LOOP -------------------------------------------
    
    async def __game_loop(self, four):
        """
        The main game loop, updates at a fixed tick rate
        
        args:
        (Four) four: the instance of the game
        """
        while not self.exited:
         
            self.TimingStruct.current_time = time.perf_counter() - self.TimingStruct.start_times["game_loop"]
            self.TimingStruct.elapsed_times["game_loop"] = self.TimingStruct.current_time
            
            self.TimingStruct.delta_time += (self.TimingStruct.current_time - self.TimingStruct.last_tick_time) / self.time_per_tick
            self.TimingStruct.last_tick_time = self.TimingStruct.current_time
             
            if self.TimingStruct.do_first_tick:
                self.__do_tick(four)
                self.TimingStruct.do_first_tick = False
            
            while self.TimingStruct.delta_time >= 1:
                self.__do_tick(four)
                self.TimingStruct.delta_time -= 1
                
            if self.TimingStruct.current_time > self.TimingStruct.tick_counter_last_cleared + 1:
                self.__get_tps()
                self.TimingStruct.tick_counter = 0
                self.TimingStruct.tick_counter_last_cleared += 1
            
            await asyncio.sleep(0)
            
    def __do_tick(self, four):
        """
        Peform one tick of the game logic
        
        args:
        (Four) four: the instance of the game
        """
        iter_start = time.perf_counter()
        
        four.loop()
        self.TimingStruct.tick_counter += 1
        
        iter_end = time.perf_counter()
        self.TimingStruct.iter_times["game_loop"] = iter_end - iter_start
    
    # ------------------------------------------- RENDER LOOP -------------------------------------------
       
    async def __render_loop(self):
        """
        The main render loop, updates at a fixed or uncapped frame rate
        """
        while not self.exited:
            
            if self.Config.UNCAPPED_FPS:
                
                self.TimingStruct.current_frame_time = time.perf_counter() - self.TimingStruct.start_times["render_loop"]
                self.TimingStruct.elapsed_times["render_loop"] = self.TimingStruct.current_frame_time
                
                self.TimingStruct.delta_frame_time = (self.TimingStruct.current_frame_time - self.TimingStruct.last_frame_time) / self.frame_time
                self.TimingStruct.last_frame_time = self.TimingStruct.current_frame_time
                
                self.__do_render()
                
            else:
                self.TimingStruct.current_frame_time = time.perf_counter() - self.TimingStruct.start_times["render_loop"]
                self.TimingStruct.elapsed_times["render_loop"] = self.TimingStruct.current_frame_time
                
                self.TimingStruct.delta_frame_time += (self.TimingStruct.current_frame_time - self.TimingStruct.last_frame_time) / self.frame_time
                self.TimingStruct.last_frame_time = self.TimingStruct.current_frame_time
                
                if self.TimingStruct.draw_first_frame:
                    self.__do_render()
                    self.TimingStruct.draw_first_frame = False
                
                if self.TimingStruct.delta_frame_time >= 1:
                    self.__do_render()
                    self.TimingStruct.delta_frame_time -= 1
         
            self.__get_fps()
            
            await asyncio.sleep(0)
    
    def __do_render(self):
        """
        Render a single frame of the game
        """
        iter_start = time.perf_counter()
        
        self.RenderStruct.key_dict = self.HandlingStruct.key_dict
        self.render.draw_frame()
        self.render_clock.tick()
        
        iter_end = time.perf_counter()
        self.TimingStruct.iter_times["render_loop"] = iter_end - iter_start
     
    def __get_tps(self):
        """
        Update the stored TPS value
        """
        self.TPS = self.TimingStruct.tick_counter
        self.TimingStruct.TPS = self.TPS
    
    def __get_fps(self):
        """
        Update the stored FPS value
        """
        self.DebugStruct.FPS = self.render_clock.get_fps()
        self.TimingStruct.FPS = self.DebugStruct.FPS
        
    def __get_polling_rate(self):
        """
        Update the stored polling rate value
        """
        self.DebugStruct.POLLING_RATE = self.handling.HandlingStruct.poll_tick_counter
    
    # =========================================== DEBUG INFO =========================================== 
     
    def __show_debug_menu(self):
        """
        Show the debug menu
        """
        self.FlagStruct.SHOW_DEBUG_MENU = not self.FlagStruct.SHOW_DEBUG_MENU
    
    async def __get_debug_info(self):
        """
        Fetch the debug information for the debug menu
        """
        while not self.exited:
            if self.FlagStruct.SHOW_DEBUG_MENU:
                self.Debug.get_metrics()
            await asyncio.sleep(0)
        
class Clock:
    def __init__(self, max_entries = 10):
        """
        Custom clock object for timing microsecond processes that can calculate the FPS from the average time between ticks
        (literally a copy of pygame.time.Clock but with time.perf_counter)
        
        args:
        (int) max_entries: the maximum number of entries to store in the clock to be used when averaging
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