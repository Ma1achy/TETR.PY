from matrix import Matrix
import pygame
from pygame_config import PyGameConfig
from config import Config
from utils import lerpBlendRGBA, Font, get_tetromino_blocks, get_prefix
import math
class Render():
    def __init__(self, window:pygame.Surface):
        """
        Render an instance of four onto a window
        
        self.window (pygame.Surface): the window to render the game onto
        """
        self.surfaces = []
        
        pygame.font.init()
        self.window = window
        self.pgconfig = PyGameConfig
        self.config = Config()
        self.four_surface = self.__init_four_surface()
        self.danger = False
        
        # fonts
        self.hun2_big = Font(self.pgconfig.GRID_SIZE).hun2()
        self.hun2_small = Font(self.pgconfig.GRID_SIZE//2).hun2()
        self.pfw_small = Font(self.pgconfig.GRID_SIZE//2).pfw()
        
    def __init_four_surface(self):
        """
        Create the surface to render the matrix, border and blocks to which can be rendered elsewhere on the window
        """
        return pygame.surface.Surface((self.pgconfig.FOUR_INSTANCE_WIDTH, self.pgconfig.FOUR_INSTANCE_HEIGHT))
    
    def render_frame(self, four, debug = None):
        """
        Render the frame of the Four Instance
        
        args:
        four (Four): the Four instance to render
        """
        self.surfaces = []
        self.danger = four.danger
        self.four_surface.fill((0, 0, 0))
        self.window.fill((0, 0, 0))
        
        self.__render_matrix(four)
        self.__render_hold(four)
        self.__render_queue(four)
            
        for surface, coords in self.surfaces:
            self.four_surface.blit(surface, coords)
        
        self.window.blit(self.four_surface, self.__get_four_coords_for_window_center())
        
        if debug is not None:
            self.__draw_debug(debug)
            
        pygame.display.update()
        
    def __get_four_coords_for_window_center(self):
        """
        Get the coordinates for the four surface to be centered in the window
        """
        return (self.pgconfig.WINDOW_WIDTH - self.pgconfig.FOUR_INSTANCE_WIDTH) // 2, (self.pgconfig.WINDOW_HEIGHT - self.pgconfig.FOUR_INSTANCE_HEIGHT) // 2
              
    def __draw_grid(self, matrix_surface_rect:pygame.Rect):
        """
        Draw the grid in the background of the matrix
        
        args:
        matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        grid_colour = lerpBlendRGBA((0, 0, 0), self.__get_border_colour(), 0.25)
        
        for idx in range(self.pgconfig.MATRIX_HEIGHT // 2, self.pgconfig.MATRIX_HEIGHT + 1):
            pygame.draw.line(self.four_surface, grid_colour,
                             (matrix_surface_rect.x, matrix_surface_rect.y + idx * self.pgconfig.GRID_SIZE - self.pgconfig.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + self.pgconfig.MATRIX_WIDTH * self.pgconfig.GRID_SIZE, matrix_surface_rect.y + idx * self.pgconfig.GRID_SIZE - self.pgconfig.MATRIX_SURFACE_HEIGHT)
                             )
            
        for idx in range(self.pgconfig.MATRIX_WIDTH + 1):
            pygame.draw.line(self.four_surface, grid_colour,
                             (matrix_surface_rect.x + idx * self.pgconfig.GRID_SIZE, matrix_surface_rect.y + self.pgconfig.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + idx * self.pgconfig.GRID_SIZE, matrix_surface_rect.y + self.pgconfig.MATRIX_HEIGHT // 2 * self.pgconfig.GRID_SIZE - self.pgconfig.MATRIX_SURFACE_HEIGHT)
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
                    colour = self.pgconfig.COLOUR_MAP[value]
                    if transparent:
                        colour = lerpBlendRGBA((0, 0, 0), colour, alpha)
                    pygame.draw.rect(self.four_surface, colour, 
                                     (matrix_surface_rect.x + j * self.pgconfig.GRID_SIZE, matrix_surface_rect.y + i * self.pgconfig.GRID_SIZE - self.pgconfig.MATRIX_SURFACE_HEIGHT, self.pgconfig.GRID_SIZE, self.pgconfig.GRID_SIZE)
                                     )

    def __draw_matrix_border(self):
        """
        Draw a border around the matrix, garbage, queue and hold
        
        args:
        matrix_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        
        # ====== MATRIX ======
        
        pygame.draw.line(self.four_surface, self.__get_border_colour(), # matrix left border
                 (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.BORDER_WIDTH // 2 - 1, self.pgconfig.MATRIX_SCREEN_CENTER_Y), 
                 (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.BORDER_WIDTH // 2 - 1, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.MATRIX_SURFACE_HEIGHT - 1), 
                 self.pgconfig.BORDER_WIDTH)

        pygame.draw.line(self.four_surface, self.__get_border_colour(),   # matrix right border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH // 2, self.pgconfig.MATRIX_SCREEN_CENTER_Y), 
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH // 2, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.MATRIX_SURFACE_HEIGHT - 1), 
                        self.pgconfig.BORDER_WIDTH)

        pygame.draw.line(self.four_surface, self.__get_border_colour(),  # matrix bottom border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.BORDER_WIDTH - self.pgconfig.GRID_SIZE, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.MATRIX_SURFACE_HEIGHT + self.pgconfig.BORDER_WIDTH // 2 - 1), 
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH - 1, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.MATRIX_SURFACE_HEIGHT + self.pgconfig.BORDER_WIDTH // 2 - 1), 
                        self.pgconfig.BORDER_WIDTH)

        # ====== GARBAGE =======
        
        pygame.draw.line(self.four_surface, self.__get_border_colour(), # left garbage border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.BORDER_WIDTH // 2 - 1 - self.pgconfig.GRID_SIZE, self.pgconfig.MATRIX_SCREEN_CENTER_Y), 
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.BORDER_WIDTH // 2 - 1 - self.pgconfig.GRID_SIZE, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.MATRIX_SURFACE_HEIGHT - 1), 
                        self.pgconfig.BORDER_WIDTH)
        
        pygame.draw.line(self.four_surface, self.__get_border_colour(),  # matrix bottom border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.BORDER_WIDTH - self.pgconfig.GRID_SIZE, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.MATRIX_SURFACE_HEIGHT - self.pgconfig.GRID_SIZE * 8 + self.pgconfig.BORDER_WIDTH // 2 - 1) , 
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.BORDER_WIDTH , self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.MATRIX_SURFACE_HEIGHT - self.pgconfig.GRID_SIZE * 8 + self.pgconfig.BORDER_WIDTH // 2 - 1), 
                        self.pgconfig.BORDER_WIDTH)
        
    
    def __draw_queue_border(self):
        
        match self.config.QUEUE_LENGTH:
            case 1:
                queue_size = self.pgconfig.GRID_SIZE * 4.5
            case 2: 
                queue_size = self.pgconfig.GRID_SIZE * 7.5
            case 3:
                queue_size = self.pgconfig.GRID_SIZE * 10.5
            case 4:
                queue_size = self.pgconfig.GRID_SIZE * 13.5
            case 5:
                queue_size = self.pgconfig.GRID_SIZE * 16.5
            case 6:
                queue_size = self.pgconfig.GRID_SIZE * 19.5
            case _:
                queue_size = self.pgconfig.GRID_SIZE * 19.5
      
        pygame.draw.line(self.four_surface, self.__get_border_colour(), # queue left border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + 6 * self.pgconfig.GRID_SIZE + self.pgconfig.BORDER_WIDTH, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE // 2 - 1),
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + 6 * self.pgconfig.GRID_SIZE + self.pgconfig.BORDER_WIDTH, self.pgconfig.MATRIX_SCREEN_CENTER_Y + queue_size - self.pgconfig.GRID_SIZE // 2 - 1),
                        self.pgconfig.BORDER_WIDTH)
        
        pygame.draw.line(self.four_surface, self.__get_border_colour(), # queue bottom border
                (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH + 6 * self.pgconfig.GRID_SIZE  + self.pgconfig.BORDER_WIDTH // 2, self.pgconfig.MATRIX_SCREEN_CENTER_Y + queue_size - self.pgconfig.GRID_SIZE // 2 - 1),
                (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH // 2, self.pgconfig.MATRIX_SCREEN_CENTER_Y + queue_size - self.pgconfig.GRID_SIZE // 2 - 1),
                self.pgconfig.BORDER_WIDTH)

        pygame.draw.line(self.four_surface, self.__get_border_colour(), # queue top border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH + 6 * self.pgconfig.GRID_SIZE  + self.pgconfig.BORDER_WIDTH // 2, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE // 2 - 1),
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH // 2, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE // 2 - 1),
                        self.pgconfig.GRID_SIZE)
    
        next_text_surface = self.hun2_big.render('NEXT', True, (0, 0, 0))
        self.surfaces.append((next_text_surface, (self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.GRID_SIZE * 10 + self.pgconfig.BORDER_WIDTH , self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE * 0.15))) 
        
    def __draw_hold_border(self):
        
        pygame.draw.line(self.four_surface, self.__get_border_colour(), # hold left border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - 7 * self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH //2 - 1, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE // 2 - 1),
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - 7 * self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH //2 - 1, self.pgconfig.MATRIX_SCREEN_CENTER_Y + 4 * self.pgconfig.GRID_SIZE),
                        self.pgconfig.BORDER_WIDTH)

        pygame.draw.line(self.four_surface, self.__get_border_colour(), # hold bottom border
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - 7 * self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH, self.pgconfig.MATRIX_SCREEN_CENTER_Y + 4 * self.pgconfig.GRID_SIZE),
                        (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH, self.pgconfig.MATRIX_SCREEN_CENTER_Y + 4 * self.pgconfig.GRID_SIZE),
                        self.pgconfig.BORDER_WIDTH)

        pygame.draw.line(self.four_surface, self.__get_border_colour(), # hold top border
            (self.pgconfig.MATRIX_SCREEN_CENTER_X - 7 * self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE // 2 - 1),
            (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE // 2 - 1),
            self.pgconfig.GRID_SIZE)
        
            
        hold_text_surface = self.hun2_big.render('HOLD', True, (0, 0, 0))
        self.surfaces.append((hold_text_surface, (self.pgconfig.MATRIX_SCREEN_CENTER_X - self.pgconfig.GRID_SIZE * 7, self.pgconfig.MATRIX_SCREEN_CENTER_Y + self.pgconfig.GRID_SIZE * 0.15)))
        
    def draw_danger_crosses(self, matrix: Matrix):
        """
        Draw crosses on the danger matrix
        
        args:
        matrix (Matrix): the matrix to draw the crosses on
        """
        offset = self.pgconfig.GRID_SIZE // 5
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if value == -1:
                    start_x = self.pgconfig.MATRIX_SCREEN_CENTER_X + j * self.pgconfig.GRID_SIZE + offset
                    start_y = self.pgconfig.MATRIX_SCREEN_CENTER_Y + i * self.pgconfig.GRID_SIZE - self.pgconfig.MATRIX_SURFACE_HEIGHT + offset
                    end_x = self.pgconfig.MATRIX_SCREEN_CENTER_X + (j + 1) * self.pgconfig.GRID_SIZE - offset
                    end_y = self.pgconfig.MATRIX_SCREEN_CENTER_Y + (i + 1) * self.pgconfig.GRID_SIZE - self.pgconfig.MATRIX_SURFACE_HEIGHT - offset
                    
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
                          
    def __render_matrix(self, four):
        """
        Render the matrix onto the window
        
        args:
        MATRIX (Matrix): The matrix object that contains the blocks
        """
        matrix_surface_rect = pygame.Rect(self.pgconfig.MATRIX_SCREEN_CENTER_X, self.pgconfig.MATRIX_SCREEN_CENTER_Y, self.pgconfig.MATRIX_SURFACE_WIDTH, self.pgconfig.MATRIX_SURFACE_HEIGHT)
        
        self.__draw_blocks(four.matrix.ghost, matrix_surface_rect, transparent = True, alpha = 0.33)
        self.__draw_grid(matrix_surface_rect)
        self.__draw_blocks(four.matrix.matrix, matrix_surface_rect, transparent = False, alpha = 1)
        self.__draw_blocks(four.matrix.piece, matrix_surface_rect, transparent = False, alpha = 1)
        
        if self.danger:
            self.draw_danger_crosses(four.matrix.danger)
        
        self.__draw_matrix_border() 
        
    
    def __render_queue(self, four):
        """
        Render the queue onto the window
        """
        queue_rect = self.__queue_rect(four.queue.length)
        pygame.draw.rect(self.four_surface, (0, 0, 0), queue_rect)
        for idx, tetromino in enumerate(four.queue.queue):
            
            # split queue_rect into four.queue.length number of rows
            row_height = queue_rect.height // four.queue.length
            row_y = queue_rect.y + idx * row_height
            
            preview_rect = pygame.Rect(queue_rect.x, row_y, queue_rect.width, row_height)
            self.__render_tetromino_preview(tetromino, preview_rect)
            self.__draw_queue_border()
       
    def __queue_rect(self, queue_length):
        """
        Get the rectangle for the queue
        """
        rect_x = self.pgconfig.MATRIX_SCREEN_CENTER_X + self.pgconfig.MATRIX_SURFACE_WIDTH + self.pgconfig.BORDER_WIDTH
        rect_y =  self.pgconfig.MATRIX_SCREEN_CENTER_Y + 1 * self.pgconfig.GRID_SIZE
        rect_width = 6 * self.pgconfig.GRID_SIZE
        rect_height = 3 * queue_length * self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH // 2
    
        return pygame.Rect(rect_x, rect_y, rect_width, rect_height)	
        
    def __hold_rect(self):
        """
        Get the rectangle for the hold
        """
        rect_x = self.pgconfig.MATRIX_SCREEN_CENTER_X - 7 * self.pgconfig.GRID_SIZE
        rect_y =  self.pgconfig.MATRIX_SCREEN_CENTER_Y + 1 * self.pgconfig.GRID_SIZE
        rect_width = 6 * self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH
        rect_height = 3 * self.pgconfig.GRID_SIZE - self.pgconfig.BORDER_WIDTH // 2
    
        return pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    
    def __render_hold(self, four):
        """
        Render the hold onto the window
        """
        tetromino = four.held_tetromino    
        hold_rect = self.__hold_rect()
        pygame.draw.rect(self.four_surface, (0, 0, 0), hold_rect)
        if tetromino is not None:
            self.__render_tetromino_preview(tetromino, hold_rect)
        self.__draw_hold_border()
    
    def __render_tetromino_preview(self, tetromino, rect):
        """
        Render a tetromino preview
        
        args:
        tetromino (list): the type of tetromino to render
        rect (pygame.Rect): the rectangle to draw the tetromino in
        """
        tetromino = get_tetromino_blocks(tetromino)
        tetromino_height = len(tetromino) * self.pgconfig.GRID_SIZE
        tetromino_width = len(tetromino[0]) * self.pgconfig.GRID_SIZE

        offset_x = (rect.width - tetromino_width) // 2
        offset_y = (rect.height - tetromino_height) // 2

        for i, row in enumerate(tetromino):
            for j, value in enumerate(row):
                if value != 0:
                    colour = self.pgconfig.COLOUR_MAP[value]
                    pygame.draw.rect(self.four_surface, colour, 
                                    (rect.x + offset_x + j * self.pgconfig.GRID_SIZE, rect.y + offset_y + i * self.pgconfig.GRID_SIZE, self.pgconfig.GRID_SIZE, self.pgconfig.GRID_SIZE)
                                    )
    
    def __draw_debug(self, debug):
       
        if debug['TPS'] < self.pgconfig.TPS * 0.95:
            tps_colour = (255, 0, 0)
        else:
            tps_colour = (0, 255, 0)
            
        if debug['FPS'] < self.pgconfig.FPS * 0.95:
            fps_colour = (255, 255, 0)
        elif debug['FPS'] < self.pgconfig.FPS * 0.5:
            fps_colour = (255, 0, 0)
        elif self.pgconfig.UNCAPPED_FPS:
            fps_colour = (0, 255, 255)
        else: 
            fps_colour = (0, 255, 0)
      
        if self.pgconfig.UNCAPPED_FPS:
            text_surface_fps = self.hun2_big.render(f'FPS: {int(debug['FPS'])} (UNCAPPED)', True, fps_colour)
        else:
            text_surface_fps = self.hun2_big.render(f'FPS: {int(debug['FPS'])}', True, fps_colour)
            
        text_surface_worst_fps = self.pfw_small.render(f'{int(debug["WORST_FPS"])} worst', True, fps_colour)
        
        text_surface_render_time = self.hun2_small.render(f'Render Time: {get_prefix(debug["REN_T"], 's')}', True, fps_colour)
        
        text_surface_worst_render_time = self.pfw_small.render(f'{get_prefix(debug["WORST_REN_T"], 's')} worst', True, fps_colour)
         
        text_surface_tps = self.hun2_big.render(f'TPS: {int(debug['TPS'])}', True, tps_colour)
        
        text_surface_worst_tps = self.pfw_small.render(f'{int(debug["WORST_TPS"])} worst', True, tps_colour)
        
        text_surface_subframe_time = self.hun2_small.render(f'Execution Time: {get_prefix(debug["SIM_T"], 's')}', True, tps_colour)
        
        text_surface_worst_subframe_time = self.pfw_small.render(f'{get_prefix(debug["WORST_SIM_T"], 's')} worst', True, tps_colour)
    
        text_surface_df = self.hun2_small.render(f'df: {debug["DF"]}', True, tps_colour)

        text_surface_worst_df = self.pfw_small.render(f'{debug["WORST_DF"]} worst', True, tps_colour)
        
        text_surface_subframe_count = self.hun2_small.render(f'Tick: {debug["TICKCOUNT"]}', True, tps_colour)

        debug_surfaces = [
            (text_surface_fps, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE // 2)),
            (text_surface_worst_fps, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 1.5)),
            (text_surface_render_time, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 2)),
            (text_surface_worst_render_time, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 2.5)),
            (text_surface_tps, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 3.5)),
            (text_surface_worst_tps, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 4.5)),
            (text_surface_subframe_time, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 5)),
            (text_surface_worst_subframe_time, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 5.5)),
            (text_surface_df, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 6)),
            (text_surface_worst_df, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 6.5)),
            (text_surface_subframe_count, (self.pgconfig.GRID_SIZE//2, self.pgconfig.GRID_SIZE * 7)),
        ]
        
        for surface, coords in debug_surfaces:
            self.window.blit(surface, coords)
        
       
   
        
            
