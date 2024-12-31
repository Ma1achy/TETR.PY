from app.debug.debug_metrics import DebugMetrics
from utils import get_prefix
from render.GUI.font import Font
import pygame

class GUIDebug():
    def __init__(self, window, Timing, RenderStruct, DebugStruct: DebugMetrics):
        """
        A debug visor that displays debug information
        
        args:
            window (pygame.Surface): The window to draw the debug menu onto
            Timing (Timing): The Timing object
            RenderStruct (RenderStruct): The RenderStruct object
            DebugStruct (DebugMetrics): The DebugMetrics object
        """
        self.window = window
        self.Timing = Timing
        self.RenderStruct = RenderStruct
        self.DebugStruct = DebugStruct

        # Initialize fonts
        self.font_hun2_big = Font('hun2', 40)
        self.font_hun2_small = Font('hun2', 12)
        self.font_pfw_small = Font('pfw', 12)
        self.font_cr_medium = Font('cr', 20)
        self.font_cr_small = Font('cr', 12)
        
        self.padding_x = 10
        self.padding_y = 10
        self.debug_surface = pygame.Surface((1500 - self.padding_x * 2, 100), pygame.SRCALPHA|pygame.HWSURFACE)
        
        self.fps_rect = pygame.Rect(self.padding_x, self.padding_y*3, self.debug_surface.get_width()//3 - self.padding_x, 80 - self.padding_y * 2)
        self.tps_rect = pygame.Rect(self.debug_surface.get_width()//3 + self.padding_x, self.padding_y*3, self.debug_surface.get_width()//3 - self.padding_x, 80 - self.padding_y * 2)
        self.polling_rect = pygame.Rect(self.debug_surface.get_width()//3 * 2 + self.padding_x, self.padding_y*3, self.debug_surface.get_width()//3 - self.padding_x * 2, 80 - self.padding_y * 2)
        self.mem_rect = pygame.Rect(self.tps_rect.left + self.tps_rect.width//2 - 25 ,5, self.polling_rect.width + self.tps_rect.width//2 + self.padding_x + 25, 20)
        
        self.fps_surface = pygame.Surface((self.fps_rect.width, self.fps_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        self.tps_surface = pygame.Surface((self.tps_rect.width, self.tps_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        self.polling_surface = pygame.Surface((self.polling_rect.width, self.polling_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        self.mem_surface = pygame.Surface((self.mem_rect.width, self.mem_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        
    def draw(self):
        """
        Draw the debug menu onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.debug_surface.fill((32, 32, 32, 200))
        self.tps_surface.fill((0, 0, 0, 64))
        self.fps_surface.fill((0, 0, 0, 64))
        self.polling_surface.fill((0, 0, 0, 64))
        self.mem_surface.fill((0, 0, 0, 64))
        
        pygame.draw.rect(self.debug_surface, (255, 255, 255, 64), self.fps_rect, 1)
        pygame.draw.rect(self.debug_surface, (255, 255, 255, 64), self.tps_rect, 1)
        pygame.draw.rect(self.debug_surface, (255, 255, 255, 64), self.polling_rect, 1)
        pygame.draw.rect(self.debug_surface, (255, 255, 255, 64), (self.mem_rect), 1)
        pygame.draw.rect(self.debug_surface, (255, 255, 255, 64), (0, 0, self.debug_surface.get_width(), self.debug_surface.get_height()), 1)
        
        self.__draw_debug_menu()
        self.debug_surface.blit(self.fps_surface, self.fps_rect.topleft)
        self.debug_surface.blit(self.tps_surface, self.tps_rect.topleft)
        self.debug_surface.blit(self.polling_surface, self.polling_rect.topleft)
        self.debug_surface.blit(self.mem_surface, self.mem_rect.topleft)
        
        self.window.blit(self.debug_surface, (self.padding_x, self.padding_y))
    
    def __draw_debug_menu(self):
        """
        Draw the debug information
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.draw_fps_debug()
        self.draw_tps_debug()
        self.draw_polling_debug()
        self.draw_mem_debug()
        self.draw_build_info()
    
    def draw_build_info(self):
        """
        Draw the build information
        """
        x = 10
        
        self.font_cr_medium.draw(
            self.debug_surface, 
            f'TETR.PY v. {self.DebugStruct.BuildInfo['VERSION']}', 
            '#ffffff', 
            'left_top', 
            x,
            -5,
        )
        
        x += self.font_cr_medium.get_width() + 10
        
        self.font_cr_small.draw(
            self.debug_surface, 
            f'{self.DebugStruct.BuildInfo["BUILD_DATE"]}', 
            '#ffffff', 
            'left_top', 
            x,
            -2.5,
        )
        
        
        x += self.font_cr_small.get_width() +2.5
        
        self.font_cr_small.draw(
            self.debug_surface, 
            f'({self.DebugStruct.BuildInfo["BUILD_ENV"]})', 
            '#ffffff', 
            'left_top', 
            x,
            -2.5,
        )
        
        x += self.font_cr_small.get_width() + 2.5
        
        self.font_cr_small.draw(
            self.debug_surface,
            f'| {self.DebugStruct.BuildInfo["GIT_BRANCH"]}:',
            '#ffffff',
            'left_top',
            x,
            -2.5,
        )
        
        x += self.font_cr_small.get_width() + 2.5
        
        self.font_cr_small.draw(
            self.debug_surface, 
            f'{self.DebugStruct.BuildInfo["GIT_COMMIT_HASH"]}', 
            '#ffffff', 
            'left_top', 
            x,
            -2.5,
        )
        
        x = self.font_cr_medium.get_width() + 20
        
        self.font_cr_small.draw(
            self.debug_surface, 
            f'OS: {self.DebugStruct.OS}', 
            '#ffffff', 
            'left_top', 
            x,
            10,
        )
        
        x += self.font_cr_small.get_width() + 2.5
        
        self.font_cr_small.draw(
            self.debug_surface, 
            f'| Python {self.DebugStruct.PythonVersion}', 
            '#ffffff', 
            'left_top', 
            x,
            10,
        )
        
        x += self.font_cr_small.get_width() + 2.5
        
        self.font_cr_small.draw(
            self.debug_surface, 
            f'| Pygame {self.DebugStruct.PygameVersion}', 
            '#ffffff', 
            'left_top', 
            x,
            10,
        )
        
    
    def draw_fps_debug(self):
        """
        Draw the FPS debug information
        """
        x = 10
        y = 10 
        
        fps_colour = '#ffff00' if self.DebugStruct.Average_FrameRate < self.Timing.target_FPS * 0.95 else '#ff0000' if self.DebugStruct.Average_FrameRate < self.Timing.target_FPS * 0.5 else '#00ff00'
            
        fps_text = f'FPS: {int(self.DebugStruct.Average_FrameRate)}'

        self.font_hun2_big.draw(
            self.fps_surface,
            fps_text,
            fps_colour,
            'left_top',
            x,
            0,
        )
     
        self.font_hun2_small.draw(
            self.fps_surface, 
            f'Render Time: {get_prefix(self.DebugStruct.Average_RenderTime, "s")}', 
            fps_colour, 
            'right_top', 
            x,
            y,
        )
        y += self.font_hun2_small.height

        self.font_pfw_small.draw(
            self.fps_surface, 
            f'c: {get_prefix(self.DebugStruct.Current_RenderTime, "s")} b: {get_prefix(self.DebugStruct.Best_RenderTime, "s")} w: {get_prefix(self.DebugStruct.Worst_RenderTime, "s")}', 
            fps_colour, 
            'right_top', 
            x, 
            y,
        )
        y += self.font_pfw_small.height 
        
        self.font_pfw_small.draw(
            self.fps_surface, 
            f'c: {int(self.DebugStruct.Current_FrameRate)} b: {int(self.DebugStruct.Best_FrameRate)} w: {int(self.DebugStruct.Worst_FrameRate)}', 
            fps_colour, 
            'right_top', 
            x,
            y,    
        )

    def draw_tps_debug(self):
        """
        Draw the TPS debug information
        """
        x = 10
        y = 10
        
        # TPS debug information
        tps_colour = '#ff0000' if self.DebugStruct.Average_TickRate < self.Timing.target_TPS * 0.95 else '#00ff00'

        self.font_hun2_big.draw(
            self.tps_surface,
            f'TPS: {int(self.DebugStruct.Average_TickRate)}',
            tps_colour,
            'left_top',
            x,
            0,
        )

        self.font_hun2_small.draw(
            self.tps_surface, 
            f'Execution Time: {get_prefix(self.DebugStruct.Average_ExecutionTime, "s")}', 
            tps_colour, 
            'right_top', 
            x, 
            y,
        )
        y += self.font_hun2_small.height
        
        self.font_pfw_small.draw(
            self.tps_surface,
            f'c: {get_prefix(self.DebugStruct.Current_ExecutionTime, "s")} b: {get_prefix(self.DebugStruct.Best_ExecutionTime, "s")} w: {get_prefix(self.DebugStruct.Worst_ExecutionTime, "s")}', 
            tps_colour,
            'right_top',
            x, 
            y,
        )
        y += self.font_pfw_small.height
     
        self.font_pfw_small.draw(
            self.tps_surface, 
            f'c: {int(self.DebugStruct.Current_TickRate)} b: {int(self.DebugStruct.Best_TickRate)} w: {int(self.DebugStruct.Worst_TickRate)}', 
            tps_colour, 
            'right_top', 
            x, 
            y,
        )
        y += self.font_pfw_small.height

       
    def draw_polling_debug(self):
        """
        Draw the polling debug information
        """
        x = 10
        y = 10
        
        # Polling debug information
        poll_colour = '#ff0000' if self.DebugStruct.Average_PollingRate < self.Timing.target_POLLING_RATE * 0.95 else '#00ff00'

        self.font_hun2_big.draw(
            self.polling_surface,
            f'POLL: {int(self.DebugStruct.Average_PollingRate)}',
            poll_colour,
            'left_top',
            x,
            0,
        )
           
        self.font_hun2_small.draw(
            self.polling_surface, 
            f'Polling Time: {get_prefix(self.DebugStruct.Average_PollingTime, "s")}', 
            poll_colour, 
            'right_top', 
            x, 
            y,
        )
        
        y += self.font_hun2_small.height
     
        self.font_pfw_small.draw(
            self.polling_surface, 
            f'c: {get_prefix(self.DebugStruct.Current_PollingTime, "s")} b: {get_prefix(self.DebugStruct.Best_PollingTime, "s")} w: {get_prefix(self.DebugStruct.Worst_PollingTime, "s")}', 
            poll_colour, 
            'right_top', 
            x, 
            y,
        )
        
        y += self.font_pfw_small.height
        
        self.font_pfw_small.draw(
            self.polling_surface, 
            f'c: {int(self.DebugStruct.Current_PollingRate)} b: {int(self.DebugStruct.Best_PollingRate)} w: {int(self.DebugStruct.Worst_PollingRate)}', 
            poll_colour, 
            'right_top', 
            x, 
            y,
        )
        
        y += self.font_pfw_small.height
    
    def draw_mem_debug(self):
        """
        Draw the memory debug information
        """
        x = 10
        y = 0
        
        mem_colour = '#00ff00' if self.DebugStruct.MemoryPercent < 50 else '#ffff00' if self.DebugStruct.MemoryPercent < 75 else '#ff0000'
            
        self.font_pfw_small.draw(
            self.mem_surface, 
            f'Memory: {self.DebugStruct.UsedMemory}/{self.DebugStruct.TotalMemory} ({self.DebugStruct.MemoryPercent:.2f}%)', 
            mem_colour, 
            'left_top', 
            x, 
            y,
        )
        
        x += self.font_pfw_small.get_width() + 10
        
        cpu_colour = '#00ff00' if self.DebugStruct.CPU_Usage < 50 else '#ffff00' if self.DebugStruct.CPU_Usage < 75 else '#ff0000'
        
        self.font_pfw_small.draw(
            self.mem_surface, 
            f'CPU: {self.DebugStruct.CPU_Usage}%', 
            cpu_colour, 
            'left_top', 
            x, 
            y,
        )
        
        x += self.font_pfw_small.get_width() + 10
        
        self.font_pfw_small.draw(
            self.mem_surface, 
            f'GPU: {self.DebugStruct.GPUStats['gpu_name']} (ID: {self.DebugStruct.GPUStats['gpu_id']})', 
            '#ffffff', 
            'left_top', 
            x, 
            y,
        )
        
        x += self.font_pfw_small.get_width() + 10
        
        temp_colour = '#00ff00' if self.DebugStruct.GPUStats['gpu_temperature'] < 50 else '#ffff00' if self.DebugStruct.GPUStats['gpu_temperature'] < 75 else '#ff0000'
        
        self.font_pfw_small.draw(
            self.mem_surface, 
            f'{self.DebugStruct.GPUStats['gpu_temperature']}°C', 
            temp_colour, 
            'left_top', 
            x, 
            y,
        )
        
        x += self.font_pfw_small.get_width() + 10
        
        gpu_colour = '#00ff00' if self.DebugStruct.GPUStats['gpu_load'] < 50 else '#ffff00' if self.DebugStruct.GPUStats['gpu_load'] < 75 else '#ff0000'
        
        self.font_pfw_small.draw(
            self.mem_surface, 
            f'{self.DebugStruct.GPUStats['gpu_memory_used']}/{self.DebugStruct.GPUStats['gpu_memory_total']} ({self.DebugStruct.GPUStats['gpu_load']:.0f}%)', 
            gpu_colour, 
            'left_top', 
            x, 
            y,
        )
    
    def update(self):
        """
        Update the debug menu
        """
        self.draw()
        
    def handle_window_resize(self):
        pass
        