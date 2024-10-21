from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_timing import StructTiming
from render.board.struct_board import StructBoardConsts

class UIInfoText():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, TimingStruct:StructTiming, Fonts, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.TimingStruct = TimingStruct
        self.BoardConsts = BoardConsts
        self.Fonts = Fonts
    
    def draw(self, surface):
        """
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.__draw_timer(surface)
    
    def __format_time(self):
        """
        Format the time in seconds into the format 'mm:ss' and 'ms'
        
        returns:
            time_minsec (str): the time in the format 'mm:ss'
            time_ms (str): the time in milliseconds
        """
        minutes = int((self.TimingStruct.current_time % 3600) // 60)
        seconds = int(self.TimingStruct.current_time % 60)
        milliseconds = int((self.TimingStruct.current_time % 1) * 1000)
        time_minsec = f"{minutes}:{seconds:02}"
        time_ms = f"{milliseconds:03}"
        return time_minsec, time_ms
    
    def __draw_timer(self, surface): 
        """
        Draw the timer
        
        args:
            surface (pygame.Surface): The surface to draw
        """
        if not self.FlagStruct.GAME_OVER:
            self.time_minsec, self.time_ms = self.__format_time()
            
        surface.blit(self.Fonts.hun2_med.render('Time', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE * 5.33, self.RenderStruct.GRID_SIZE * 22.33 + self.BoardConsts.MATRIX_SURFACE_HEIGHT))
        surface.blit(self.Fonts.hun2_big.render(f'{self.time_minsec}.', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE * 5.5 - (len(self.time_minsec) * self.RenderStruct.GRID_SIZE//2 + 1), self.RenderStruct.GRID_SIZE * 23.25 + self.BoardConsts.MATRIX_SURFACE_HEIGHT))
        surface.blit(self.Fonts.hun2_med.render(f'{self.time_ms}', True, (255, 255, 255)), (self.RenderStruct.GRID_SIZE * 5.66, self.RenderStruct.GRID_SIZE * 23.45 + self.BoardConsts.MATRIX_SURFACE_HEIGHT))