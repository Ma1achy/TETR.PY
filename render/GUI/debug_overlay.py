from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_debug import StructDebug
from utils import get_prefix
from render.GUI.menu import Font

class GUIDebug():
    def __init__(self, Config: StructConfig, RenderStruct: StructRender, DebugStruct: StructDebug):
        self.Config = Config
        self.RenderStruct = RenderStruct
        self.DebugStruct = DebugStruct

        # Initialize fonts
        self.font_hun2_big = Font('hun2', self.RenderStruct.WINDOW_HEIGHT // 30)
        self.font_hun2_small = Font('hun2', self.RenderStruct.WINDOW_HEIGHT // 55)
        self.font_pfw_small = Font('pfw', self.RenderStruct.WINDOW_HEIGHT // 65)
        
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
        # Start position
        x = 10
        y = 0  # Top of the surface, adjusted incrementally
        y_padding = self.RenderStruct.WINDOW_HEIGHT // 200
        
        if self.DebugStruct.Average_FrameRate < self.Config.FPS * 0.95:
            fps_colour = '#ffff00'  # Yellow
        elif self.DebugStruct.Average_FrameRate < self.Config.FPS * 0.5:
            fps_colour = '#ff0000'  # Red
        else:
            fps_colour = '#00ff00'  # Green

        # FPS debug information
        fps_text = f'FPS: {int(self.DebugStruct.Average_FrameRate)}'

        self.font_hun2_big.draw(
            surface,
            fps_text,
            fps_colour,
            'left_top',
            x,
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_big.height + y_padding

        self.font_pfw_small.draw(
            surface, 
            f'worst: {int(self.DebugStruct.Worst_FrameRate)} | best: {int(self.DebugStruct.Best_FrameRate)} | current: {int(self.DebugStruct.Current_FrameRate)}', 
            fps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_pfw_small.height + y_padding

        self.font_hun2_small.draw(
            surface, 
            f'Render Time: {get_prefix(self.DebugStruct.Average_RenderTime, "s")}', 
            fps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_small.height + y_padding

        self.font_pfw_small.draw(
            surface, 
            f'worst: {get_prefix(self.DebugStruct.Worst_RenderTime, "s")} | best: {get_prefix(self.DebugStruct.Best_RenderTime, "s")} | current: {get_prefix(self.DebugStruct.Current_RenderTime, "s")}', 
            fps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_pfw_small.height + y_padding

        # TPS debug information
        tps_colour = '#ff0000' if self.DebugStruct.Average_TickRate < self.Config.TPS * 0.95 else '#00ff00'

        self.font_hun2_big.draw(
            surface,
            f'TPS: {int(self.DebugStruct.Average_TickRate)}',
            tps_colour,
            'left_top',
            x,
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_big.height + y_padding

        self.font_pfw_small.draw(
            surface, 
            f'worst: {int(self.DebugStruct.Worst_TickRate)} | best: {int(self.DebugStruct.Best_TickRate)} | current: {int(self.DebugStruct.Current_TickRate)}', 
            tps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_pfw_small.height + y_padding

        self.font_hun2_small.draw(
            surface, 
            f'Execution Time: {get_prefix(self.DebugStruct.Average_ExecutionTime, "s")}', 
            tps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_small.height + y_padding

        self.font_pfw_small.draw(
            surface, 
            f'worst: {get_prefix(self.DebugStruct.Worst_ExecutionTime, "s")} | best: {get_prefix(self.DebugStruct.Best_ExecutionTime, "s")} | current: {get_prefix(self.DebugStruct.Current_ExecutionTime, "s")}', 
            tps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_pfw_small.height + y_padding

        self.font_hun2_small.draw(
            surface, 
            f'Delta Tick: {self.DebugStruct.Average_DeltaTick:.2f}', 
            tps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_small.height + y_padding

        self.font_pfw_small.draw(
            surface, 
            f'worst: {self.DebugStruct.Worst_DeltaTick} | best: {self.DebugStruct.Best_DeltaTick} | current: {int(self.DebugStruct.Current_DeltaTick)}', 
            tps_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_pfw_small.height + y_padding

        self.font_hun2_small.draw(
            surface,
            f'Tick: {self.DebugStruct.TickCounter}', 
            tps_colour,
            'left_top',
            x,
            y,
            (32, 32, 32, 128)
            )
        y += self.font_hun2_small.height + y_padding

        # Polling debug information
        poll_colour = '#ff0000' if self.DebugStruct.Average_PollingRate < self.Config.POLLING_RATE * 0.95 else '#00ff00'

        self.font_hun2_big.draw(
            surface,
            f'POLL: {int(self.DebugStruct.Average_PollingRate)}',
            poll_colour,
            'left_top',
            x,
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_big.height + y_padding

        self.font_pfw_small.draw(
            surface, 
            f'worst: {int(self.DebugStruct.Worst_PollingRate)} | best: {int(self.DebugStruct.Best_PollingRate)} | current: {int(self.DebugStruct.Current_PollingRate)}', 
            poll_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_pfw_small.height + y_padding

        self.font_hun2_small.draw(
            surface, 
            f'Polling Time: {get_prefix(self.DebugStruct.Average_PollingTime, "s")}', 
            poll_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_small.height + y_padding

        self.font_pfw_small.draw(
            surface, 
            f'worst: {get_prefix(self.DebugStruct.Worst_PollingTime, "s")} | best: {get_prefix(self.DebugStruct.Best_PollingTime, "s")} | current: {get_prefix(self.DebugStruct.Current_PollingTime, "s")}', 
            poll_colour, 
            'left_top', 
            x, 
            y,
            (32, 32, 32, 128)
        )
        y += self.font_pfw_small.height + y_padding
        
        self.font_hun2_small.draw(
            surface,
            f'Tick: {self.DebugStruct.PollingCounter}',
            poll_colour, 'left_top',
            x,
            y,
            (32, 32, 32, 128)
        )
        y += self.font_hun2_small.height + y_padding
