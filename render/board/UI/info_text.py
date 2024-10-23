from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_timing import StructTiming
from render.board.struct_board import StructBoardConsts
import pygame

class UIInfoText():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, TimingStruct:StructTiming, Fonts, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.TimingStruct = TimingStruct
        self.BoardConsts = BoardConsts
        self.Fonts = Fonts
        
        # TODO: create surfaces that you can choose to render different counters/timers/info onto
        # they will then be blitted onto the board surface in the correct position
        self.left_counter_slot_1 = None
        self.left_counter_slot_2 = None
        self.left_counter_slot_3 = None
        self.left_counter_slot_4 = None
        
        self.right_counter_slot_1 = None
    
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
        
        text_time_ms = self.Fonts.hun2_med.render(self.time_ms, True, (255, 255, 255))
        text_time_ms_rect = text_time_ms.get_rect()
        text_time_ms_position = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - text_time_ms_rect.width - self.RenderStruct.GRID_SIZE * 1.25, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT  - 3 * self.Fonts.hun2_med.get_height()//4)
        
        text_time_minsec = self.Fonts.hun2_big.render(f'{self.time_minsec}.', True, (255, 255, 255))
        text_time_minsec_rect = text_time_minsec.get_rect()
        text_time_minsec_position = (text_time_ms_position[0] - text_time_minsec_rect.width, text_time_ms_position[1] + text_time_ms_rect.height - text_time_minsec_rect.height)
        
        text_time = self.Fonts.hun2_med.render('TIME', True, (255, 255, 255))
        text_time_rect = text_time.get_rect()
        text_time_position = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - text_time_rect.width - self.RenderStruct.GRID_SIZE * 1.25, text_time_minsec_position[1] - text_time_rect.height * 1.05)
        
        surface.blit(text_time_ms, text_time_ms_position)
        surface.blit(text_time_minsec, text_time_minsec_position)
        surface.blit(text_time, text_time_position)
        
        pygame.draw.rect(surface, (255, 255, 255), (text_time_ms_position[0], text_time_ms_position[1], text_time_ms_rect.width, text_time_ms_rect.height), 1)
        pygame.draw.rect(surface, (255, 255, 255), (text_time_minsec_position[0], text_time_minsec_position[1], text_time_minsec_rect.width, text_time_minsec_rect.height), 1)
        pygame.draw.rect(surface, (255, 255, 255), (text_time_position[0], text_time_position[1], text_time_rect.width, text_time_rect.height), 1)
