import threading
from config import StructConfig
from input.handling.handling import Handling
import time
from input.handling.handling_config import HandlingConfig
from core.state.struct_debug import StructDebug
from core.state.struct_timing import StructTiming
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_flags import StructFlags, set_flag_attr
from core.state.struct_handling import StructHandling
from core.state.struct_render import StructRender
from instance.four import Four
from core.clock import Clock
import pygame
import queue
from dataclasses import dataclass, field
from typing import Dict
import os
from render.render_new import Render
from input_manager import InputManager
from game_instance_manager import GameInstanceManager

# render loop will do frame based updates, so drawing & ui logic
# input loop will do polling based updates, so getting inputs & ticking input handlers of game instances
# main loop will do game logic updates, so ticking game instances

#TODO: change renderer methods to NOT use methods ASSOCIATED WITH A GAME INSTANCE
#      change game instance to UPDATE variables, i.e, current_tetromino is on floor etc which are contained in GameInstanceStruct
#      GameInstanceStruct will have to be contained in a Queue or something so that the renderer can access it in a thread safe way
#      Debug Menu will have to be changed in a similar way but ALSO, there will have to be per game instance debug info

class App():
    def __init__(self):
        
        self.is_focused = False
        self.PRINT_WARNINGS = True
        
        self.game_instances = []
        self.key_states_queue = queue.Queue() 

        self.Config = StructConfig()    
        self.Timing = Timing()
        self.FrameClock = Clock()
        
        self.RenderStruct = StructRender()
        self.DebugStruct = StructDebug()
        self.HandlingConfig = HandlingConfig()
        
        self.__init_pygame()
        self.__register_event_handlers()
            
        self.InputManager = InputManager(self.key_states_queue, self.Timing, self.PRINT_WARNINGS)
        self.GameInstanceManager = GameInstanceManager(self.Timing, self.PRINT_WARNINGS)
        self.Render = Render(self.Config, self.Timing, self.DebugStruct, self.game_instances)
        self.Debug = Debug(self.Config, self.Timing, self.RenderStruct, self.DebugStruct)
        
        self.GameParameters = { # temp, will be pased to game instance upon creation. This dict will be created by the menu manager
            'MATRIX_WIDTH': 10,
            'MATRIX_HEIGHT': 20,
            'ROTATION_SYSTEM': 'SRS',
            'RANDOMISER': '7BAG',
            'QUEUE_PREVIEWS': 5,
            'SEED': 0,
            'HOLD_ENABLED': True,
            'ALLOWED_SPINS': 'ALL-MINI',
            'LOCK_OUT_OK': True,
            'TOP_OUT_OK': False,
            'RESET_ON_TOP_OUT': False
        }
               
    def __initalise(self):
        set_flag_attr()
        
        self.input_thread = threading.Thread(target = self.InputManager.input_loop)
        self.logic_thread = threading.Thread(target = self.GameInstanceManager.logic_loop)
        
        self.Timing.start_times['input_loop'] = time.perf_counter()
        self.Timing.start_times['logic_loop'] = time.perf_counter()
        self.Timing.start_times['render_loop'] = time.perf_counter()
    
    def __register_event_handlers(self):
        EventHandler.register(pygame.WINDOWCLOSE)(self.__exit)
       
        EventHandler.register(pygame.WINDOWFOCUSLOST)(self.__is_focused)
        EventHandler.register(pygame.WINDOWFOCUSGAINED)(self.__is_focused)
        EventHandler.register(pygame.VIDEOEXPOSE)(self.__is_focused)
        EventHandler.register(pygame.WINDOWMINIMIZED)(self.__is_focused)
    
    def __init_pygame(self):
        pygame.init()
        pygame.font.init()
        
        pygame.event.set_allowed([
            pygame.QUIT,
            pygame.ACTIVEEVENT,
            pygame.VIDEORESIZE,
            pygame.VIDEOEXPOSE,
            pygame.WINDOWCLOSE,
            pygame.WINDOWMAXIMIZED,
            pygame.WINDOWMINIMIZED,
            pygame.WINDOWRESIZED,
            pygame.WINDOWRESTORED,
            pygame.WINDOWENTER,
            pygame.WINDOWLEAVE,
            pygame.WINDOWSHOWN,
            pygame.WINDOWHIDDEN,
            pygame.WINDOWFOCUSLOST,
            pygame.WINDOWFOCUSGAINED,
            pygame.CLIPBOARDUPDATE,
            pygame.DROPFILE,
            pygame.DROPBEGIN,
            pygame.DROPCOMPLETE,
            pygame.TEXTINPUT,
            pygame.TEXTEDITING,
            pygame.MOUSEBUTTONUP, # mouse events are for UI, which will happen on a frame basis
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEMOTION,
            pygame.MOUSEWHEEL,
            ]
        )
        
    def run(self):
        self.__initalise()
        
        self.InputManager.start_keyboard_hook() 
        self.input_thread.start()
        self.logic_thread.start()
        self.render_loop() # render loop has to be in main thread because calling pygame events in a seperate thread isn't allowed in macOS, stupid as fuck

        self.__exit()
             
    def __exit(self, event = None):
        self.Timing.exited = True
        self.InputManager.exit()
        pygame.font.quit()
        pygame.quit()
        
        if self.input_thread.is_alive():
            self.input_thread.join(timeout = self.Timing.poll_interval)

        if self.logic_thread.is_alive():
            self.logic_thread.join(timeout = self.Timing.tick_interval)

        os._exit(0)
              
    def render_loop(self):
        """
        Render loop handles frame based updates, so drawing frames and the UI logic and handle window events.
        Tick rate is as a fast as possible.
        """
        try:
            while not self.Timing.exited:
         
                iteration_start_time = time.perf_counter()
                
                self.Timing.current_frame_time = time.perf_counter() - self.Timing.start_times['render_loop']
                self.Timing.elapsed_times['render_loop'] = self.Timing.current_frame_time
                
                self.Timing.frame_delta_time = (self.Timing.current_frame_time - self.Timing.last_frame_time)
                self.Timing.last_frame_time = self.Timing.current_frame_time
                  
                self.do_render_tick()

                iteration_end_time = time.perf_counter()
                elapsed_time = iteration_end_time - iteration_start_time
                
                self.get_fps()
                
                time.sleep(max(0, self.Timing.frame_interval - elapsed_time))
                        
        except Exception as e:
            print(f"\033[91mError in {threading.current_thread().name}: {e}\033[0m")
            return
        
        finally: 
            if self.PRINT_WARNINGS:
                print(f"\033[92mRender loop Timing.exited in {threading.current_thread().name}\033[0m")  
            self.Timing.exited = True
            return
                
    def do_render_tick(self):
        
        start = time.perf_counter()
        
        if self.Timing.exited:
            return
        
        for event in pygame.event.get():
            EventHandler.notify(event)
        
        self.Debug.get_metrics()  
        self.Render.draw_frame()
        self.FrameClock.tick()
            
        self.Timing.iteration_times['render_loop'] = time.perf_counter() - start
                 
    def get_fps(self):
        self.Timing.FPS = self.FrameClock.get_fps()
    
    def __is_focused(self, event):
        match event.type:
            case pygame.WINDOWFOCUSGAINED:
                self.is_focused = True
            case pygame.WINDOWFOCUSLOST:
                self.is_focused = False
            case pygame.VIDEOEXPOSE:
                self.is_focused = True
            case pygame.WINDOWMINIMIZED:
                self.is_focused = False
