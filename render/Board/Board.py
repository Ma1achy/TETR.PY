from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from render.Board.BoardConsts import StructBoardConsts
import pygame
from render.Board.Matrix import Matrix
from render.Board.HoldAndQueue import HoldAndQueue
from render.Board.UI.Border import UIBorder
from render.Board.UI.InfoText import UIInfoText

class Board():
    def __init__(self, Config:StructConfig, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, TimingStruct:StructTiming, DebugStruct:StructDebug, Fonts):
            
        self.Config = Config
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.DebugStruct = DebugStruct
        self.BoardConts = StructBoardConsts()
        
        self.BoardConts.MATRIX_SURFACE_WIDTH = self.GameInstanceStruct.matrix.WIDTH * self.RenderStruct.GRID_SIZE
        self.BoardConts.MATRIX_SURFACE_HEIGHT = self.GameInstanceStruct.matrix.HEIGHT // 2 * self.RenderStruct.GRID_SIZE
        
        self.BoardConts.board_rect_width = self.BoardConts.MATRIX_SURFACE_WIDTH + 17 * self.RenderStruct.GRID_SIZE
        self.BoardConts.board_rect_height = self.BoardConts.MATRIX_SURFACE_HEIGHT * 2 + self.RenderStruct.BORDER_WIDTH + 4 * self.RenderStruct.GRID_SIZE
        
        self.BoardConts.matrix_rect_pos_x = self.BoardConts.board_rect_width // 2 - self.BoardConts.MATRIX_SURFACE_WIDTH // 2 
        self.BoardConts.matrix_rect_pos_y = self.BoardConts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.GRID_SIZE * 4 + self.RenderStruct.BORDER_WIDTH // 2
        
        self.Matrix = Matrix(self.Config, self.RenderStruct, self.FlagStruct, self.GameInstanceStruct, self.BoardConts)
        self.HoldAndQueue = HoldAndQueue(Config, RenderStruct, FlagStruct, GameInstanceStruct, self.BoardConts)
        self.UI_Border = UIBorder(Config, RenderStruct, FlagStruct, Fonts, self.BoardConts)
        self.UI_InfoText = UIInfoText(RenderStruct, FlagStruct, TimingStruct, self.BoardConts, Fonts)
        
        self.board_center_x_board_space = self.BoardConts.board_rect_width // 2
        self.board_center_y_board_space = self.BoardConts.board_rect_height // 2 + 2 * self.RenderStruct.GRID_SIZE + self.BoardConts.MATRIX_SURFACE_HEIGHT // 2
    
    def GetBoardSurface(self):
        return pygame.Surface((self.BoardConts.board_rect_width, self.BoardConts.board_rect_height), pygame.SRCALPHA)
    
    def Draw(self, surface):
        self.Matrix.Draw(surface)
        pygame.draw.rect(surface, (0, 0, 255), (0, 0, self.BoardConts.board_rect_width, self.BoardConts.board_rect_height), 1)
        self.HoldAndQueue.Draw(surface)
        self.UI_Border.Draw(surface) 
        self.UI_InfoText.Draw(surface)