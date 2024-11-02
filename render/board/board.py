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
from utils import ease_out_cubic, ease_in_out_quad, smoothstep
from instance.four import RNG

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
        
        self.RNG = RNG(seed = 0)
        
        self.Matrix = Matrix(RenderStruct, FlagStruct, GameInstanceStruct, TimingStruct, self.BoardConsts, self.RNG)
        self.HoldAndQueue = HoldAndQueue(RenderStruct, FlagStruct, GameInstanceStruct, self.BoardConsts)
        self.UI_Border = UIBorder(RenderStruct, FlagStruct, GameInstanceStruct, Fonts, self.BoardConsts)
        self.UI_InfoText = UIInfoText(RenderStruct, FlagStruct, GameInstanceStruct, TimingStruct,  Fonts, self.BoardConsts)
        self.UI_ActionText = UIActionText(GameInstanceStruct, RenderStruct, FlagStruct, TimingStruct, Fonts, self.BoardConsts)
        
        self.board_center_x_board_space = self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH // 2
        self.board_center_y_board_space = self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT // 2

        self.board_stifness = 1
        
        self.angle = 0
        self.max_angle = 3 * 1/self.board_stifness
        self.spin_velocity = 0 
        self.spin_direction  = 0
        self.spin_in_progress = False
        
        self.scale = 1
        
        self.offset_x, self.offset_y = 0, 0
        self.push_direction = 0
        self.horizontal_push = 0
        
        self.bounce_velocity = 0
        self.bounce_in_progress = False
        
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
        self.UI_InfoText.draw(surface)
        
        self.board_spin_animation()
        self.board_push_horizontal_animation()
        self.board_push_down_animation()
        self.harddrop_bounce_animation()
        self.board_scale_push_in_animation()
        
        if self.RenderStruct.draw_guide_lines:
            pygame.draw.rect(surface, (0, 0, 255), (0, 0, self.BoardConsts.board_rect_width, self.BoardConsts.board_rect_height), 1)
            pygame.draw.circle(surface, (255, 0, 0), (self.board_center_x_board_space, self.board_center_y_board_space), 5)
        
    def __do_board_spin(self):
        self.spin_in_progress = True
        self.FlagStruct.SPIN_ANIMATION = False
            
    def board_spin_animation(self):
        
        spin_speed = 2048 * 1 / self.board_stifness * self.dt 
        max_speed = spin_speed
        
        if abs(self.spin_velocity) >= max_speed:
            self.spin_velocity = self.spin_velocity / abs(self.spin_velocity) * max_speed
               
        if self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_CLOCKWISE:
            self.spin_direction = - 1
            self.spin_velocity += spin_speed * self.spin_direction
            
        elif self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_COUNTERCLOCKWISE:        
            self.spin_direction = 1
            self.spin_velocity += spin_speed * self.spin_direction
            
        elif self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_180: 
            if not self.spin_in_progress:       
                f = self.RNG.next_float()
                if f < 0.5:
                    self.spin_direction = -1
                else:
                    self.spin_direction = 1

            self.spin_velocity += spin_speed * self.spin_direction
        
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
                
    def board_push_horizontal_animation(self):
        
        k = 10 * self.board_stifness
        dir = 0
        f = 100
       
        if self.FlagStruct.PUSH_HORIZONTAL:
            dir = self.FlagStruct.PUSH_HORIZONTAL.x
            self.push_direction = dir
            self.horizontal_push = dir * f
        else:
            self.push_direction = 0
            self.horizontal_push = 0
        
        s = self.horizontal_push/k
        self.offset_x = ease_out_cubic(self.offset_x, s, self.dt)
        
        if abs(self.offset_x) < self.RenderStruct.GRID_SIZE * 1E-9:
            self.offset_x = 0
   
    def board_push_down_animation(self):
        
        if self.bounce_in_progress:
            return
        
        k = 10 * self.board_stifness
        dir = 0
        f = 100
        
        if self.FlagStruct.PUSH_VERTICAL:
            dir = self.FlagStruct.PUSH_VERTICAL.y
            self.push_direction = dir
            self.vertical_push = dir * f
        else:
            self.push_direction = 0
            self.vertical_push = 0
        
        s = self.vertical_push/k
        self.offset_y = ease_out_cubic(self.offset_y, s, self.dt)
        
        if abs(self.offset_y) < self.RenderStruct.GRID_SIZE * 1E-9:
            self.offset_y = 0
    
    def harddrop_bounce_animation(self):
        
        if self.FlagStruct.PUSH_VERTICAL:
            return
        
        bounce_speed = 2048 * self.dt
        max_speed = bounce_speed
        
        if abs(self.bounce_velocity) >= max_speed * 1.5:
            self.bounce_velocity = self.bounce_velocity / abs(self.bounce_velocity) * max_speed    
        
        self.bounce_velocity += bounce_speed 
        
        if self.FlagStruct.HARD_DROP_BOUNCE:
            self.__do_bounce()
        
        self.__update_bounce()
            
    def __do_bounce(self):
        self.bounce_in_progress = True
        self.FlagStruct.HARD_DROP_BOUNCE = False
        
    def __update_bounce(self):
        
        k = 10 * self.board_stifness
        dir = 1
        f = self.bounce_velocity * dir * 4
        s = f/k

        if not self.bounce_in_progress and self.offset_y == 0:
            return
        
        elif not self.bounce_in_progress and self.offset_y != 0:
            if abs(self.offset_y) < 0.001:
                self.bounce_velocity = 0
                self.offset_y = 0
                return
            else:
                self.offset_y = ease_out_cubic(self.offset_y, -self.offset_y, self.dt)
            pass
        else:
            self.offset_y = ease_out_cubic(self.offset_y, s, self.dt * s)
            
            if self.offset_y >= s:
                self.bounce_in_progress = False
                        
    def __lock_delay_to_scale(self):
        """
        Convert the lock delay to a scale factor
        """
        if self.GameInstanceStruct.lock_delay_in_ticks == 0 or self.GameInstanceStruct.lock_delay_in_ticks == 'inf':
            return 1
        
        progress = self.GameInstanceStruct.current_tetromino.lock_delay_counter / self.GameInstanceStruct.lock_delay_in_ticks
        smooth_progress = smoothstep(progress)
        scale = min(1, 1 - max(0, min(0.0333 * 1/self.board_stifness, smooth_progress)))
        return scale
    
    def board_scale_push_in_animation(self):
    
        if self.GameInstanceStruct.current_tetromino.is_on_floor():
            self.__do_lock_delay_animation()
            
        self.__update_lock_delay_animation()
        
    def __do_lock_delay_animation(self):
        self.lock_delay_scale_in_progress = True  
        
    def __update_lock_delay_animation(self):
        
        if self.GameInstanceStruct.current_tetromino is None or not self.GameInstanceStruct.current_tetromino.is_on_floor():
            self.lock_delay_scale_in_progress = False
                
        if not self.lock_delay_scale_in_progress and self.scale == 1:
            return
        
        if not self.lock_delay_scale_in_progress and self.scale != 1:
            self.scale = ease_out_cubic(self.scale, 1, self.dt)
     
            if self.scale > 0.999:
                self.scale = 1
                return
        
        else:
            self.scale = ease_out_cubic(self.scale, self.__lock_delay_to_scale(), self.dt)
            
            if self.scale < 0.98:
                self.lock_delay_scale_in_progress = False
                self.scale = ease_out_cubic(self.scale, 1, self.dt)

            
            
           
        