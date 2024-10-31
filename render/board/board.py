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
from core.handling import Action
from utils import ease_out_cubic, ease_in_out_quad 

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

        self.angle = 0
        self.max_angle = 3
        self.spin_velocity = 0 
        self.spin_in_progress = False
        
        self.scale = 1
        
        self.offset_x, self.offset_y = 0, 0
        
    def get_board_surface(self):
        """
        Get the surface to draw the board onto
        """
        return pygame.Surface((self.BoardConsts.board_rect_width, self.BoardConsts.board_rect_height), pygame.SRCALPHA|pygame.HWSURFACE)
    
    def draw(self, surface):
        """
        Draw the board onto a surface
        """
        if self.TimingStruct.FPS == 0:
            self.dt = 1
        else:
            self.dt = 1 / self.TimingStruct.FPS
        
        self.UI_Border.draw(surface) 
        self.HoldAndQueue.draw(surface)
        self.UI_ActionText.draw(surface)
        self.Matrix.draw(surface)
       # pygame.draw.rect(surface, (0, 0, 255), (0, 0, self.BoardConsts.board_rect_width, self.BoardConsts.board_rect_height), 1)
       # pygame.draw.circle(surface, (255, 0, 0), (self.board_center_x_board_space, self.board_center_y_board_space), 5)
        self.UI_InfoText.draw(surface)
        
        self.board_spin_animation()
        
    def __do_board_spin(self):
        self.spin_in_progress = True
        self.FlagStruct.SPIN_ANIMATION = False
            
    def board_spin_animation(self):
        
        spin_speed = 2048 * self.dt
        max_speed = spin_speed
        
        if abs(self.spin_velocity) >= max_speed:
            self.spin_velocity = self.spin_velocity / abs(self.spin_velocity) * max_speed
               
        if self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_CLOCKWISE:
            if self.spin_velocity > 0:
                self.spin_velocity = 0
            self.spin_velocity += - spin_speed 
        
        elif self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_COUNTERCLOCKWISE:
            if self.spin_velocity < 0:
                self.spin_velocity = 0
            self.spin_velocity += spin_speed 
            
        elif self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_180:
            if self.spin_velocity > 0:
                self.spin_velocity = 0
            self.spin_velocity += - spin_speed 
            
        if self.FlagStruct.SPIN_ANIMATION:
            self.__do_board_spin()
            
        self.__update_board_spin()
             
    def __update_board_spin(self):
        
        if not self.spin_in_progress and self.angle == 0:
            return
        
        elif not self.spin_in_progress and self.angle != 0:
            if abs(self.angle) < 0.01:
                self.angle = 0
                return
            else:
                self.angle = ease_out_cubic(self.angle, -self.angle, self.dt)
        else:
            self.angle = ease_in_out_quad(self.angle, self.spin_velocity * 90, self.dt)

            if abs(self.angle) >= self.max_angle:
                self.spin_in_progress = False
                self.angle = max(min(self.angle, self.max_angle), -self.max_angle)
       