from dataclasses import dataclass, field
from typing import Dict
from collections import deque
import time

@dataclass
class Timing():
    
    restart: bool = False
    exited: bool  = False
    restarts: int = 0
    restart_interval: float = 0.5
    last_restart_time: float = 0
    
    target_FPS: int = 144
    target_TPS: int = 256
    target_POLLING_RATE: int = 1000
    
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
    render_tick_delta_time: float = 0
    do_first_frame: bool = True
    
    current_input_tick_time: int = 0
    last_input_tick_time: int = 0
    input_tick_delta_time: int = 0
    do_first_input_tick: bool = True
    input_tick_counter_last_cleared: int = 0
    input_tick_counter: int = 0
    
    is_focused: bool = False
    
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