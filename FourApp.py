import keyboard
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
import pygame
import queue
from dataclasses import dataclass, field
from typing import Dict
import sys

# plan:
# have pygame only deal with rendering on its own thread
# each game instance will have its own thread and will have async methods for handling and game logic
# main thread will handle game instance creation and deletion and things like menu logic
# input will be handled on its own thread

# need to change handling to take in key_states

#TODO: change renderer methods to NOT use methods ASSOCIATED WITH A GAME INSTANCE
#      change game instance to UPDATE variables, i.e, current_tetromino is on floor etc which are contained in GameInstanceStruct
#      GameInstanceStruct will have to be contained in a Queue or something so that the renderer can access it in a thread safe way
#      Debug Menu will have to be changed in a similar way but ALSO, there will have to be per game instance debug info
class FourApp():
    def __init__(self):
        self.game_instances = []
        
        self.key_states_queue = queue.Queue() 
            
        self.InputManager = InputManager(self.key_states_queue)
        
        self.Config = StructConfig()
        self.TimingStruct = StructTiming()
        
        self.Timing = Timing()
        
        self.GameInstanceStruct = StructGameInstance()
        self.FlagStruct = StructFlags()
        self.RenderStruct = StructRender()
        self.DebugStruct = StructDebug()
        self.HandlingConfig = HandlingConfig()
        
        self.TPS = self.Config.TPS
        self.FPS = self.Config.FPS
        self.POLLING_RATE = self.Config.POLLING_RATE
        
        self.frame_interval = 1 / self.Config.FPS
        self.tick_interval = 1 / self.Config.TPS
        self.poll_interval = 1 / self.Config.POLLING_RATE
        
        self.max_main_ticks_per_iteration = 256
        
        self.GameInstanceManager = GameInstanceManager(self.Config, self.TimingStruct, self.HandlingConfig, self.game_instances)
        
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
        
        self.exited = False
        self.PRINT_WARNINGS = True
        
    def __initalise(self):
        set_flag_attr()
        
        self.input_thread = threading.Thread(target = self.input_loop)
        self.render_thread = threading.Thread(target = self.render_loop)
        
        self.Timing.start_times['input_loop'] = time.perf_counter()
        self.Timing.start_times['main_loop'] = time.perf_counter()
        self.Timing.start_times['render_loop'] = time.perf_counter()
    
    def __init_pygame(self):
        pygame.init()
    
    def run(self):
        self.__initalise()
        
        self.InputManager.start_keyboard_hook()
        self.input_thread.start()
        self.render_thread.start()
        self.main_loop() 
        
        self.__exit()
             
    def __exit(self):
        self.exited = True
        self.input_thread.join()
        self.render_thread.join()
        
        keyboard.unhook_all()
        pygame.quit()
        sys.exit()
        
    def main_loop(self):
        try:
            while not self.exited:
                iteration_start_time = time.perf_counter()
                ticks_done = 0
                
                self.Timing.current_main_tick_time = time.perf_counter() - self.Timing.start_times['main_loop']
                self.Timing.elapsed_times['main_loop'] = self.Timing.current_main_tick_time
                
                self.Timing.main_tick_delta_time += (self.Timing.current_main_tick_time - self.Timing.last_main_tick_time) / self.tick_interval
                self.Timing.last_main_tick_time = self.Timing.current_main_tick_time
                
                if self.Timing.do_first_main_tick:

                    self.do_main_tick()
                    self.Timing.do_first_main_tick = False
                    
                while self.Timing.main_tick_delta_time >= 1 and ticks_done < self.max_main_ticks_per_iteration: # only process a certain number of ticks per iteration otherwise drop the extra ticks to catch up
                    self.do_main_tick()
                    self.Timing.main_tick_delta_time -= 1
                    ticks_done += 1
                
                # recalibrate if too many ticks are processed in one iteration
                if ticks_done > self.max_main_ticks_per_iteration:
                    if self.PRINT_WARNINGS:
                        print("\033[93mWARNING: Too many ticks processed in one iteration of Main Loop, recalibrating...\033[0m")
                        
                    self.Timing.main_tick_delta_time = 1
                    
                if self.Timing.current_main_tick_time > self.Timing.main_tick_counter_last_cleared + 1:
                    self.get_tps()
                    self.Timing.main_tick_counter = 0
                    self.Timing.main_tick_counter_last_cleared += 1
                
                iteration_end_time = time.perf_counter()
                elapsed_time = iteration_end_time - iteration_start_time
    
                if elapsed_time > self.tick_interval and self.PRINT_WARNINGS:
                    print(f"\033[93mWARNING: Main loop iteration took too long! [{elapsed_time:.6f} s]\033[0m")
                        
                time.sleep(max(0, self.tick_interval - elapsed_time))
                        
        except Exception as e:
            print(f"\033[91mError in {threading.current_thread().name}: {e}\033[0m")
            self.__exit()
              
    def render_loop(self):
        
        try:
            while not self.exited:
                
                iteration_start_time = time.perf_counter()
                
                self.Timing.current_frame_time = time.perf_counter() - self.Timing.start_times['render_loop']
                self.Timing.elapsed_times['render_loop'] = self.Timing.current_frame_time
                
                self.Timing.frame_delta_time += (self.Timing.current_frame_time - self.Timing.last_frame_time) / self.frame_interval
                self.Timing.last_frame_time = self.Timing.current_frame_time
                
                if self.Timing.do_first_frame:
                    self.__init_pygame()
                    self.do_render_tick()
                    self.Timing.do_first_frame = False
                    
                self.do_render_tick()

                iteration_end_time = time.perf_counter()
                elapsed_time = iteration_end_time - iteration_start_time
                
                if elapsed_time < self.frame_interval:
                    time.sleep(0)
                else:
                    if self.PRINT_WARNINGS:
                        print(f"\033[93mWARNING: Render loop iteration took too long! [{elapsed_time:.6f} s]\033[0m")
                    time.sleep(0)
                        
        except Exception as e:
            print(f"\033[91mError in {threading.current_thread().name}: {e}\033[0m")
            self.__exit()
            
    def input_loop(self):
    
        try:
            while not self.InputManager.stop_event.is_set() and not self.exited:
                
                iteration_start_time = time.perf_counter()
                
                self.Timing.current_input_tick_time = time.perf_counter() - self.Timing.start_times['input_loop']
                self.Timing.elapsed_times['input_loop'] = self.Timing.current_input_tick_time
                
                self.Timing.input_tick_delta_time += (self.Timing.current_input_tick_time - self.Timing.last_input_tick_time) / self.poll_interval
                self.Timing.last_input_tick_time = self.Timing.current_input_tick_time
                
                if self.Timing.do_first_input_tick:
                    self.do_input_tick()
                    self.Timing.do_first_input_tick = False
                
                while self.Timing.input_tick_delta_time >= 1:
                    self.do_input_tick()
                    self.Timing.input_tick_delta_time -= 1
                
                if self.Timing.current_input_tick_time > self.Timing.input_tick_counter_last_cleared + 1:
                    self.get_poll_rate()
                    self.Timing.input_tick_counter = 0
                    self.Timing.input_tick_counter_last_cleared += 1

                iteration_end_time = time.perf_counter()
                elapsed_time = iteration_end_time - iteration_start_time
                
                if elapsed_time < self.poll_interval:
                    time.sleep(0)
                else:
                    if self.PRINT_WARNINGS:
                        print(f"\033[93mWARNING: Input loop iteration took too long! [{elapsed_time:.6f} s]\033[0m")
                    time.sleep(0)
            else:
                time.sleep(0)
                         
        except Exception as e:
            print(f"\033[91mError in {threading.current_thread().name}: {e}\033[0m")
            self.__exit()
            
    def do_main_tick(self):
        print(self.TPS, self.POLLING_RATE)
        time.sleep(self.tick_interval)
        self.Timing.main_tick_counter += 1
       
    def do_render_tick(self):
        
        pygame.event.pump() # the pygame event queue must be called or the os will think the app is not responding
                    
    def do_input_tick(self):
        
        if self.InputManager.wait_for_input_event(timeout = self.poll_interval):
           
            self.key_states = self.key_states_queue.get()
            print(self.key_states)
            
        self.Timing.input_tick_counter += 1
        
    def get_tps(self):
        self.TPS = self.Timing.main_tick_counter
        self.Timing.TPS = self.TPS
        
    def get_poll_rate(self):
        self.poll_rate = self.Timing.input_tick_counter
        self.Timing.POLLING_RATE = self.poll_rate
