import pygame.gfxdraw
import pygame, math
import numpy as np
from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from utils import lerpBlendRGBA, get_tetromino_blocks, get_prefix, smoothstep, TransformSurface, RotateSurface, ScaleSurface, ease
from core.handling import Action
from render.UI.debug_menu import UIDebug
from render.UI.key_states_overlay import UIKeyStates
from render.board.board import Board
from render.fonts import Fonts

class Render():
    def __init__(self, Config:StructConfig, RenderStruct:StructRender, Flags:StructFlags, GameInstanceStruct:StructGameInstance, TimingStruct:StructTiming, DebugStruct:StructDebug):  
        """
        Render an instance of four onto a window
        
        args:
            self.window (pygame.Surface): the window to render the game onto
        """
        
        self.Config = Config
        self.RenderStruct = RenderStruct
        self.FlagStruct = Flags
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.DebugStruct = DebugStruct
        
        self.RenderStruct.TEXTURE_ATLAS = pygame.image.load('render/textures.png')
        self.RenderStruct.TEXTURES_PER_ROW = 5
        self.RenderStruct.TEXTURES_PER_COLUMN = 5
      
        self.RenderStruct.use_textures = True
        self.RenderStruct.coloured_shadow = True
        self.RenderStruct.shadow_opacity = 200
        
        self.angle = 0
        self.max_angle = 3
    
        self.board_center_screen_pos_x = self.RenderStruct.WINDOW_WIDTH // 2 
        self.board_center_screen_pos_y = self.RenderStruct.WINDOW_HEIGHT // 2
      
        self.window = self.__init_window()
        self.Fonts = Fonts(self.RenderStruct)
        
        self.Board = Board(self.Config, self.RenderStruct, self.FlagStruct, self.GameInstanceStruct, self.TimingStruct, self.DebugStruct, self.Fonts)
        self.UI_Debug = UIDebug(self.Config, self.RenderStruct, self.DebugStruct, self.FlagStruct, self.Fonts)
        self.UI_KeyStates = UIKeyStates(self.RenderStruct, self.Fonts)
        self.board_surface = self.Board.get_board_surface()
        
        self.image_path = 'render/image.jpg'
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.smoothscale(self.image, (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT))
        
        self.spin_direction = 0 
        self.spin_in_progress = False
        
    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_caption(self.RenderStruct.CAPTION)
        return pygame.display.set_mode((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
     
    def draw_frame(self):
        """
        Render the frame of the Four Instance
        """
        self.dt = self.TimingStruct.delta_frame_time / 1000
        
        self.board_spin_animation()
        
        self.window.fill((255, 0, 255))
        self.board_surface.fill((0, 0, 0, 0))
        self.window.blit(self.image, (0, 0))
        
        
        self.Board.draw(self.board_surface)
        
        offset_x, offset_y = 0, 0
        scale = 1
        
        transformed_surface, transformed_rect = TransformSurface(self.board_surface, scale, self.angle, pygame.Vector2(self.Board.board_center_x_board_space, self.Board.board_center_y_board_space), pygame.Vector2(self.board_center_screen_pos_x, self.board_center_screen_pos_y), pygame.Vector2(offset_x, offset_y))
        self.window.blit(transformed_surface, transformed_rect.topleft)
    
        # self.angle = 0
        # offset_x, offset_y = 0, 0
        # scale = 1
    
        # transformed_surface, transformed_rect = TransformSurface(self.board_surface, scale, self.angle, (self.board_center_x_board_space, self.board_center_y_board_space), (self.board_center_screen_pos_x, self.board_center_screen_pos_y), (offset_x, offset_y))
        # self.RenderStruct.surfaces.append((transformed_surface, transformed_rect.topleft))
    
        # for surface, coords in self.RenderStruct.surfaces:
        #     self.window.blit(surface, coords)
        
        # if self.RenderStruct.draw_guide_lines:
        #     pygame.draw.line(self.window, (255, 0, 255), (self.RenderStruct.WINDOW_WIDTH // 2, 0), (self.RenderStruct.WINDOW_WIDTH // 2, self.RenderStruct.WINDOW_HEIGHT), 1)
        #     pygame.draw.line(self.window, (255, 0, 255), (0, self.RenderStruct.WINDOW_HEIGHT // 2), (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT // 2), 1)
        #     pygame.draw.line(self.window, (0, 255, 0), (self.RenderStruct.WINDOW_WIDTH // 4, 0), (self.RenderStruct.WINDOW_WIDTH // 4, self.RenderStruct.WINDOW_HEIGHT), 1)
        #     pygame.draw.line(self.window, (0, 255, 0), (0, self.RenderStruct.WINDOW_HEIGHT // 4), (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT // 4), 1)
        #     pygame.draw.line(self.window, (0, 255, 0), (self.RenderStruct.WINDOW_WIDTH // 4 * 3, 0), (self.RenderStruct.WINDOW_WIDTH // 4 * 3, self.RenderStruct.WINDOW_HEIGHT), 1)
        #     pygame.draw.line(self.window, (0, 255, 0), (0, self.RenderStruct.WINDOW_HEIGHT // 4 * 3), (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT // 4 * 3), 1)
    
        self.UI_Debug.draw(self.window)
        self.UI_KeyStates.draw(self.window)
        
        pygame.display.update()
        
    def board_spin_animation(self):
        """
        Animate the board spinning
        """
        
        if abs(self.spin_direction) >= 256:
            self.spin_direction = self.spin_direction / abs(self.spin_direction)
            
        if self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_CLOCKWISE:
            if self.spin_direction > 0:
                self.spin_direction = 0
            self.spin_direction += - 20000 * self.dt
        
        elif self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_COUNTERCLOCKWISE:
            if self.spin_direction < 0:
                self.spin_direction = 0
            self.spin_direction += 20000 * self.dt
            
        elif self.FlagStruct.SPIN_DIRECTION == Action.ROTATE_180:
            if self.spin_direction > 0:
                self.spin_direction = 0
            self.spin_direction += - 20000 * self.dt
            
        if self.FlagStruct.SPIN_ANIMATION:
            self.__do_board_spin()
            
        self.__update_board_spin()

    def __do_board_spin(self):
        self.spin_in_progress = True
        self.FlagStruct.SPIN_ANIMATION = False
            
    def __update_board_spin(self):
        
        reset_threshold = 0.1
        
        if not self.spin_in_progress and self.angle == 0:
            self.angle = 0
            self.spin_direction = 0
            self.FlagStruct.SPIN_COUNT = 0
            return
        
        elif not self.spin_in_progress:
            if abs(self.angle) < reset_threshold:
                self.angle = 0
                return
            else:
                self.angle = ease_out_cubic(self.angle, -self.angle, self.dt * 4.5)
        else:
            self.angle = ease_in_out_quad(self.angle, self.angle + self.spin_direction * 90, self.dt * 3.5)

            if abs(self.angle) >= self.max_angle:
                self.spin_in_progress = False
                self.angle = max(min(self.angle, self.max_angle), -self.max_angle)
        
def ease_in_out_quad(start, end, t):
    change = end - start
    if t < 0.5:
        return start + change * (2 * t ** 2)
    else:
        return start + change * (-1 + (4 - 2 * t) * t)
    
def ease_out_cubic(start, end, t):
    change = end - start
    t -= 1
    return start + change * (t ** 3 + 1) 

def lerp(current, target, t):
    return current + (target - current) * t 

        
    