class EventHandler:
    targets = {}

    @staticmethod
    def register(event_type):
        def decorator(fn):
            EventHandler.targets.setdefault(event_type, []).append(fn)
            return fn
        return decorator

    @staticmethod
    def notify(event):
        fn_list = EventHandler.targets.get(event.type, [])
        for fn in fn_list:
            fn(event)
    
class GameInstance():
    def __init__(self, ID, Config, TimingStruct, HandlingConfig, GameParameters):
        
        self.ID = ID
        self.Config = Config
        self.GameParameters = GameParameters
        
        self.TimingStruct = TimingStruct
        
        self.HandlingConfig = HandlingConfig
        self.HandlingStruct = StructHandling()
        
        self.FlagStruct = StructFlags()
        self.GameInstanceStruct = StructGameInstance()
        
        self.HandlingLogic = Handling(
            self.Config, 
            self.HandlingConfig, 
            self.HandlingStruct, 
            self.FlagStruct, 
        )
        
        self.GameLogic = Four(
            self.Config,
            self.FlagStruct, 
            self.GameInstanceStruct, 
            self.TimingStruct, 
            self.HandlingStruct, 
            self.HandlingConfig, 
            matrix_width = self.GameParameters['MATRIX_WIDTH'], 
            matrix_height = self.GameParameters['MATRIX_HEIGHT'],
            rotation_system = self.GameParameters['ROTATION_ SYSTEM'],
            randomiser = self.GameParameters['RANDOMISER'], 
            queue_previews = self.GameParameters['QUEUE_PREVIEWS'], 
            seed = self.GameParameters['SEED'], 
            hold = self.GameParameters['HOLD_ENABLED'], 
            allowed_spins = self.GameParameters['ALLOWED_SPINS'], 
            lock_out_ok = self.GameParameters['LOCK_OUT_OK'],
            top_out_ok = self.GameParameters['TOP_OUT_OK'],
            reset_on_top_out = self.GameParameters['RESET_ON_TOP_OUT']
        )
             
    def do_game_tick(self):
        self.GameLogic.tick()
    
    def do_handling_tick(self):
        self.HandlingLogic.tick()

