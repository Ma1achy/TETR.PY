from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from render.board.struct_board import StructBoardConsts
import pygame
from utils import lerpBlendRGBA

class UIBorder():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct, Fonts, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.FlagStruct = FlagStruct
        self.Fonts = Fonts
        self.BoardConsts = BoardConsts
        
        self.matrix_background_surface_rect = pygame.Rect(self.BoardConsts.matrix_rect_pos_x, self.BoardConsts.matrix_rect_pos_y, self.BoardConsts.MATRIX_SURFACE_WIDTH, self.BoardConsts.MATRIX_SURFACE_HEIGHT)
        self.matrix_background_surface = pygame.Surface((self.BoardConsts.MATRIX_SURFACE_WIDTH, self.BoardConsts.MATRIX_SURFACE_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)
        
        self.garbage_bar_background_rect = pygame.Rect(self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y, self.RenderStruct.GRID_SIZE, self.BoardConsts.MATRIX_SURFACE_HEIGHT)
        self.garbage_bar_background_surface = pygame.Surface((self.RenderStruct.GRID_SIZE, self.BoardConsts.MATRIX_SURFACE_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)
        self.garbage_bar_background_surface.set_alpha(200)
        
    def draw(self, surface):
        """
        Draw the border around the matrix, hold, and queue onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        
        self.__draw_matrix_grid(surface)
        self.__draw_border(surface)
        
        if self.BoardConsts.draw_garbage_bar:
            self.__draw_garbage_border(surface)
        
        if self.GameInstanceStruct.hold:  
            self.__draw_hold_border(surface)
        
        if self.GameInstanceStruct.queue_previews > 0:
            self.__draw_queue_border(surface)
        
    def __draw_matrix_grid(self, surface):
        """
        Draw the grid in the background of the matrix
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        self.matrix_background_surface.fill((0, 0, 0, 200))
        grid_colour = lerpBlendRGBA((0, 0, 0), self.__get_border_colour(), 0.25)
        width = 1
        
        for idx in range(self.GameInstanceStruct.matrix.WIDTH + 1):
            pygame.draw.line(self.matrix_background_surface, grid_colour, 
                            (idx * self.RenderStruct.GRID_SIZE, 0), 
                            (idx * self.RenderStruct.GRID_SIZE, self.BoardConsts.MATRIX_SURFACE_HEIGHT), width)

        for idx in range(self.GameInstanceStruct.matrix.HEIGHT + 1):
            pygame.draw.line(self.matrix_background_surface, grid_colour, 
                            (0, idx * self.RenderStruct.GRID_SIZE), 
                            (self.BoardConsts.MATRIX_SURFACE_WIDTH, idx * self.RenderStruct.GRID_SIZE), width)
        
        surface.blit(self.matrix_background_surface, self.matrix_background_surface_rect.topleft)
                    
    def __draw_border(self, surface):
        """
        Draw a border around the matrix
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """ 
        pygame.draw.line(surface, self.__get_border_colour(), # matrix left border
                 (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH // 2 - 1, self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.BoardConsts.matrix_rect_pos_y), 
                 (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH // 2 - 1, self.BoardConsts.matrix_rect_pos_y), self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.__get_border_colour(),   # matrix right border
                        (self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y), 
                        (self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT - 1), 
                        self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.__get_border_colour(),  # matrix bottom border
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2), 
                        (self.BoardConsts.matrix_rect_pos_x   + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH - 1, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2), 
                        self.RenderStruct.BORDER_WIDTH)

    def __draw_garbage_border(self, surface):
        """
        Draw a border around the garbage bar
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.garbage_bar_background_surface.fill((0, 0, 0, 200))
        
        pygame.draw.line(surface, self.__get_border_colour(), # left garbage border
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH // 2 - 1 - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y), 
                        (self.BoardConsts.matrix_rect_pos_x   - self.RenderStruct.BORDER_WIDTH // 2 - 1 - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT - 1), 
                        self.RenderStruct.BORDER_WIDTH)
        
        pygame.draw.line(surface, self.__get_border_colour(), # horizontal line inside bar
                        (self.BoardConsts.matrix_rect_pos_x   - self.RenderStruct.BORDER_WIDTH - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT - self.RenderStruct.GRID_SIZE * 8 + self.RenderStruct.BORDER_WIDTH // 2 - 1) , 
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH , self.BoardConsts.matrix_rect_pos_y+ self.BoardConsts.MATRIX_SURFACE_HEIGHT - self.RenderStruct.GRID_SIZE * 8 + self.RenderStruct.BORDER_WIDTH // 2 - 1), 
                        self.RenderStruct.BORDER_WIDTH)
        
        pygame.draw.line(surface, self.__get_border_colour(),# bottom garbage border
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2 - 1) , 
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH , self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2 - 1), 
                        self.RenderStruct.BORDER_WIDTH)
        
        self.surface.blit(self.garbage_bar_background_surface, self.garbage_bar_background_rect.topleft)
        
    def __draw_queue_border(self, surface):
        """
        Draw a border around the queue
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        match self.GameInstanceStruct.queue_previews:
            case 1:
                queue_size = self.RenderStruct.GRID_SIZE * 4.5
            case 2: 
                queue_size = self.RenderStruct.GRID_SIZE * 7.5
            case 3:
                queue_size = self.RenderStruct.GRID_SIZE * 10.5
            case 4:
                queue_size = self.RenderStruct.GRID_SIZE * 13.5
            case 5:
                queue_size = self.RenderStruct.GRID_SIZE * 16.5
            case 6:
                queue_size = self.RenderStruct.GRID_SIZE * 19.5
            case _:
                queue_size = self.RenderStruct.GRID_SIZE * 19.5
      
        pygame.draw.line(surface, self.__get_border_colour(), # queue right border
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + 6 * self.RenderStruct.GRID_SIZE + self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2 - 1),
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + 6 * self.RenderStruct.GRID_SIZE + self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + queue_size - self.RenderStruct.GRID_SIZE // 2 + 1),
                        self.RenderStruct.BORDER_WIDTH)
        
        pygame.draw.line(surface, self.__get_border_colour(), # queue bottom border
                (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH + 6 * self.RenderStruct.GRID_SIZE  + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + queue_size - self.RenderStruct.GRID_SIZE // 2 + 1),
                (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + queue_size - self.RenderStruct.GRID_SIZE // 2 + 1),
                self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.__get_border_colour(), # queue top border
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH + 6 * self.RenderStruct.GRID_SIZE  + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
                        self.RenderStruct.GRID_SIZE)
    
        text = self.Fonts.hun2_big.render('NEXT', True, (0, 0, 0))
        surface.blit(text, (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE * 0.15))
        
    def __draw_hold_border(self, surface):
        """
        Draw a border around the hold
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        if self.BoardConsts.draw_garbage_bar:
            start = 7
            end = - self.RenderStruct.GRID_SIZE
        else:
            start = 6
            end = 0
            
        pygame.draw.line(surface, self.__get_border_colour(), # hold left border
                        (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH //2 - 1, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2 - 1),
                        (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH //2 - 1, self.BoardConsts.matrix_rect_pos_y + 4 * self.RenderStruct.GRID_SIZE),
                        self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.__get_border_colour(), # hold bottom border
                        (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + 4 * self.RenderStruct.GRID_SIZE),
                        (self.BoardConsts.matrix_rect_pos_x  + end - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + 4 * self.RenderStruct.GRID_SIZE),
                        self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.__get_border_colour(), # hold top border
            (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
            (self.BoardConsts.matrix_rect_pos_x  + end - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
            self.RenderStruct.GRID_SIZE)
        
            
        text = self.Fonts.hun2_big.render('HOLD', True, (0, 0, 0))
        surface.blit(text, (self.BoardConsts.matrix_rect_pos_x  - (start + 0.25) * self.RenderStruct.GRID_SIZE + self.RenderStruct.GRID_SIZE * 0.25, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE * 0.15))
        
    def __get_border_colour(self):
        """
        Get the colour of the border
        """
        if self.FlagStruct.DANGER:
            return (255, 0, 0)
        else:
            return (255, 255, 255)