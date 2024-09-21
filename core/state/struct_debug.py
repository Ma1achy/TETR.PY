from dataclasses import dataclass, field
from typing import List

@dataclass
class StructDebug():

   DEBUG: bool = False
   
   debug_dict: dict = None
   max_avg_len: int = 500
   
   tick_times: List[float] = field(default_factory = list)
   exe_idx: int = 0
   worst_tick_time: float = 0
   best_tick_time: float = 0
   
   render_times: List[float] = field(default_factory = list)
   r_idx: int = 0
   worst_render_time: float = 0
   best_render_time: float = 0
   
   tick_time: float = 0
   render_time_raw: float = 0
   
   FPSs: List[int] = field(default_factory = list)
   FPS: int = 144
   average_FPS: float = 0
   fps_idx: int = 0
   worst_fps: int = 0
   best_fps: int = 0
   
   TPSs: List[int] = field(default_factory = list)
   TPS: int = 256
   average_TPS: float = 0
   tps_idx: int = 0
   worst_tps: int = 0
   best_tps: int = 0
   
   dfs: List[float] = field(default_factory = list)
   df_idx: int = 0
   average_df: float = 0
   delta_tick: float = 0
   worst_df: float = 0
   best_df: float = 0
   
   POLLING_RATEs: List[float] = field(default_factory = list)
   POLLING_RATE: int = 1000
   polling_idx: int = 0
   average_polling: float = 0
   worst_polling: int = 0
   best_polling: int = 0
   
   POLLING_TIMES: List[float] = field(default_factory = list)
   POLLING_T: float = 0
   polling_t_idx: int = 0
   average_polling_t: float = 0
   worst_polling_t: float = 0
   best_polling_t: float  = 0
           
   draw_bounding_box: bool = False
   draw_origin: bool = False
   draw_pivot: bool = False