@dataclass
class Timing():
    
    exited = False
    FPS: int = 144
    TPS: int = 256
    POLLING_RATE: int = 1000
    
    current_main_tick_time: float = 0
    last_main_tick_time: float = 0
    main_tick_delta_time: float = 0
    do_first_main_tick: bool = True
    main_tick_counter_last_cleared: float = 0
    main_tick_counter: int = 0
    
    current_frame_time: float = 0
    last_frame_time: float = 0
    frame_delta_time: float = 0
    do_first_frame: bool = True
    
    current_input_tick_time: int = 0
    last_input_tick_time: int = 0
    input_tick_delta_time: int = 0
    do_first_input_tick: bool = True
    input_tick_counter_last_cleared: int = 0
    input_tick_counter: int = 0
    
    start_times: Dict[str, float] = field(default_factory = lambda: {
    'input_loop': 0,
    'logic_loop': 0,
    'render_loop': 0
    })
    
    elapsed_times: Dict[str, float] = field(default_factory = lambda: {
        'input_loop': 0,
        'logic_loop': 0,
        'render_loop': 0
    })
    
    iteration_times: Dict[str, float] = field(default_factory = lambda: {
        'input_loop': 1,
        'logic_loop': 1,
        'render_loop': 1
    })
    
    def __post_init__(self):
        self.tick_interval = 1 / self.TPS
        self.poll_interval = 1 / self.POLLING_RATE
        self.frame_interval = 1 / self.FPS


