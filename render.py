from matrix import Matrix
import pygame
from pygame_config import PyGameConfig
from utils import lerpBlendRGBA
class Render():
    def __init__(self, window:pygame.Surface):
        """
        Render an instance of four onto a window
        
        self.window (pygame.Surface): the window to render the game onto
        """
        
        self.window = window
        self.config = PyGameConfig
        self.four_surface = self.__init_four_surface()
        self.danger = False
        
    def __init_four_surface(self):
        """
        Create the surface to render the matrix, border and blocks to which can be rendered elsewhere on the window
        """
        return pygame.surface.Surface((self.config.FOUR_INSTANCE_WIDTH, self.config.FOUR_INSTANCE_HEIGHT))
    
    def __get_four_coords_for_window_center(self):
        """
        Get the coordinates for the four surface to be centered in the window
        """
        return (self.config.WINDOW_WIDTH - self.config.FOUR_INSTANCE_WIDTH) // 2, (self.config.WINDOW_HEIGHT - self.config.FOUR_INSTANCE_HEIGHT) // 2

    def render_frame(self, four):
        """
        Render the frame of the Four Instance
        
        args:
        four (Four): the Four instance to render
        """
        self.four_surface.fill((0, 0, 0))
        self.window.fill((0, 0, 0))
        
        self.__render_matrix(four.matrix)
            
        self.window.blit(self.four_surface, (self.__get_four_coords_for_window_center()))
        pygame.display.update()
              
    def __draw_grid(self, matrix_surface_rect:pygame.Rect):
        """
        Draw the grid in the background of the matrix
        
        args:
        matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        grid_colour = lerpBlendRGBA((0, 0, 0), self.__get_border_colour(), 0.25)
        
        for idx in range(self.config.MATRIX_HEIGHT // 2, self.config.MATRIX_HEIGHT + 1):
            pygame.draw.line(self.four_surface, grid_colour,
                             (matrix_surface_rect.x, matrix_surface_rect.y + idx * self.config.GRID_SIZE - self.config.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + self.config.MATRIX_WIDTH * self.config.GRID_SIZE, matrix_surface_rect.y + idx * self.config.GRID_SIZE - self.config.MATRIX_SURFACE_HEIGHT)
                             )
            
        for idx in range(self.config.MATRIX_WIDTH + 1):
            pygame.draw.line(self.four_surface, grid_colour,
                             (matrix_surface_rect.x + idx * self.config.GRID_SIZE, matrix_surface_rect.y + self.config.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + idx * self.config.GRID_SIZE, matrix_surface_rect.y + self.config.MATRIX_HEIGHT // 2 * self.config.GRID_SIZE - self.config.MATRIX_SURFACE_HEIGHT)
                             )
            
    def __draw_blocks(self, matrix:Matrix, matrix_surface_rect:pygame.Rect, transparent:bool, alpha:float):
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
                    colour = self.config.COLOUR_MAP[value]
                    if transparent:
                        colour = lerpBlendRGBA((0, 0, 0), colour, alpha)
                    pygame.draw.rect(self.four_surface, colour, 
                                     (matrix_surface_rect.x + j * self.config.GRID_SIZE, matrix_surface_rect.y + i * self.config.GRID_SIZE - self.config.MATRIX_SURFACE_HEIGHT, self.config.GRID_SIZE, self.config.GRID_SIZE)
                                     )

    def __draw_border(self, matrix_rect:pygame.Rect):
        """
        Draw the border around the matrix
        
        args:
        matrix_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        pygame.draw.line(self.four_surface, self.__get_border_colour(), 
                 (self.config.MATRIX_SCREEN_CENTER_X - self.config.BORDER_WIDTH // 2 - 1, self.config.MATRIX_SCREEN_CENTER_Y), 
                 (self.config.MATRIX_SCREEN_CENTER_X - self.config.BORDER_WIDTH // 2 - 1, self.config.MATRIX_SCREEN_CENTER_Y + matrix_rect.height), 
                 self.config.BORDER_WIDTH)

        # Draw the right border line
        pygame.draw.line(self.four_surface, self.__get_border_colour(), 
                        (self.config.MATRIX_SCREEN_CENTER_X + matrix_rect.width + self.config.BORDER_WIDTH // 2 - 1, self.config.MATRIX_SCREEN_CENTER_Y), 
                        (self.config.MATRIX_SCREEN_CENTER_X + matrix_rect.width + self.config.BORDER_WIDTH // 2 - 1, self.config.MATRIX_SCREEN_CENTER_Y + matrix_rect.height), 
                        self.config.BORDER_WIDTH)

        # Draw the bottom border line
        pygame.draw.line(self.four_surface, self.__get_border_colour(), 
                        (self.config.MATRIX_SCREEN_CENTER_X - self.config.BORDER_WIDTH, self.config.MATRIX_SCREEN_CENTER_Y + matrix_rect.height + self.config.BORDER_WIDTH // 2 - 1), 
                        (self.config.MATRIX_SCREEN_CENTER_X + matrix_rect.width + self.config.BORDER_WIDTH - 1, self.config.MATRIX_SCREEN_CENTER_Y + matrix_rect.height + self.config.BORDER_WIDTH // 2 - 1), 
                        self.config.BORDER_WIDTH)
    
    def draw_danger_crosses(self, matrix: Matrix):
        """
        Draw crosses on the danger matrix
        
        args:
        matrix (Matrix): the matrix to draw the crosses on
        """
        offset = self.config.GRID_SIZE // 6  
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if value == -1:
                    start_x = self.config.MATRIX_SCREEN_CENTER_X + j * self.config.GRID_SIZE + offset
                    start_y = self.config.MATRIX_SCREEN_CENTER_Y + i * self.config.GRID_SIZE - self.config.MATRIX_SURFACE_HEIGHT + offset
                    end_x = self.config.MATRIX_SCREEN_CENTER_X + (j + 1) * self.config.GRID_SIZE - offset
                    end_y = self.config.MATRIX_SCREEN_CENTER_Y + (i + 1) * self.config.GRID_SIZE - self.config.MATRIX_SURFACE_HEIGHT - offset
                    
                    pygame.draw.line(self.four_surface, (255, 0, 0), 
                                    (start_x, start_y), 
                                    (end_x, end_y), 
                                    5)
                    pygame.draw.line(self.four_surface, (255, 0, 0), 
                                    (end_x, start_y), 
                                    (start_x, end_y), 
                                    5)
    
    def __get_border_colour(self):
        """
        Get the colour of the border
        """
        if self.danger:
            return (255, 0, 0)
        else:
            return (255, 255, 255)
                          
    def __render_matrix(self, matrix:Matrix):
        """
        Render the matrix onto the window
        
        args:
        MATRIX (Matrix): The matrix object that contains the blocks
        """
        matrix_surface_rect = pygame.Rect(self.config.MATRIX_SCREEN_CENTER_X, self.config.MATRIX_SCREEN_CENTER_Y, self.config.MATRIX_SURFACE_WIDTH, self.config.MATRIX_SURFACE_HEIGHT)
        
        self.__draw_blocks(matrix.ghost, matrix_surface_rect, transparent = True, alpha = 0.33)
        self.__draw_grid(matrix_surface_rect)
        self.__draw_blocks(matrix.matrix, matrix_surface_rect, transparent = False, alpha = 1)
        self.__draw_blocks(matrix.piece, matrix_surface_rect, transparent = False, alpha = 1)
        
        if self.danger:
            self.draw_danger_crosses(matrix.danger)
        
        self.__draw_border(pygame.Rect(self.config.MATRIX_SCREEN_CENTER_X, self.config.MATRIX_SCREEN_CENTER_Y, self.config.MATRIX_SURFACE_WIDTH, self.config.MATRIX_SURFACE_HEIGHT)) 
            
