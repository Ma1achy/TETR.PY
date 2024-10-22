from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from render.board.struct_board import StructBoardConsts
import pygame

class UIActionText():
    def __init__(self, GameInstanceStruct:StructGameInstance, RenderStruct:StructRender, FlagStruct:StructFlags, TimingStruct:StructTiming, Fonts, BoardConsts):
 
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.Fonts = Fonts
        self.BoardConsts = BoardConsts
        
    def draw(self, surface):
        self.draw_t_spin_action_text(surface)
        self.draw_line_clear_action_text(surface)
        self.draw_back_to_back_action_text(surface)
    
    def draw_t_spin_action_text(self, surface):
        surface.blit(self.Fonts.hun2_big.render('T-SPIN', True, (168, 34, 139)), (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.GRID_SIZE * 5 - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE * 4.4 + self.RenderStruct.BORDER_WIDTH))
        
    def draw_line_clear_action_text(self, surface):
        surface.blit(self.Fonts.hun2_bigger.render('DOUBLE', True, (255, 255, 255)), (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.GRID_SIZE * 7.25 - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE * 5.5 + self.RenderStruct.BORDER_WIDTH))
    
    def draw_back_to_back_action_text(self, surface):
        surface.blit(self.Fonts.hun2_med.render('B2B x2', True, (253, 220, 92)), (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.GRID_SIZE * 3.9 - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE * 7 + self.RenderStruct.BORDER_WIDTH))