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
        
        self.queue_rect_width = 6 * self.RenderStruct.GRID_SIZE + self.RenderStruct.BORDER_WIDTH // 2 + 1
        self.queue_rect_height = 3 * self.GameInstanceStruct.queue.length * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2
        
        self.hold_rect_width = 6 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2
        self.hold_rect_height = 3 * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH // 2
    
    def Draw(self, surface):
        self.__DrawQueue(surface)
        self.__DrawHold(surface)
    
    def __DrawQueue(self, surface):
        """
        Render the queue onto the window
        
        args0
            four (Four): the Four instance to render
        """
        queue_rect = self.__GetQueueRect()
        pygame.gfxdraw.box(surface, queue_rect, (0, 0, 0))
        
        for idx, tetromino in enumerate(self.GameInstanceStruct.queue.queue):
            
            # split queue_rect into queue length number of rows
            row_height = queue_rect.height // self.GameInstanceStruct.queue.length
            row_y = queue_rect.y + idx * row_height
            
            preview_rect = pygame.Rect(queue_rect.x, row_y, queue_rect.width, row_height)
            self.__DrawTetrominoPreview(surface, tetromino, preview_rect)
       
    def __GetQueueRect(self):
        """
        Get the rectangle for the queue
        """
        rect_x = self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2
        rect_y =  self.BoardConsts.matrix_rect_pos_y + 1 * self.RenderStruct.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.queue_rect_width, self.queue_rect_height)	
    
    def __GetHoldRect(self):
        """
        Get the rectangle for the hold
        """
        rect_x = self.BoardConsts.matrix_rect_pos_x - 7 * self.RenderStruct.GRID_SIZE
        rect_y =  self.BoardConsts.matrix_rect_pos_y + 1 * self.RenderStruct.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.hold_rect_width, self.hold_rect_height)
    
    def __DrawHold(self, surface):
        """
        Render the hold onto the window
        
        args:
            four (Four): the Four instance
        """
        tetromino = self.GameInstanceStruct.held_tetromino    
        hold_rect = self.__GetHoldRect()
        pygame.gfxdraw.box(surface, hold_rect, (0, 0, 0))
        
        self.__DrawTetrominoPreview(surface, tetromino, hold_rect, can_hold = self.GameInstanceStruct.can_hold)
        
    def __DrawTetrominoPreview(self, surface, tetromino, rect, can_hold = True):
        """
        Render a tetromino preview
        
        args:
            tetromino (list): the type of tetromino to render
            rect (pygame.Rect): the rectangle to draw the tetromino in
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