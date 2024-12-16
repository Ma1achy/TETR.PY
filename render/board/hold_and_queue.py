from old_state.struct_render import StructRender
from instance.state.flags import Flags
from instance.state.game_state import GameState
from render.board.struct_board import StructBoardConsts
import pygame
from utils import lerpBlendRGBA, get_tetromino_blocks


class HoldAndQueue():
    def __init__(self, RenderStruct:StructRender, FlagStruct:Flags, GameInstanceStruct:GameState, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.BoardConsts = BoardConsts
        
        self.background_alpha = 200
        
        self.BoardConsts.queue_rect_width = 6 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2
        self.BoardConsts.queue_rect_height = 3 * self.GameInstanceStruct.queue_previews * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2 + 1
        
        self.BoardConsts.hold_rect_width = 6 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH 
        self.BoardConsts.hold_rect_height = 3 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2 
        
        if self.GameInstanceStruct.queue_previews > 0:
            self.queue_rect = self.__get_queue_rect()
            self.queue_background_Surf = pygame.Surface((self.queue_rect.width, self.queue_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
            
            self.row_height = self.queue_rect.height // self.GameInstanceStruct.queue_previews  # split queue_rect into queue length number of rows
            
            self.queue_surf = pygame.Surface((self.queue_rect.width, self.queue_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
            self.queue_pieces = 'PLACEHOLDER'
            
        if self.GameInstanceStruct.hold:
            self.hold_rect = self.__get_hold_rect()
            self.hold_background_Surf = pygame.Surface((self.hold_rect.width, self.hold_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
            
            self.hold_surf = pygame.Surface((self.hold_rect.width, self.hold_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
            self.held_piece = 'PLACEHOLDER'
            self.can_hold = 'PLACEHOLDER'
        
    def draw(self, surface):
        """
        Draw the hold and queue onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        if self.GameInstanceStruct.queue_previews > 0:
            self.__draw_queue(surface)
        
        if self.GameInstanceStruct.hold:
            self.__draw_hold(surface)
    
    def __draw_queue(self, surface):
        """
        Draw the queue
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        
        if self.queue_pieces != self.GameInstanceStruct.queue.queue[:self.GameInstanceStruct.queue_previews]:
            
            self.queue_pieces = self.GameInstanceStruct.queue.queue[:self.GameInstanceStruct.queue_previews]
            
            self.queue_background_Surf.fill((0, 0, 0, self.background_alpha))
            self.queue_surf.fill((0, 0, 0, 0))
            
            for idx, tetromino in enumerate(self.GameInstanceStruct.queue.queue):
                if idx == self.GameInstanceStruct.queue_previews:
                    break
                
                self.row_y = idx * self.row_height
                preview_rect = pygame.Rect(0, self.row_y, self.queue_rect.width, self.row_height)
                self.__draw_tetromino_preview(self.queue_surf, tetromino, preview_rect)
        
        surface.blit(self.queue_background_Surf, self.queue_rect.topleft)  
        surface.blit(self.queue_surf, self.queue_rect.topleft)

    def __get_queue_rect(self):
        """
        Get the rectangle for the queue
        """
        rect_x = self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH 
        rect_y =  self.BoardConsts.matrix_rect_pos_y + 1 * self.RenderStruct.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.BoardConsts.queue_rect_width, self.BoardConsts.queue_rect_height)	
    
    def __get_hold_rect(self):
        """
        Get the rectangle for the hold
        """
        if self.BoardConsts.draw_garbage_bar:
            start = 7
        else:
            start = 6
            
        rect_x = self.BoardConsts.matrix_rect_pos_x - start * self.RenderStruct.GRID_SIZE
        rect_y =  self.BoardConsts.matrix_rect_pos_y + 1 * self.RenderStruct.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.BoardConsts.hold_rect_width, self.BoardConsts.hold_rect_height)
    
    def __draw_hold(self, surface):
        """
        Draw the hold
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        
        if self.GameInstanceStruct.held_tetromino != self.held_piece or self.GameInstanceStruct.can_hold != self.can_hold:
            self.held_piece = self.GameInstanceStruct.held_tetromino
            self.can_hold = self.GameInstanceStruct.can_hold
            self.hold_background_Surf.fill((0, 0, 0, self.background_alpha))
            self.hold_surf.fill((0, 0, 0, 0))
            
            preview_rect = pygame.Rect(0, 0, self.hold_rect.width, self.hold_rect.height)
            self.__draw_tetromino_preview(self.hold_surf, self.GameInstanceStruct.held_tetromino, preview_rect, can_hold = self.GameInstanceStruct.can_hold)
        
        surface.blit(self.hold_background_Surf, self.hold_rect.topleft)
        surface.blit(self.hold_surf, self.hold_rect.topleft)
        
    def __draw_tetromino_preview(self, surface, tetromino, rect, can_hold = True):
        """
        Draw preview of a tetromino
        
        args:
            surface (pygame.Surface): The surface to draw onto
            tetromino (list): The tetromino to draw
            rect (pygame.Rect): The rectangle to draw the tetromino into
            can_hold (bool): Whether the tetromino can be held
        """
        if tetromino is None:
            return
        
        tetromino = get_tetromino_blocks(tetromino)
        tetromino = [row for row in tetromino if any(cell != 0 for cell in row)] # remove rows with only 0 values in from tetromino
        
        tetromino_height = len(tetromino) * self.RenderStruct.GRID_SIZE
        tetromino_width = len(tetromino[0]) * self.RenderStruct.GRID_SIZE

        offset_x = (rect.width - tetromino_width) // 2
        offset_y = (rect.height - tetromino_height) // 2

        if self.RenderStruct.use_textures:
            for i, row in enumerate(tetromino):
                for j, value in enumerate(row):
                    if value != 0:
                        if can_hold:
                            texture = self.RenderStruct.textures[value]
                        else:
                            texture = self.RenderStruct.textures['Locked']
                        
                        surface.blit(texture, (rect.x + offset_x + j * self.RenderStruct.GRID_SIZE, rect.y + offset_y + i * self.RenderStruct.GRID_SIZE))
            
        else:
            for i, row in enumerate(tetromino):
                for j, value in enumerate(row):
                    if value != 0:
                        if can_hold:
                            colour = self.RenderStruct.COLOUR_MAP[value]
                        else:
                            colour = lerpBlendRGBA(self.RenderStruct.COLOUR_MAP[value], self.RenderStruct.COLOUR_MAP['Locked'], 0.85)
                        
                        pygame.gfxdraw.box(surface, 
                                        (rect.x + offset_x + j * self.RenderStruct.GRID_SIZE, rect.y + offset_y + i * self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE),
                                        colour
                                        )