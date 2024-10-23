from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from render.board.struct_board import StructBoardConsts
import pygame
from utils import lerpBlendRGBA, smoothstep

class Matrix():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.BoardConts = BoardConsts
    
    def draw(self, surface):
        """
        Draw the matrix, current tetromino and its shadow onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        matrix_rect = pygame.Rect(self.BoardConts.matrix_rect_pos_x, self.BoardConts.matrix_rect_pos_y, self.BoardConts.MATRIX_SURFACE_WIDTH, self.BoardConts.MATRIX_SURFACE_HEIGHT)
        
        self.__draw_current_tetromino_shadow(surface, matrix_rect)
        self.__draw_placed_blocks(surface, self.GameInstanceStruct.matrix.matrix, matrix_rect)
        self.__draw_current_tetromino(surface, matrix_rect)
        
        if self.FlagStruct.DANGER:
            self.__draw_next_tetromino_warning(surface, matrix_rect) 
        
    def __draw_current_tetromino(self, surface, matrix_surface_rect:pygame.Rect):
        """
        Draw the current tetromino
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.current_tetromino, self.GameInstanceStruct.current_tetromino.position, matrix_surface_rect)
        
        blend_colour = (0, 0, 0)
        piece_alpha = self.__get_lock_delay_alpha(self.GameInstanceStruct.current_tetromino.lock_delay_counter, self.GameInstanceStruct.lock_delay_in_ticks)
        
        self.__draw_tetromino_blocks(surface, self.GameInstanceStruct.current_tetromino.blocks, rect, blend_colour, piece_alpha)
        
        if self.RenderStruct.draw_bounding_box:
            pygame.draw.rect(surface, (0, 255, 0), rect, 2)
        
        if self.RenderStruct.draw_origin:
            self.__draw_tetromino_position(surface, matrix_surface_rect)
              
        if self.RenderStruct.draw_pivot:
            self.__draw_pivot_position(surface, matrix_surface_rect)
                
    def __draw_current_tetromino_shadow(self, surface, matrix_surface_rect:pygame.Rect):
        """
        Draw the shadow of the current tetromino
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """ 
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        if self.GameInstanceStruct.current_tetromino.shadow_position.y <= self.GameInstanceStruct.current_tetromino.position.y:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.current_tetromino, self.GameInstanceStruct.current_tetromino.shadow_position, matrix_surface_rect)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        blend_colour = (0, 0, 0)
        piece_alpha = 1
        
        self.__draw_tetromino_blocks(shadow_surface, self.GameInstanceStruct.current_tetromino.blocks, shadow_surface.get_rect(), blend_colour, piece_alpha)
        shadow_surface.set_alpha(88)
        surface.blit(shadow_surface, (rect.x, rect.y))
    
    def __draw_next_tetromino_warning(self, surface, matrix_surface_rect:pygame.Rect):
        """
        Draw the warning crosses of the next tetromino
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        if self.GameInstanceStruct.next_tetromino is None:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.next_tetromino, self.GameInstanceStruct.next_tetromino.position, matrix_surface_rect)
        
        self.__DrawWarningCrosses(surface, self.GameInstanceStruct.next_tetromino.blocks, rect)
            
    def __get_rect(self, tetromino, position, matrix_surface_rect):
        """
        Get the rectangle for the tetromino
        
        args:
            tetromino (Tetromino): the tetromino to get the rectangle for
            position (Vector2): the position of the tetromino
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn
        """
        tetromino_rect_length = self.RenderStruct.GRID_SIZE * len(tetromino.blocks[0])
        tetromino_rect_width = self.RenderStruct.GRID_SIZE * len(tetromino.blocks[1])
        
        tetromino_position_x =  matrix_surface_rect.x + position.x * self.RenderStruct.GRID_SIZE
        tetromino_position_y = matrix_surface_rect.y + position.y * self.RenderStruct.GRID_SIZE - (self.GameInstanceStruct.matrix.HEIGHT * self.RenderStruct.GRID_SIZE)//2 
        
        return pygame.Rect(tetromino_position_x, tetromino_position_y , tetromino_rect_length, tetromino_rect_width)    
    
    def __draw_tetromino_blocks(self, surface, tetromino_blocks, rect, blend_colour, alpha):
        """
        Draw the blocks of a tetromino
        
        args:
            surface (pygame.Surface): The surface to draw onto
            tetromino_blocks (list): the blocks of the tetromino
            rect (pygame.Rect): the rectangle to draw the tetromino into
            blend_colour (tuple): the colour to blend the tetromino with
            alpha (float): the alpha value of the tetromino
        """
        for i, row in enumerate(tetromino_blocks):
            for j, value in enumerate(row):
                if value != 0:
                    if self.FlagStruct.GAME_OVER:
                        colour = lerpBlendRGBA(self.RenderStruct.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    else:
                        colour = self.RenderStruct.COLOUR_MAP[value]
                    pygame.draw.rect(
                        surface, 
                        lerpBlendRGBA(blend_colour, colour, alpha),
                        (rect.x + j * self.RenderStruct.GRID_SIZE, rect.y + i * self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE)
                    )
                    
    def __get_lock_delay_alpha(self, lock_delay_counter, lock_delay_in_ticks):
        """
        Get the alpha value to use when blending the current tetromino with a base colour based on the lock delay timer
        """
        if lock_delay_in_ticks == 0 or lock_delay_in_ticks == 'inf':
            return 1
        
        progress = lock_delay_counter / lock_delay_in_ticks
        smooth_progress = smoothstep(progress)
        alpha = 1 - max(0, min(0.25, smooth_progress))
        return alpha

    def __DrawWarningCrosses(self, surface, tetromino_blocks, rect):
        """
        Draw the warning crosses for the next tetromino
        """
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
                    
    def __draw_placed_blocks(self, surface, matrix, matrix_surface_rect:pygame.Rect):
        """
        Draw the placed blocks in the matrix
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix (list): the matrix to draw
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn
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
    
    def __draw_tetromino_position(self, surface, matrix_surface_rect):
        """
        Draw the position of the current tetromino as a cross
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        loc = self.GameInstanceStruct.current_tetromino.position
        
        x = matrix_surface_rect.x + loc.x * self.RenderStruct.GRID_SIZE
        y = matrix_surface_rect.y + loc.y * self.RenderStruct.GRID_SIZE - (self.GameInstanceStruct.matrix.HEIGHT * self.RenderStruct.GRID_SIZE) // 2 
        
        length = self.RenderStruct.GRID_SIZE // 4

        pygame.draw.line(surface, (0, 255, 0), (x - length, y), (x + length, y), 2)
        pygame.draw.line(surface, (0, 255, 0), (x, y - length), (x, y + length), 2)

    def __draw_pivot_position(self, surface, matrix_surface_rect):
        """
        Draw the pivot of the current tetromino as a cross
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        loc = self.GameInstanceStruct.current_tetromino.position + self.GameInstanceStruct.current_tetromino.pivot
        
        x = matrix_surface_rect.x + loc.x * self.RenderStruct.GRID_SIZE 
        y = matrix_surface_rect.y + loc.y * self.RenderStruct.GRID_SIZE - (self.GameInstanceStruct.matrix.HEIGHT * self.RenderStruct.GRID_SIZE) // 2

        length = self.RenderStruct.GRID_SIZE // 4

        pygame.draw.line(surface, (255, 255, 255), (x - length, y), (x + length, y), 2)
        pygame.draw.line(surface, (255, 255, 255), (x, y - length), (x, y + length), 2)
    
    def __get_grid_colour(self):
        """
        Get the colour of the border
        """
        if self.FlagStruct.DANGER:
            return (255, 0, 0)
        else:
            return (255, 255, 255)