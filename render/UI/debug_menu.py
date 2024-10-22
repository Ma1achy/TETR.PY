from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from utils import get_prefix

class UIDebug():
    def __init__(self, Config:StructConfig, RenderStruct:StructRender, DebugStruct:StructDebug, FlagStruct:StructFlags, Fonts):
        
        self.Fonts = Fonts
        
        self.debug_surfaces = []
        self.Config = Config
        self.RenderStruct = RenderStruct
        self.DebugStruct = DebugStruct
        self.FlagStruct = FlagStruct
    
    def draw(self, surface):
        """
        Draw the debug menu onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.__draw_debug_menu(surface)
    
    def __draw_debug_menu(self, surface):
        """
        Draw the debug information
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """      
        if not self.FlagStruct.SHOW_DEBUG_MENU:
            return
        
        self.debug_surfaces = []

        if self.DebugStruct.Average_FrameRate < self.Config.FPS * 0.95:
            fps_colour = (255, 255, 0)
        elif self.DebugStruct.Average_FrameRate < self.Config.FPS * 0.5:
            fps_colour = (255, 0, 0)
        elif self.Config.UNCAPPED_FPS:
            fps_colour = (0, 255, 255)
        else:
            fps_colour = (0, 255, 0)

        # FPS debug information
        fps_text = f'FPS: {int(self.DebugStruct.Average_FrameRate)}'
        
        if self.Config.UNCAPPED_FPS:
            fps_text += ' (UNCAPPED)'
            
        self.debug_surfaces.append((self.Fonts.hun2_big.render(fps_text, True, fps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE // 2)))

        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_FrameRate)} | best: {int(self.DebugStruct.Best_FrameRate)} | current: {int(self.DebugStruct.Current_FrameRate)}', True, fps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 1.5)))

        self.debug_surfaces.append((self.Fonts.hun2_small.render(f'Render Time: {get_prefix(self.DebugStruct.Average_RenderTime, "s")}', True, fps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 2)))

        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_RenderTime, "s")} | best: {get_prefix(self.DebugStruct.Best_RenderTime, "s")} | current: {get_prefix(self.DebugStruct.Current_RenderTime, "s")}', True, fps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 2.5)))

        if self.DebugStruct.Average_TickRate < self.Config.TPS * 0.95:
            tps_colour = (255, 0, 0)
        else:
            tps_colour = (0, 255, 0)

        # TPS debug information
        self.debug_surfaces.append((self.Fonts.hun2_big.render(f'TPS: {int(self.DebugStruct.Average_TickRate)}', True, tps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 3.5)))

        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_TickRate)} | best: {int(self.DebugStruct.Best_TickRate)} | current: {int(self.DebugStruct.Current_TickRate)}', True, tps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 4.5)))

        self.debug_surfaces.append((self.Fonts.hun2_small.render(f'Execution Time: {get_prefix(self.DebugStruct.Average_ExecutionTime, "s")}', True, tps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 5)))

        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_ExecutionTime, "s")} | best: {get_prefix(self.DebugStruct.Best_ExecutionTime, "s")} | current: {get_prefix(self.DebugStruct.Current_ExecutionTime, "s")}', True, tps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 5.5)))

        self.debug_surfaces.append((self.Fonts.hun2_small.render(f'Delta Tick: {self.DebugStruct.Average_DeltaTick:.2f}', True, tps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 6)))

        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'worst: {self.DebugStruct.Worst_DeltaTick} | best: {self.DebugStruct.Best_DeltaTick} | current: {int(self.DebugStruct.Current_DeltaTick)}', True, tps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 6.5)))

        self.debug_surfaces.append((self.Fonts.hun2_small.render(f'Tick: {self.DebugStruct.TickCounter}', True, tps_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 7)))
        
        # handling debug information
        
        if self.DebugStruct.Average_PollingRate < self.Config.POLLING_RATE * 0.95:
            poll_colour = (255, 0, 0)
        else:
            poll_colour = (0, 255, 0)
        
        self.debug_surfaces.append((self.Fonts.hun2_big.render(f'POLL: {int(self.DebugStruct.Average_PollingRate)}', True, poll_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 8)))
        
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_PollingRate)} | best: {int(self.DebugStruct.Best_PollingRate)} | current: {int(self.DebugStruct.Current_PollingRate)}', True, poll_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 9)))
        
        self.debug_surfaces.append((self.Fonts.hun2_small.render(f'Polling Time: {get_prefix(self.DebugStruct.Average_PollingTime, "s")}', True, poll_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 9.5)))
        
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_PollingTime, "s")} | best: {get_prefix(self.DebugStruct.Best_PollingTime, "s")} | current: {get_prefix(self.DebugStruct.Current_PollingTime, "s")}', True, poll_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 10)))

        das_colour = (255, 255, 255)

        self.debug_surfaces.append((self.Fonts.hun2_big.render(f'DAS: {int(self.DebugStruct.DAS_Left_Counter)} ms {int(self.DebugStruct.DAS_Right_Counter)} ms', True, das_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 11)))
        
        self.debug_surfaces.append((self.Fonts.hun2_small.render(f'Threshold: {self.DebugStruct.DAS_Threshold} ms', True, das_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 12)))
        
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'DCD: {self.DebugStruct.DCD} | DAS Cancel: {self.DebugStruct.DAS_Cancel} | Direction: {self.DebugStruct.Prioritise_Direction} (Priority: {self.DebugStruct.Direction})', True, das_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 12.5)))
        
        arr_colour = (255, 255, 255)
        
        self.debug_surfaces.append((self.Fonts.hun2_big.render(f'ARR: {int(self.DebugStruct.ARR_Left_Counter)} ms {int(self.DebugStruct.ARR_Right_Counter)} ms', True, arr_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 13.5)))
        
        self.debug_surfaces.append((self.Fonts.hun2_small.render(f'Threshold: {self.DebugStruct.ARR_Threshold} ms', True, arr_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 14.5)))
        
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'SDF: { self.DebugStruct.Soft_Drop_Factor} | PrefSD: {self.DebugStruct.Prefer_Soft_Drop} | On Floor: {self.DebugStruct.On_Floor}', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 15.5)))
        
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'Gravity: {self.DebugStruct.Gravity:.2f} G ({self.DebugStruct.G_in_ticks} ticks) | Multi: {self.DebugStruct.Gravity_Multiplier} | Counter: {self.DebugStruct.Gravity_Counter}', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 16)))
    
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'Lock Delay: {self.DebugStruct.Lock_Delay} ({self.DebugStruct.Lock_Delay_Ticks} ticks) | Counter: {self.DebugStruct.Lock_Delay_Counter} | Resets Left: {self.DebugStruct.Max_Moves} | y: {self.DebugStruct.Lowest_Pivot}', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 16.5)))
        
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'PrevAccHD: {self.DebugStruct.Prevent_Accidental_Hard_Drop} | Delay: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Time} ticks| Counter: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Counter} | Flag: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Flag}', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 17)))
        
        self.debug_surfaces.append((self.Fonts.pfw_small.render(f'Seed: {self.DebugStruct.Seed}', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.GRID_SIZE * 17.5)))
        
        for surf, coords in self.debug_surfaces:
            surface.blit(surf, coords)