import pygame.gfxdraw
from app.state.config import Config

from instance.state.flags import Flags
from instance.state.game_state import GameState

from app.debug.debug_metrics import DebugMetrics
from utils import TransformSurface
from render.UI.debug_menu import UIDebug
from render.UI.key_states_overlay import UIKeyStates
from render.board.board import Board
from render.fonts import Fonts

class Render():
    def __init__(self, RenderStruct:StructRender, Flags:Flags, GameInstanceStruct:GameState, TimingStruct:StructTiming, DebugStruct:DebugMetrics):  
        """
        Render an instance of four onto a window
        
        args:
            self.window (pygame.Surface): the window to render the game onto
        """
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = Flags
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.DebugStruct = DebugStruct
        self.icon = pygame.image.load('resources/icon.png')
        self.window = self.__init_window()
        self.Fonts = Fonts(self.RenderStruct)
        
        self.RenderStruct.TEXTURE_ATLAS = pygame.image.load('resources/block/blocks.png').convert_alpha()
        self.RenderStruct.TEXTURES_PER_ROW = 5
        self.RenderStruct.TEXTURES_PER_COLUMN = 5
      
        self.RenderStruct.use_textures = True
        self.RenderStruct.coloured_shadow = True
        self.RenderStruct.shadow_opacity = 200
        
        self.board_center_screen_pos_x = self.RenderStruct.WINDOW_WIDTH // 2
        self.board_center_screen_pos_y = self.RenderStruct.WINDOW_HEIGHT // 2
        
        self.Board = Board(self.Config, self.RenderStruct, self.FlagStruct, self.GameInstanceStruct, self.TimingStruct, self.DebugStruct, self.Fonts)
        self.UI_Debug = UIDebug(self.Config, self.RenderStruct, self.DebugStruct, self.FlagStruct, self.Fonts)
        self.UI_KeyStates = UIKeyStates(self.RenderStruct, self.Fonts)
        self.board_surface = self.Board.get_board_surface()
        
        self.image_path = 'resources/background/b1.jpg'
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT))
        
    def __init_window(self):
        """
        Create the window to draw to
        """
        pygame.display.set_icon(self.icon)
        pygame.display.set_caption(self.RenderStruct.CAPTION)
        return pygame.display.set_mode((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF)
     
    def draw_frame(self):
        """
        Render the frame of the Four Instance
        """
        if self.TimingStruct.FPS == 0:
            self.dt = 1
        else:
            self.dt = 1 / self.TimingStruct.FPS
            
        self.window.fill((0, 0, 0))
        self.window.blit(self.image, (0, 0))
        
        if self.Board.top_out_surface_alpha > 1:
            self.window.blit(self.Board.top_out_surface, (0, 0))
        
        self.board_surface.fill((0, 0, 0, 0))
        self.Board.draw(self.board_surface)
        
        transformed_surface, transformed_rect = TransformSurface(self.board_surface, self.Board.scale, self.Board.angle, pygame.Vector2(self.Board.board_center_x_board_space, self.Board.board_center_y_board_space), pygame.Vector2(self.board_center_screen_pos_x, self.board_center_screen_pos_y), pygame.Vector2(self.Board.offset_x, self.Board.offset_y))
        transformed_surface.set_alpha(self.Board.alpha)
        self.window.blit(transformed_surface, transformed_rect.topleft)

        self.draw_guidline_debug()
        self.UI_Debug.draw(self.window)
        self.UI_KeyStates.draw(self.window)
        
        pygame.display.update()
        
    def draw_guidline_debug(self):
        if self.RenderStruct.draw_guide_lines:
            pygame.draw.line(self.window, (255, 0, 255), (self.RenderStruct.WINDOW_WIDTH // 2, 0), (self.RenderStruct.WINDOW_WIDTH // 2, self.RenderStruct.WINDOW_HEIGHT), 1)
            pygame.draw.line(self.window, (255, 0, 255), (0, self.RenderStruct.WINDOW_HEIGHT // 2), (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT // 2), 1)
            pygame.draw.line(self.window, (0, 255, 0), (self.RenderStruct.WINDOW_WIDTH // 4, 0), (self.RenderStruct.WINDOW_WIDTH // 4, self.RenderStruct.WINDOW_HEIGHT), 1)
            pygame.draw.line(self.window, (0, 255, 0), (0, self.RenderStruct.WINDOW_HEIGHT // 4), (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT // 4), 1)
            pygame.draw.line(self.window, (0, 255, 0), (self.RenderStruct.WINDOW_WIDTH // 4 * 3, 0), (self.RenderStruct.WINDOW_WIDTH // 4 * 3, self.RenderStruct.WINDOW_HEIGHT), 1)
            pygame.draw.line(self.window, (0, 255, 0), (0, self.RenderStruct.WINDOW_HEIGHT // 4 * 3), (self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT // 4 * 3), 1)