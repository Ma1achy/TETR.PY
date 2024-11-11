from dataclasses import dataclass, field
from typing import Dict

@dataclass
class StructTiming():

    current_time: float = 0
    last_tick_time: float = 0
    delta_time: float = 0
    do_first_tick: bool = True
    tick_counter: int = 0
    tick_counter_last_cleared: float = 0
    FPS = 144
    TPS = 256

    current_frame_time: float = 0
    last_frame_time: float = 0
    delta_frame_time: float = 0
    draw_first_frame: bool = True

    start_times: Dict[str, int] = field(default_factory = lambda: {
    'handle_events': 0,
    'game_loop': 0,
    'get_debug_info': 0,
    'render_loop': 0
    })
    
    elapsed_times: Dict[str, int] = field(default_factory = lambda: {
        'handle_events': 0,
        'game_loop': 0,
        'get_debug_info': 0,
        'render_loop': 0
    })
    
    iter_times: Dict[str, int] = field(default_factory = lambda: {
        'handle_events': 1,
        'game_loop': 1,
        'get_debug_info': 1,
        'render_loop': 1
    })
    
    handling_current_time: float = 0
    handling_last_tick_time: float = 0
    handling_delta_time: float = 0
    handling_do_first_tick: bool = True
    handling_tick_counter: int = 0
    handling_tick_counter_last_cleared: float = 0
    handling_polling_rate: int = 1000
    