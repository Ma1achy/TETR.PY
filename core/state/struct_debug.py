from dataclasses import dataclass, field
from typing import List

@dataclass
class StructDebug():

   PRINT_WARNINGS: bool = False
   ERROR: tuple = None
   max_avg_len: int = 500
   
   tick_time_list: List[float] = field(default_factory = list)
   tick_time_idx: int = 0
  
   render_time_list: List[float] = field(default_factory = list)
   render_idx: int = 0

   tick_time: float = 0
   render_time_raw: float = 0
   
   FPS_list: List[int] = field(default_factory = list)
   FPS: int = 144
   fps_idx: int = 0
   
   TPS_list: List[int] = field(default_factory = list)
   TPS: int = 256
   tps_idx: int = 0
   
   delta_tick_list: List[float] = field(default_factory = list)
   delta_tick_idx: int = 0
   delta_tick: float = 0
   
   polling_rate_list: List[float] = field(default_factory = list)
   polling_rate: int = 1000
   polling_idx: int = 0

   polling_time_list: List[float] = field(default_factory = list)
   polling_time: float = 0
   polling_time_idx: int = 0
