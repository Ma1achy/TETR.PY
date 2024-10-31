from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from render.board.struct_board import StructBoardConsts
import pygame
from render.board.matrix import Matrix
from render.board.hold_and_queue import HoldAndQueue
from render.board.UI.border import UIBorder
from render.board.UI.info_text import UIInfoText
from render.board.UI.action_text import UIActionText

class Board():
    def __init__(self, Config:StructConfig, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, TimingStruct:StructTiming, DebugStruct:StructDebug, Fonts):
            
        self.Config = Config
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.DebugStruct = DebugStruct
        self.BoardConsts = StructBoardConsts()
        
        self.BoardConsts.draw_garbage_bar = False
        
        self.BoardConsts.MATRIX_SURFACE_WIDTH = self.GameInstanceStruct.matrix.WIDTH * self.RenderStruct.GRID_SIZE
        self.BoardConsts.MATRIX_SURFACE_HEIGHT = self.GameInstanceStruct.matrix.HEIGHT // 2 * self.RenderStruct.GRID_SIZE
        
        self.BoardConsts.board_rect_width = self.BoardConsts.MATRIX_SURFACE_WIDTH + 25 * self.RenderStruct.GRID_SIZE
        self.BoardConsts.board_rect_height = self.BoardConsts.MATRIX_SURFACE_HEIGHT * 2 + self.RenderStruct.BORDER_WIDTH + 4 * self.RenderStruct.GRID_SIZE
        
        self.BoardConsts.matrix_rect_pos_x = self.BoardConsts.board_rect_width // 2 - self.BoardConsts.MATRIX_SURFACE_WIDTH // 2 
        self.BoardConsts.matrix_rect_pos_y = self.BoardConsts.MATRIX_SURFACE_HEIGHT - self.RenderStruct.GRID_SIZE * 4 - self.RenderStruct.BORDER_WIDTH 
        
        self.Matrix = Matrix(RenderStruct, FlagStruct, GameInstanceStruct, TimingStruct, self.BoardConsts)
        self.HoldAndQueue = HoldAndQueue(RenderStruct, FlagStruct, GameInstanceStruct, self.BoardConsts)
        self.UI_Border = UIBorder(RenderStruct, FlagStruct, GameInstanceStruct, Fonts, self.BoardConsts)
        self.UI_InfoText = UIInfoText(RenderStruct, FlagStruct, GameInstanceStruct, TimingStruct,  Fonts, self.BoardConsts)
        self.UI_ActionText = UIActionText(GameInstanceStruct, RenderStruct, FlagStruct, TimingStruct, Fonts, self.BoardConsts)
        
        self.board_center_x_board_space = self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH // 2
        self.board_center_y_board_space = self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT // 2
    
    def get_board_surface(self):
        """
        Get the surface to draw the board onto
        """
        return pygame.Surface((self.BoardConsts.board_rect_width, self.BoardConsts.board_rect_height), pygame.SRCALPHA|pygame.HWSURFACE)
    
    def draw(self, surface):
        """
        Draw the board onto a surface
        """
        self.UI_Border.draw(surface) 
        self.HoldAndQueue.draw(surface)
        self.UI_ActionText.draw(surface)
        self.Matrix.draw(surface)
       # pygame.draw.rect(surface, (0, 0, 255), (0, 0, self.BoardConsts.board_rect_width, self.BoardConsts.board_rect_height), 1)
       # pygame.draw.circle(surface, (255, 0, 0), (self.board_center_x_board_space, self.board_center_y_board_space), 5)
        self.UI_InfoText.draw(surface)
       