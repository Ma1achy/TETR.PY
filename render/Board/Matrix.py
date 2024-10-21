from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from render.board.struct_board import StructBoardConsts
import pygame
from utils import lerpBlendRGBA, SmoothStep

class Matrix():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.BoardConts = BoardConsts
    
    def Draw(self, surface):
        """
        Render the matrix, current tetromino and its shadow onto the window
        
        args:
            four (Four): the Four instance to render
        """
        matrix_rect = pygame.Rect(self.BoardConts.matrix_rect_pos_x, self.BoardConts.matrix_rect_pos_y, self.BoardConts.MATRIX_SURFACE_WIDTH, self.BoardConts.MATRIX_SURFACE_HEIGHT)
        
        self.__DrawCurrentTetrominoShadow(surface, matrix_rect)
        self.__DrawMatrixGrid(surface, matrix_rect)
        self.__DrawPlacedBlocks(surface, self.GameInstanceStruct.matrix.matrix, matrix_rect)
        self.__DrawCurrentTetromino(surface, matrix_rect)
        
        if self.FlagStruct.DANGER:
            self.__DrawNextTetrominoWarning(surface, matrix_rect) 
        
    def __DrawCurrentTetromino(self, surface, matrix_surface_rect:pygame.Rect):
        
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        rect = self.__GetRect(self.GameInstanceStruct.current_tetromino, self.GameInstanceStruct.current_tetromino.position, matrix_surface_rect)
        
        blend_colour = (0, 0, 0)
        piece_alpha = self.__GetLockDelayAlpha(self.GameInstanceStruct.current_tetromino.lock_delay_counter, self.GameInstanceStruct.lock_delay_in_ticks)
        
        self.__DrawTetrominoBlocks(surface, self.GameInstanceStruct.current_tetromino.blocks, rect, blend_colour, piece_alpha)
        
        if self.RenderStruct.draw_bounding_box:
            pygame.draw.rect(surface, (0, 255, 0), rect, 2)
        
        if self.RenderStruct.draw_origin:
            self.__DrawTetrominoPosition(surface, matrix_surface_rect)
              
        if self.RenderStruct.draw_pivot:
            self.__DrawPivotPosition(surface, matrix_surface_rect)
                
    def __DrawCurrentTetrominoShadow(self, surface, matrix_surface_rect:pygame.Rect):
            
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        if self.GameInstanceStruct.current_tetromino.shadow_position.y <= self.GameInstanceStruct.current_tetromino.position.y:
            return
        
        rect = self.__GetRect(self.GameInstanceStruct.current_tetromino, self.GameInstanceStruct.current_tetromino.shadow_position, matrix_surface_rect)
        
        blend_colour = (0, 0, 0)
        piece_alpha = 0.33
        
        self.__DrawTetrominoBlocks(surface, self.GameInstanceStruct.current_tetromino.blocks, rect, blend_colour, piece_alpha)
    
    def __DrawNextTetrominoWarning(self, surface, matrix_surface_rect:pygame.Rect):
        
        if self.GameInstanceStruct.next_tetromino is None:
            return
        
        rect = self.__GetRect(self.GameInstanceStruct.next_tetromino, self.GameInstanceStruct.next_tetromino.position, matrix_surface_rect)
        
        self.__DrawWarningCrosses(surface, self.GameInstanceStruct.next_tetromino.blocks, rect)
            
    def __GetRect(self, tetromino, position, matrix_surface_rect):
        
        tetromino_rect_length = self.RenderStruct.GRID_SIZE * len(tetromino.blocks[0])
        tetromino_rect_width = self.RenderStruct.GRID_SIZE * len(tetromino.blocks[1])
        
        tetromino_position_x =  matrix_surface_rect.x + position.x * self.RenderStruct.GRID_SIZE
        tetromino_position_y = matrix_surface_rect.y + position.y * self.RenderStruct.GRID_SIZE - (self.GameInstanceStruct.matrix.HEIGHT * self.RenderStruct.GRID_SIZE)//2 
        
        return pygame.Rect(tetromino_position_x, tetromino_position_y , tetromino_rect_length, tetromino_rect_width)    
    
    def __DrawTetrominoBlocks(self, surface, tetromino_blocks, rect, blend_colour, alpha):
    
        for i, row in enumerate(tetromino_blocks):
            for j, value in enumerate(row):
                if value != 0:
                    if self.FlagStruct.GAME_OVER:
                        colour = lerpBlendRGBA(self.RenderStruct.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    else:
                        colour = self.RenderStruct.COLOUR_MAP[value]
                    pygame.gfxdraw.box(
                        surface, 
                        (rect.x + j * self.RenderStruct.GRID_SIZE, rect.y + i * self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE),
                        lerpBlendRGBA(blend_colour, colour, alpha)
                    )
                    
    def __GetLockDelayAlpha(self, lock_delay_counter, lock_delay_in_ticks):
        if lock_delay_in_ticks == 0 or lock_delay_in_ticks == 'inf':
            return 1
        
        progress = lock_delay_counter / lock_delay_in_ticks
        smooth_progress = SmoothStep(progress)
        alpha = 1 - max(0, min(0.25, smooth_progress))
        return alpha

    def __DrawWarningCrosses(self, surface, tetromino_blocks, rect):
        
        padding = self.RenderStruct.GRID_SIZE // 5
        thickness = 5
        
        for i, row in enumerate(tetromino_blocks):
            for j, value in enumerate(row):
                if value != 0:
                    pygame.draw.line(surface, (255, 0, 0), 
                                     (rect.x + j * self.RenderStruct.GRID_SIZE + padding, rect.y + i * self.RenderStruct.GRID_SIZE + padding), 
                                     (rect.x + (j + 1) * self.RenderStruct.GRID_SIZE - padding, rect.y + (i + 1) * self.RenderStruct.GRID_SIZE - padding), thickness)
                    
                    pygame.draw.line(surface, (255, 0, 0), 
                                     (rect.x + (j + 1) * self.RenderStruct.GRID_SIZE - padding, rect.y + i * self.RenderStruct.GRID_SIZE + padding), 
                                     (rect.x + j * self.RenderStruct.GRID_SIZE + padding, rect.y + (i + 1) * self.RenderStruct.GRID_SIZE - padding), thickness)
                   
    def __DrawMatrixGrid(self, surface, matrix_surface_rect:pygame.Rect):
        """
        Draw the grid in the background of the matrix
        
        args:
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        grid_colour = lerpBlendRGBA((0, 0, 0), self.__GetGridColour(), 0.25)
        width = 1
        
        for idx in range(self.GameInstanceStruct.matrix.HEIGHT // 2, self.GameInstanceStruct.matrix.HEIGHT):
            pygame.draw.line(surface, grid_colour,
                             (matrix_surface_rect.x, matrix_surface_rect.y + idx * self.RenderStruct.GRID_SIZE - self.BoardConts.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + self.GameInstanceStruct.matrix.WIDTH * self.RenderStruct.GRID_SIZE, matrix_surface_rect.y + idx * self.RenderStruct.GRID_SIZE - self.BoardConts.MATRIX_SURFACE_HEIGHT),
                             width
                             )
            
        for idx in range(self.GameInstanceStruct.matrix.WIDTH + 1):
            pygame.draw.line(surface, grid_colour,
                             (matrix_surface_rect.x + idx * self.RenderStruct.GRID_SIZE, matrix_surface_rect.y + self.BoardConts.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + idx * self.RenderStruct.GRID_SIZE, matrix_surface_rect.y +  self.GameInstanceStruct.matrix.HEIGHT // 2 * self.RenderStruct.GRID_SIZE - self.BoardConts.MATRIX_SURFACE_HEIGHT),
                             width
                             )
    
    def __DrawPlacedBlocks(self, surface, matrix, matrix_surface_rect:pygame.Rect):
        """
        Draw the blocks in the matrix
        
        args:
            matrix (Matrix): the matrix to draw the blocks from
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
            transparent (bool): whether the blocks should be transparent
            alpha (float): the alpha value of the transparency
        """
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if value != 0:
                    if self.FlagStruct.GAME_OVER:
                        colour = lerpBlendRGBA(self.RenderStruct.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    else:
                        colour = self.RenderStruct.COLOUR_MAP[value]
            
                    pygame.draw.rect(
                        surface, colour, 
                        (matrix_surface_rect.x + j * self.RenderStruct.GRID_SIZE, matrix_surface_rect.y + i * self.RenderStruct.GRID_SIZE - self.BoardConts.MATRIX_SURFACE_HEIGHT, self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE)
                        ) 
    
    def __DrawTetrominoPosition(self, surface, matrix_surface_rect):
        loc = self.GameInstanceStruct.current_tetromino.position
        
        x = matrix_surface_rect.x + loc.x * self.RenderStruct.GRID_SIZE
        y = matrix_surface_rect.y + loc.y * self.RenderStruct.GRID_SIZE - (self.GameInstanceStruct.matrix.HEIGHT * self.RenderStruct.GRID_SIZE) // 2 
        
        length = self.RenderStruct.GRID_SIZE // 4

        pygame.draw.line(surface, (0, 255, 0), (x - length, y), (x + length, y), 2)
        pygame.draw.line(surface, (0, 255, 0), (x, y - length), (x, y + length), 2)

    def __DrawPivotPosition(self, surface, matrix_surface_rect):
        
        loc = self.GameInstanceStruct.current_tetromino.position + self.GameInstanceStruct.current_tetromino.pivot
        
        x = matrix_surface_rect.x + loc.x * self.RenderStruct.GRID_SIZE 
        y = matrix_surface_rect.y + loc.y * self.RenderStruct.GRID_SIZE - (self.GameInstanceStruct.matrix.HEIGHT * self.RenderStruct.GRID_SIZE) // 2

        length = self.RenderStruct.GRID_SIZE // 4

        pygame.draw.line(surface, (255, 255, 255), (x - length, y), (x + length, y), 2)
        pygame.draw.line(surface, (255, 255, 255), (x, y - length), (x, y + length), 2)
    
    def __GetGridColour(self):
        """
        Get the colour of the border
        """
        if self.FlagStruct.DANGER:
            return (255, 0, 0)
        else:
            return (255, 255, 255)