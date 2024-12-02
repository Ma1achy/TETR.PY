from dataclasses import dataclass, field
from typing import Dict

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