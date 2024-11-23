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
import pygame_gui as gui
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
        
        self.EventHandler = EventHandler()
        self.__register_event_handlers()
        self.InputManager = InputManager(self.key_states_queue, self.Timing, self.PRINT_WARNINGS)
        self.GameInstanceManager = GameInstanceManager(self.Timing, self.PRINT_WARNINGS)
        self.Render = Render(self.Config, self.Timing, self.DebugStruct, self.game_instances)
        
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
        self.EventHandler.register(pygame.WINDOWCLOSE)(self.__exit)
       
        self.EventHandler.register(pygame.WINDOWFOCUSLOST)(self.__is_focused)
        self.EventHandler.register(pygame.WINDOWFOCUSGAINED)(self.__is_focused)
        self.EventHandler.register(pygame.VIDEOEXPOSE)(self.__is_focused)
        self.EventHandler.register(pygame.WINDOWMINIMIZED)(self.__is_focused)
    
    def __init_pygame(self):
        pygame.init()
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
                
                if self.Timing.do_first_frame:
                    self.__init_pygame()
                    self.do_render_tick()
                    self.Timing.do_first_frame = False
                    
                self.do_render_tick()

                iteration_end_time = time.perf_counter()
                elapsed_time = iteration_end_time - iteration_start_time
                
                if elapsed_time > self.Timing.frame_interval and self.PRINT_WARNINGS:
                    #print(f"\033[93mWARNING: Render loop iteration took too long! [{elapsed_time:.6f} s]\033[0m")
                    pass
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
        
        if self.Timing.exited:
            return
        
        for event in pygame.event.get():
            EventHandler.notify(event)
        
        self.Render.draw_frame()
        self.FrameClock.tick()
                 
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
    
def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
    

