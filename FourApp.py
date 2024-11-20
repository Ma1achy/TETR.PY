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

# plan:
# have pygame only deal with rendering on its own thread
# each game instance will have its own thread and will have async methods for handling and game logic
# main thread will handle game instance creation and deletion and things like menu logic
# input will be handled on its own thread

# need to change handling to take in key_states

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
        self.frame_interval = 1 / self.Config.FPS
        self.tick_interval = 1 / self.Config.TPS
        self.poll_interval = 1 / self.Config.POLLING_RATE
        
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
        
    def run(self):
        self.__initalise()
        
        self.InputManager.start_keyboard_hook()
        self.input_thread.start()
        self.render_thread.start()
        
        self.main_loop() 
                
    def exit(self):
        self.exited = True
        self.input_thread.join()
        self.render_thread.join()
        
    def main_loop(self):
        while not self.exited:
            iteration_start_time = time.perf_counter()
            
            self.Timing.current_main_tick_time = time.perf_counter() - self.Timing.start_times['main_loop']
            self.Timing.elapsed_times['main_loop'] = self.Timing.current_main_tick_time
            
            self.Timing.main_tick_delta_time += (self.Timing.current_main_tick_time - self.Timing.last_main_tick_time) / self.tick_interval
            self.Timing.last_main_tick_time = self.Timing.current_main_tick_time
            
            if self.Timing.do_first_main_tick:
                self.do_main_tick()
                self.Timing.do_first_main_tick = False
                
            while self.Timing.main_tick_delta_time >= 1:
                self.do_main_tick()
                self.Timing.main_tick_delta_time -= 1
            
            if self.Timing.current_main_tick_time > self.Timing.main_tick_counter_last_cleared + 1:
                self.Timing.main_tick_counter = 0
                self.Timing.main_tick_counter_last_cleared += 1
            
            iteration_end_time = time.perf_counter()
            
            iteration_time = iteration_end_time - iteration_start_time
            
            if iteration_time < self.tick_interval:
                time.sleep(self.tick_interval - iteration_time)
            else:
                if self.PRINT_WARNINGS:
                    print(f"\033[93mWARNING: Main loop iteration took too long! [{iteration_time:.6f} seconds]\033[0m")
                    
    def render_loop(self):
    
        while not self.exited:
            
            iteration_start_time = time.perf_counter()
            
            self.Timing.current_frame_time = time.perf_counter() - self.Timing.start_times['render_loop']
            self.Timing.elapsed_times['render_loop'] = self.Timing.current_frame_time
            
            self.Timing.frame_delta_time += (self.Timing.current_frame_time - self.Timing.last_frame_time) / self.frame_interval
            self.Timing.last_frame_time = self.Timing.current_frame_time
            
            self.do_render_tick()

            iteration_end_time = time.perf_counter()
            iteration_time = iteration_end_time - iteration_start_time
            
            if iteration_time < self.frame_interval:
                time.sleep(self.frame_interval - iteration_time)
            else:
                if self.PRINT_WARNINGS:
                    print(f"\033[93mWARNING: Render loop iteration took too long! [{iteration_time:.6f} seconds]\033[0m")
            
    def input_loop(self):
    
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
                self.Timing.input_tick_counter = 0
                self.Timing.input_tick_counter_last_cleared += 1

            iteration_end_time = time.perf_counter()
            iteration_time = iteration_end_time - iteration_start_time
            
            if iteration_time < self.poll_interval:
                time.sleep(self.poll_interval - iteration_time)
            else:
                if self.PRINT_WARNINGS:
                    print(f"\033[93mWARNING: Input loop iteration took too long! [{iteration_time:.6f} seconds]\033[0m")

    def do_main_tick(self):
    
        self.Timing.main_tick_counter += 1
        time.sleep(self.tick_interval*0.25) # temp to simulate work
        
    def do_render_tick(self):
        time.sleep(self.frame_interval*0.25) # temp to simulate work
    
    def do_input_tick(self):
        if self.InputManager.wait_for_input_event(timeout = self.poll_interval):
            self.key_states = self.key_states_queue.get()
            print(self.key_states)
    
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
            rotation_system = self.GameParameters['ROTATION_SYSTEM'],
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
    