class InputManager:
    def __init__(self, key_states_queue):
        self.key_states = {}
        self.key_states_queue = key_states_queue
        self.input_event = threading.Event()
        self.stop_event = threading.Event()
        
    def start_keyboard_hook(self):
        keyboard.hook(self.get_key_events)
    
    def get_key_events(self, key_event):
    
        if key_event.event_type == keyboard.KEY_DOWN:
            self.on_key_press(key_event)
            
        elif key_event.event_type == keyboard.KEY_UP:
            self.on_key_release(key_event)
        
        self.queue_key_states()
        self.input_event.set()

    def queue_key_states(self):
        self.key_states_queue.put(self.key_states)

    def on_key_press(self, key):
        keyinfo = self.__get_key_info(key)
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = True
                
        except KeyError:
            KeyEntry = self.key_states.setdefault(keyinfo, {'current': False, 'previous': False})
            KeyEntry['previous'] = KeyEntry['current']
            KeyEntry['current'] = True
        
    def on_key_release(self, key):
        keyinfo = self.__get_key_info(key)
        
        try:
            KeyEntry = self.key_states[keyinfo]
            if KeyEntry:
                KeyEntry['previous'] = KeyEntry['current']
                KeyEntry['current'] = False
                
        except KeyError:
            KeyEntry = self.key_states.setdefault(keyinfo, {'current': False, 'previous': False})
            KeyEntry['previous'] = KeyEntry['current']
            KeyEntry['current'] = False
        
    def __get_key_info(self, key):
        return key if isinstance(key, str) else key.name

    def stop(self):
        self.stop_event.set()
    
    def wait_for_input_event(self, timeout = None):
        if self.input_event.wait(timeout = timeout):
            self.input_event.clear()  
            return True
        return False
        
