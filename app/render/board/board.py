from app.state.config import Config
from old_state.struct_render import StructRender
from instance.state.flags import Flags
from instance.state.game_state import GameState
from old_state.struct_timing import StructTiming
from app.debug.debug_metrics import DebugMetrics
from render.board.struct_board import StructBoardConsts
import pygame
from render.board.matrix import Matrix
from render.board.hold_and_queue import HoldAndQueue
from render.board.UI.border import UIBorder
from render.board.UI.info_text import UIInfoText
from render.board.UI.action_text import UIActionText
from instance.handling.handling import Action
from app.utils import ease_out_cubic, ease_in_out_quad, smoothstep
from instance.engine.four import RNG
import math
 
class Board():
    def __init__(self, Config:Config, RenderStruct:StructRender, FlagStruct:Flags, GameInstanceStruct:GameState, TimingStruct:StructTiming, DebugStruct:DebugMetrics, Fonts):
            
        self.Config = Config
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.DebugStruct = DebugStruct
        self.BoardConsts = StructBoardConsts()
        self.Fonts = Fonts
        self.BoardConsts.draw_garbage_bar = True
        
        if self.BoardConsts.draw_garbage_bar:
            self.BoardConsts.GarbageWidth = self.RenderStruct.GRID_SIZE
        else:
            self.BoardConsts.GarbageWidth = 0
            
        if self.GameInstanceStruct.top_out_ok:
            self.BoardConsts.game_over_type =  'ZOOMOUT'
        else:
            self.BoardConsts.game_over_type = 'FALL'
        
        if self.GameInstanceStruct.reset_on_top_out:
            self.BoardConsts.game_over_type = 'FIZZLE'
        
        self.BoardConsts.MATRIX_SURFACE_WIDTH = self.GameInstanceStruct.matrix.WIDTH * self.RenderStruct.GRID_SIZE
        self.BoardConsts.MATRIX_SURFACE_HEIGHT = self.GameInstanceStruct.matrix.HEIGHT // 2 * self.RenderStruct.GRID_SIZE
        
        self.BoardConsts.board_rect_width = self.BoardConsts.MATRIX_SURFACE_WIDTH + 25 * self.RenderStruct.GRID_SIZE
        self.BoardConsts.board_rect_height = self.BoardConsts.MATRIX_SURFACE_HEIGHT * 2 + self.RenderStruct.BORDER_WIDTH + 4 * self.RenderStruct.GRID_SIZE
        
        self.BoardConsts.matrix_rect_pos_x = self.BoardConsts.board_rect_width // 2 - self.BoardConsts.MATRIX_SURFACE_WIDTH // 2 
        self.BoardConsts.matrix_rect_pos_y = self.BoardConsts.MATRIX_SURFACE_HEIGHT - self.RenderStruct.GRID_SIZE * 4 - self.RenderStruct.BORDER_WIDTH 
        
        self.BoardConsts.top_out_colour = (255, 0, 0)
        self.BoardConsts.board_glow_surface = self.get_board_surface()
        self.BoardConsts.matrix_line_glow_surface = self.get_board_surface()
        self.glow_alpha = 0
        self.RNG = RNG(seed = 0)
        
        self.Matrix = Matrix(RenderStruct, FlagStruct, GameInstanceStruct, TimingStruct, self.BoardConsts, self.RNG)
        self.UI_Border = UIBorder(RenderStruct, FlagStruct, GameInstanceStruct, Fonts, self.BoardConsts)
        self.HoldAndQueue = HoldAndQueue(RenderStruct, FlagStruct, GameInstanceStruct, self.BoardConsts)
        self.UI_InfoText = UIInfoText(RenderStruct, FlagStruct, GameInstanceStruct, TimingStruct,  Fonts, self.BoardConsts)
        self.UI_ActionText = UIActionText(GameInstanceStruct, RenderStruct, FlagStruct, TimingStruct, Fonts, self.BoardConsts)
        
        self.top_out_surface = pygame.Surface((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)
         
        self.top_out_surface_alpha = 0
        self.top_out_colour_bg = 255
        self.BoardConsts.top_out_colour = (255, self.top_out_colour_bg, self.top_out_colour_bg)
        self.BoardConsts.warning_cross_opacity = 0
        
        self.board_center_x_board_space = self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH // 2
        self.board_center_y_board_space = self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT // 2

        self.alpha = 255
        
        self.board_stifness = 1 # "spring constant" of board
        
        # base strength of the board animations
        self.spin_strength = 2048
        self.board_push_horizontal_strength = 100
        self.hard_drop_bounce_strength = 100
        self.board_push_down_strength = 100
        self.lock_delay_strength = 100
        
        self.angle = 0
        self.max_angle = 3 * 1/self.board_stifness
        self.spin_velocity = 0 
        self.spin_direction  = 0
        self.spin_in_progress = False
        
        self.default_scale = 1
        self.scale = 1
        
        self.offset_x, self.offset_y = 0, 0
        self.push_direction = 0
        self.horizontal_push = 0
        
        self.bounce_velocity = 0
        self.bounce_in_progress = False
        
        self.game_over_animation_in_progress = False
        self.fall_y_vel = 0
        self.gravity = 300 * self.RenderStruct.GRID_SIZE
        self.fall_rot_vel = 0
        self.shake_time = 0.5
        self.done_fizzle = False
        
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
        self.__draw_matrix_grid_glow(surface)

        self.HoldAndQueue.draw(surface)
        self.UI_ActionText.draw(surface)
        self.Matrix.draw(surface)
        self.UI_InfoText.draw(surface)
        
        self.__draw_board_glow(surface)
        self.__draw_hold_text(surface)
        self.__draw_queue_text(surface)
        
        self.__do_animations()
        
        if self.RenderStruct.draw_guide_lines:
            pygame.draw.rect(surface, (0, 0, 255), (0, 0, self.BoardConsts.board_rect_width, self.BoardConsts.board_rect_height), 1)
            pygame.draw.circle(surface, (255, 0, 0), (self.board_center_x_board_space, self.board_center_y_board_space), 5)
    
    def __do_animations(self):
        self.__board_spin_animation()
        self.__board_push_horizontal_animation()
        self.__board_push_down_animation()
        self.__harddrop_bounce_animation()
        self.__board_scale_push_in_animation()
        self.__game_over_animation()
        self.__top_out_darken_animation()
        
    def __draw_matrix_grid_glow(self, surface):
        if self.alpha > 0:
            self.BoardConsts.matrix_line_glow_surface.set_alpha(self.glow_alpha//2)
            surface.blit(self.BoardConsts.matrix_line_glow_surface, (0, 0))
    
    def __draw_board_glow(self, surface):
        if self.glow_alpha > 0:
            self.BoardConsts.board_glow_surface.set_alpha(self.glow_alpha)
            surface.blit(self.BoardConsts.board_glow_surface, (0, 0))
              
    def __do_board_spin(self):
        self.spin_in_progress = True
        self.FlagStruct.SPIN_ANIMATION = False
            
    def __board_spin_animation(self):
        
        if self.game_over_animation_in_progress:
            return
        
        spin_speed = self.spin_strength * 1 / self.board_stifness * self.dt 
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
                
    def __board_push_horizontal_animation(self):
        
        k = 10 * self.board_stifness
        dir = 0
        f = self.board_push_horizontal_strength
        
        if self.game_over_animation_in_progress:
            return
        
        if self.FlagStruct.PUSH_HORIZONTAL:
            dir = self.FlagStruct.PUSH_HORIZONTAL.x
            self.push_direction = dir
            self.horizontal_push = dir * f
        else:
            self.push_direction = 0
            self.horizontal_push = 0
        
        s = self.horizontal_push/k * self.default_scale
        self.offset_x = ease_out_cubic(self.offset_x, s, self.dt)
        
        if abs(self.offset_x) < self.RenderStruct.GRID_SIZE * 1E-9 * self.default_scale:
            self.offset_x = 0
   
    def __board_push_down_animation(self):
        
        if self.bounce_in_progress:
            return
        
        k = 10 * self.board_stifness
        dir = 0
        f = self.board_push_down_strength
        
        if self.FlagStruct.PUSH_VERTICAL:
            dir = self.FlagStruct.PUSH_VERTICAL.y
            self.push_direction = dir
            self.vertical_push = dir * f
        else:
            self.push_direction = 0
            self.vertical_push = 0
        
        s = self.vertical_push/k * self.default_scale
        self.offset_y = ease_out_cubic(self.offset_y, s, self.dt)
        
        if abs(self.offset_y) < self.RenderStruct.GRID_SIZE * 1E-9 * self.default_scale:
            self.offset_y = 0
    
    def __harddrop_bounce_animation(self):
        
        if self.FlagStruct.PUSH_VERTICAL:
            return
               
        if self.FlagStruct.HARD_DROP_BOUNCE:
            self.__do_bounce()
        
        self.__update_bounce()
            
    def __do_bounce(self):
        self.bounce_in_progress = True
        self.FlagStruct.HARD_DROP_BOUNCE = False
        
    def __update_bounce(self):
        
        k = 10 * self.board_stifness
        f = self.hard_drop_bounce_strength
        s = f/k * self.default_scale

        if not self.bounce_in_progress and self.offset_y == 0:
            return
        
        elif not self.bounce_in_progress and self.offset_y != 0:
            if abs(self.offset_y) < 0.001 * self.default_scale:
                self.bounce_velocity = 0
                self.offset_y = 0
                return
            else:
                self.offset_y = ease_out_cubic(self.offset_y, -self.offset_y, self.dt)
            pass
        else:
            self.offset_y = ease_out_cubic(self.offset_y, s * 4, self.dt)
            
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
        scale = min(self.default_scale, self.default_scale - max(0, min(0.000333 * self.lock_delay_strength/self.board_stifness * self.default_scale, smooth_progress)))
        return scale
    
    def __board_scale_push_in_animation(self):
        
        self.__do_lock_delay_animation()
        self.__update_lock_delay_animation()
        
    def __do_lock_delay_animation(self):
        self.lock_delay_scale_in_progress = True  
        
    def __update_lock_delay_animation(self):
        
        if self.game_over_animation_in_progress:
            return
        
        if self.GameInstanceStruct.current_tetromino is None or not self.GameInstanceStruct.is_on_floor:
            self.lock_delay_scale_in_progress = False
                
        if not self.lock_delay_scale_in_progress and self.scale == self.default_scale:
            return
        
        if not self.lock_delay_scale_in_progress and self.scale != self.default_scale:
            self.scale = ease_out_cubic(self.scale, self.default_scale, self.dt)

            if abs(self.scale - self.default_scale) < 0.001:
                self.scale = self.default_scale
        else:
            if self.__placement_will_gameover(): # if the placement will cause a game over, scale up instead
                self.scale = ease_out_cubic(self.scale, self.__lock_delay_to_scale() * 1.06, self.dt)

                if self.scale > 1.05 * self.default_scale:
                    self.lock_delay_scale_in_progress = False
                    self.scale = ease_out_cubic(self.scale, self.default_scale, self.dt)
            else:
                self.scale = ease_out_cubic(self.scale, self.__lock_delay_to_scale(), self.dt)
                
                if self.scale < 0.98 * self.default_scale:
                    self.lock_delay_scale_in_progress = False
                    self.scale = ease_out_cubic(self.scale, self.default_scale, self.dt)
                
    def __game_over_animation(self):
        
        if self.FlagStruct.GAME_OVER and not self.game_over_animation_in_progress:
            self.__do_game_over_animation()
    
        self.__update_game_over_animation()
        
    def __do_game_over_animation(self):
        self.game_over_animation_in_progress = True
        self.f = self.RNG.next_float()

    def __do_shake(self):
        if self.shake_time <= 0:
            return

        self.scale = self.default_scale
        self.shake_time -= self.dt
        
        amplitude = self.shake_time * self.RenderStruct.GRID_SIZE * 3 * self.default_scale 
        frequency = 64 

        self.offset_x = amplitude * math.sin(self.shake_time * frequency) * (0.5 + self.RNG.next_float() * 0.5)
        self.offset_y = amplitude * math.sin(self.shake_time * frequency * 1.5) * (0.5 + self.RNG.next_float() * 0.5)
        
    def __update_game_over_animation(self):
        
        if not self.game_over_animation_in_progress:
            return
        
        if self.shake_time > 0:
            self.__do_shake()
            return
            
        if self.BoardConsts.game_over_type == 'FALL':

            if self.f < 0.5:
                dir = 1
            else:
                dir = -1
                
            self.angle = ease_in_out_quad(self.angle, dir * 720, self.dt)
           
            self.fall_y_vel += self.gravity * self.dt 
            self.offset_y += self.fall_y_vel * self.dt
            
            if (self.offset_y - self.BoardConsts.MATRIX_SURFACE_HEIGHT * 3 * self.default_scale) > self.RenderStruct.WINDOW_HEIGHT:
                self.game_over_animation_in_progress = False
                self.angle = 0 
        
        elif self.BoardConsts.game_over_type == 'ZOOMOUT':
            
            self.scale = ease_out_cubic(self.scale, self.scale * 0.97, self.dt)
                
            if self.scale < self.default_scale * 0.6:
                self.alpha = ease_out_cubic(self.alpha, 0, self.dt)
                
                if self.alpha <= 1:
                    self.game_over_animation_in_progress = False
                    self.alpha = 0
        
        elif self.BoardConsts.game_over_type == 'FIZZLE':
            
            if not self.done_fizzle:
                self.Matrix.do_fizzle_game_over = True
                self.done_fizzle = True
            
            if not self.Matrix.do_fizzle_game_over:
                self.shake_time = 0.5
                self.game_over_animation_in_progress = False
                self.Matrix.do_fizzle_game_over = False
                self.done_fizzle = False
                self.GameInstanceStruct.reset = True # after animation is done allow the game to reset
        
    def __top_out_darken_animation(self):
        
        self.top_out_surface.fill((0, 0, 0, self.top_out_surface_alpha))
        self.__update_top_out_darken()
        
    def __update_top_out_darken(self):
        
        if self.__placement_will_gameover():
            self.top_out_surface_alpha = ease_out_cubic(self.top_out_surface_alpha, 255, self.dt)
            self.top_out_colour_bg = ease_out_cubic(self.top_out_colour_bg, 0, self.dt)
            self.BoardConsts.top_out_colour = (255, self.top_out_colour_bg, self.top_out_colour_bg)
            self.BoardConsts.warning_cross_opacity = ease_out_cubic(self.BoardConsts.warning_cross_opacity, 512, self.dt)
            self.glow_alpha = ease_out_cubic(self.glow_alpha, 270, self.dt)
            
        if self.FlagStruct.DANGER:
            self.top_out_surface_alpha = ease_out_cubic(self.top_out_surface_alpha, 180, self.dt)
            self.top_out_colour_bg = ease_out_cubic(self.top_out_colour_bg, 0, self.dt)
            self.BoardConsts.top_out_colour = (255, self.top_out_colour_bg, self.top_out_colour_bg)
            self.BoardConsts.warning_cross_opacity = ease_out_cubic(self.BoardConsts.warning_cross_opacity, 200, self.dt)
            self.glow_alpha = ease_out_cubic(self.glow_alpha, 128, self.dt)

        else:
            self.top_out_surface_alpha = ease_out_cubic(self.top_out_surface_alpha, 0, self.dt)
            self.top_out_colour_bg = ease_out_cubic(self.top_out_colour_bg, 255, self.dt)
            self.BoardConsts.top_out_colour = (255, self.top_out_colour_bg, self.top_out_colour_bg)
            self.BoardConsts.warning_cross_opacity = ease_out_cubic(self.BoardConsts.warning_cross_opacity, 0, self.dt)
            self.glow_alpha = ease_out_cubic(self.glow_alpha, 0, self.dt)
             
            if self.glow_alpha < 1:
                self.glow_alpha = 0
    
    def __placement_will_gameover(self):
       
        if self.GameInstanceStruct.current_tetromino is None:
            return False
         
        if self.GameInstanceStruct.is_in_buffer_zone or self.GameInstanceStruct.is_in_spawn_overlap:
            return True  
        else:
            return False 
                  
    def __draw_hold_text(self, surface):
        if not self.GameInstanceStruct.hold:  
            return
        
        text = self.Fonts.hun2_big.render('NEXT', True, (0, 0, 0))
        surface.blit(text, (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE * 0.15))
                
    def __draw_queue_text(self, surface):
        if not self.GameInstanceStruct.queue_previews > 0:
            return
        
        if self.BoardConsts.draw_garbage_bar:
            start = 7
        else:
            start = 6
        text = self.Fonts.hun2_big.render('HOLD', True, (0, 0, 0))
        surface.blit(text, (self.BoardConsts.matrix_rect_pos_x  - (start + 0.25) * self.RenderStruct.GRID_SIZE + self.RenderStruct.GRID_SIZE * 0.25, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE * 0.15))
        
        
        
        
        
            
 
                
    