class Debug():
    def __init__(self, Config, TimingStruct, RenderStruct, DebugStruct):
        """
        Manage the debug information for the game
        
        args:
            Config (StructConfig): The configuration struct
            TimingStruct (StructTiming): The timing struct
            HandlingStruct (StructHandling): The handling struct
            GameInstanceStruct (StructGameInstance): The game instance struct
            FlagStruct (StructFlags): The flag struct
            RenderStruct (StructRender): The render struct
            DebugStruct (StructDebug): The debug struct
        """
        self.Config = Config
        self.Timing = TimingStruct
        self.RenderStruct = RenderStruct
        self.DebugStruct = DebugStruct
    
    # =================================================== METRIC CALCULATION ===================================================
    
    def __calculate_metrics(self, values_list, current_value, idx, metric, larger_is_better):
        """
        Calculate the average, best and worst values of a metric
        
        args:
            values_list (list): The list of values to calculate the metrics for
            current_value (int): The current value of the metric
            idx (int): The current index of the list
            metric (str): The name of the metric
            larger_is_better (bool): Whether a larger value is better for the metric
        """
        if idx >= self.DebugStruct.max_avg_len:
            idx = 0
        
        if len(values_list) >= self.DebugStruct.max_avg_len:
            values_list.pop(idx)
        
        values_list.append(current_value)
        idx += 1
        
        average = sum(values_list) / len(values_list)
        
        if larger_is_better:
            best_value = max(values_list)
            worst_value = min(values_list)
        else:
            best_value = min(values_list)
            worst_value = max(values_list)
            
        self.__update_debug_info(metric, current_value, average, best_value, worst_value)
    
    def __update_debug_info(self, metric, current_value, average, best_value, worst_value):
        """
        Update the debug information stored in the debug struct
        
        args:
            metric (str): The name of the metric
            current_value (int): The current value of the metric
            average (int): The average value of the metric
            best_value (int): The best value of the metric
            worst_value (int): The worst value of the metric
        """
        current_attr = f"Current_{metric}"
        average_attr = f"Average_{metric}"
        best_attr = f"Best_{metric}"
        worst_attr = f"Worst_{metric}"
        
        setattr(self.DebugStruct, current_attr, current_value)
        setattr(self.DebugStruct, average_attr, average)
        setattr(self.DebugStruct, best_attr, best_value)
        setattr(self.DebugStruct, worst_attr, worst_value)
    
    # =================================================== DEBUG METRICS ===================================================
    
    def __get_tick_debug(self):
        """
        Get the tick related debug information
        """
        self.DebugStruct.TPS = self.Timing.TPS
        self.__calculate_metrics(self.DebugStruct.TPS_list, self.Timing.TPS, self.DebugStruct.tps_idx, "TickRate", True)
        self.__calculate_metrics(self.DebugStruct.tick_time_list, self.Timing.iteration_times["logic_loop"], self.DebugStruct.tick_time_idx, "ExecutionTime", False)
        self.__calculate_metrics(self.DebugStruct.delta_tick_list, (self.Config.TPS - self.DebugStruct.Current_TickRate), self.DebugStruct.delta_tick_idx, "DeltaTick", False)
        
        self.DebugStruct.TickCounter = self.Timing.main_tick_counter
        
    def __get_frame_debug(self):
        """
        Get the frame related debug information
        """
        self.DebugStruct.FPS = self.Timing.FPS
        self.__calculate_metrics(self.DebugStruct.FPS_list, self.DebugStruct.FPS, self.DebugStruct.fps_idx, "FrameRate", True)
        self.__calculate_metrics(self.DebugStruct.render_time_list, self.Timing.iteration_times["render_loop"], self.DebugStruct.render_idx, "RenderTime", False)
    
    def __get_polling_debug(self):
        """
        Get the polling related debug information
        """
        self.DebugStruct.PollingRate = self.Timing.POLLING_RATE
        self.__calculate_metrics(self.DebugStruct.polling_rate_list, self.DebugStruct.polling_rate, self.DebugStruct.polling_idx, "PollingRate", True)
        self.__calculate_metrics(self.DebugStruct.polling_time_list, self.Timing.iteration_times["input_loop"], self.DebugStruct.polling_time_idx, "PollingTime", False) 
  
        self.DebugStruct.PollingCounter = self.Timing.input_tick_counter
        
    def get_metrics(self):
        """
        Get the debug metrics for the debug menu
        """
        self.__get_tick_debug()
        self.__get_frame_debug()
        self.__get_polling_debug()
        
def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
    