class GameInstanceManager():
    def __init__(self, Config, TimingStruct, HandlingConfig, game_instances):
        
        self.game_instances = game_instances

        self.Config = Config
        self.TimingStruct = TimingStruct
        self.HandlingConfig = HandlingConfig
        
    def create_instance(self, ID, Config, TimingStruct, HandlingConfig, GameParameters):
        self.game_instances.append(GameInstance(ID, Config, TimingStruct, HandlingConfig, GameParameters))
        
    def remove_instance(self, ID):
        self.game_instances = [instance for instance in self.game_instances if instance.ID != ID]
           
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
        
    def start_game_tick_thread(self):
        self.game_thread = threading.Thread(target=self.game_loop, daemon = True)
        self.game_thread.start()
    
    def start_handling_tick_thread(self):
        self.handling_thread = threading.Thread(target=self.handling_loop, daemon = True)
        self.handling_thread.start()
        
    def game_loop(self):
        while True:
            self.do_game_tick()
            
    def handling_loop(self):
        while True:
            self.do_handling_tick()

    def do_game_tick(self):
        self.GameLogic.tick()
    
    def do_handling_tick(self):
        self.HandlingLogic.tick()

@dataclass
class Timing():
    
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
    'main_loop': 0,
    'render_loop': 0
    })
    
    elapsed_times: Dict[str, float] = field(default_factory = lambda: {
        'input_loop': 0,
        'main_loop': 0,
        'render_loop': 0
    })
    
    iteration_times: Dict[str, float] = field(default_factory = lambda: {
        'input_loop': 1,
        'main_loop': 1,
        'render_loop': 1
    })
    

def main():
    app = FourApp()
    app.run()

if __name__ == "__main__":
    main()
    

