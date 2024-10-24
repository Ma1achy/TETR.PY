from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from render.board.struct_board import StructBoardConsts
import pygame
from utils import lerpBlendRGBA, get_tetromino_blocks


class HoldAndQueue():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.BoardConsts = BoardConsts
        
        self.background_alpha = 200
        
        self.BoardConsts.queue_rect_width = 6 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2
        self.BoardConsts.queue_rect_height = 3 * self.GameInstanceStruct.queue_previews * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2
        
        self.BoardConsts.hold_rect_width = 6 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH 
        self.BoardConsts.hold_rect_height = 3 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2 
    
    def draw(self, surface):
        """
        Draw the hold and queue onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.__draw_queue(surface)
        self.__draw_hold(surface)
    
    def __draw_queue(self, surface):
        """
        Draw the queue
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        queue_rect = self.__get_queue_rect()
        queue_background_Surf = pygame.Surface((queue_rect.width, queue_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        queue_background_Surf.fill((0, 0, 0))
        
        queue_background_Surf.set_alpha(self.background_alpha)
        surface.blit(queue_background_Surf, queue_rect.topleft)
        
        for idx, tetromino in enumerate(self.GameInstanceStruct.queue.queue):
            if idx == self.GameInstanceStruct.queue_previews:
                break
            
            row_height = queue_rect.height // self.GameInstanceStruct.queue_previews  # split queue_rect into queue length number of rows
            row_y = queue_rect.y + idx * row_height
            
            preview_rect = pygame.Rect(queue_rect.x, row_y, queue_rect.width, row_height)
            self.__draw_tetromino_preview(surface, tetromino, preview_rect)
       
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
        rect_x = self.BoardConsts.matrix_rect_pos_x - 7 * self.RenderStruct.GRID_SIZE
        rect_y =  self.BoardConsts.matrix_rect_pos_y + 1 * self.RenderStruct.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.BoardConsts.hold_rect_width, self.BoardConsts.hold_rect_height)
    
    def __draw_hold(self, surface):
        """
        Draw the hold
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        tetromino = self.GameInstanceStruct.held_tetromino    
        hold_rect = self.__get_hold_rect()
        hold_background_Surf = pygame.Surface((hold_rect.width, hold_rect.height), pygame.SRCALPHA|pygame.HWSURFACE)
        hold_background_Surf.fill((0, 0, 0))
        
        hold_background_Surf.set_alpha(self.background_alpha)
        surface.blit(hold_background_Surf, hold_rect.topleft)
        
        self.__draw_tetromino_preview(surface, tetromino, hold_rect, can_hold = self.GameInstanceStruct.can_hold)
        
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

        for i, row in enumerate(tetromino):
            for j, value in enumerate(row):
                if value != 0:
                    if can_hold:
                        colour = self.RenderStruct.COLOUR_MAP[value]
                    else:
                        colour = lerpBlendRGBA(self.RenderStruct.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    
                    pygame.gfxdraw.box(surface, 
                                    (rect.x + offset_x + j * self.RenderStruct.GRID_SIZE, rect.y + offset_y + i * self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE),
                                    colour
                                    )