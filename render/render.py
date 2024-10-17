from instance.matrix import Matrix
import pygame
from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from utils import lerpBlendRGBA, Font, get_tetromino_blocks, get_prefix, smoothstep, Vec2

class Render():
    def __init__(self, window:pygame.Surface, Config:StructConfig, RenderStruct:StructRender, Flags:StructFlags, GameInstanceStruct:StructGameInstance, TimingStruct, DebugStruct):  
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
        
        self.board_rect_width = self.Config.MATRIX_SURFACE_WIDTH + 17 * self.Config.GRID_SIZE
        self.board_rect_height = self.Config.MATRIX_SURFACE_HEIGHT + self.Config.BORDER_WIDTH + 4 * self.Config.GRID_SIZE
        
        self.board_rect_x_pos = self.Config.WINDOW_WIDTH // 2 -  15.75 * self.Config.GRID_SIZE + self.Config.BORDER_WIDTH // 2
        self.board_rect_y_pos = 0
        
        self.matrix_rect_pos_x = self.board_rect_width //2 - self.Config.MATRIX_SURFACE_WIDTH //2 + self.Config.GRID_SIZE * 2 + self.Config.BORDER_WIDTH
        self.matrix_rect_pos_y = self.Config.GRID_SIZE * 4
        
        self.queue_rect_width = 6 * self.Config.GRID_SIZE + self.Config.BORDER_WIDTH // 2 + 1
        self.queue_rect_height = 3 * self.Config.QUEUE_LENGTH * self.Config.GRID_SIZE - self.Config.BORDER_WIDTH // 2
        
        self.hold_rect_width = 6 * self.Config.GRID_SIZE - self.Config.BORDER_WIDTH // 2
        self.hold_rect_height = 3 * self.Config.GRID_SIZE - self.Config.BORDER_WIDTH // 2
      
        self.window = window
        
        # fonts
        pygame.font.init()
        self.hun2_big = Font(self.Config.GRID_SIZE).hun2()
        self.hun2_med = Font(3 * self.Config.GRID_SIZE // 4).hun2()
        self.hun2_small = Font(self.Config.GRID_SIZE//2).hun2()
        self.pfw_small = Font(self.Config.GRID_SIZE//2).pfw()
        self.action_ui = Font(self.Config.GRID_SIZE).action_ui()
        
        self.MATRIX_SURFACE_WIDTH = self.Config.MATRIX_WIDTH * self.Config.GRID_SIZE
        self.MATRIX_SURFACE_HEIGHT = self.Config.MATRIX_HEIGHT // 2 * self.Config.GRID_SIZE
      
    def render_frame(self):
        """
        Render the frame of the Four Instance
        """
        self.RenderStruct.surfaces = []

        self.window.fill((0, 0, 0))
        
        self.board_rect = pygame.Rect(self.board_rect_x_pos, self.board_rect_y_pos, self.board_rect_width, self.board_rect_height)
        self.board_surface = pygame.Surface((self.board_rect.width, self.board_rect.height))
        self.RenderStruct.surfaces.append((self.board_surface, (self.board_rect_x_pos, self.board_rect_y_pos)))
        
        self.__render_matrix()
        self.__render_hold()
        self.__render_queue()
        self.__draw_UI_border()
        self.__draw_timer()
         
        for surface, coords in self.RenderStruct.surfaces:
            self.window.blit(surface, coords)
            
        # pygame.draw.rect(self.window, (0, 0, 255), self.board_rect, 2)  
        
        # pygame.draw.line(self.window, (255, 0, 255), (self.Config.WINDOW_WIDTH // 2, 0), (self.Config.WINDOW_WIDTH // 2, self.Config.WINDOW_HEIGHT), 1)
        # pygame.draw.line(self.window, (255, 0, 255), (0, self.Config.WINDOW_HEIGHT // 2), (self.Config.WINDOW_WIDTH, self.Config.WINDOW_HEIGHT // 2), 1)
        
        self.__draw_debug_menu()
        self.__draw_key_states()
        
        pygame.display.update()
    
    def draw_current_tetromino(self, matrix_surface_rect:pygame.Rect):
        
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.current_tetromino, self.GameInstanceStruct.current_tetromino.position, matrix_surface_rect)
        
        blend_colour = (0, 0, 0)
        piece_alpha = self.__get_alpha(self.GameInstanceStruct.current_tetromino.lock_delay_counter, self.GameInstanceStruct.lock_delay_in_ticks)
        
        self.__draw_tetromino_blocks(self.GameInstanceStruct.current_tetromino.blocks, rect, blend_colour, piece_alpha)
        
        if self.RenderStruct.draw_bounding_box:
            pygame.draw.rect(self.window, (0, 255, 0), rect, 2)
        
        if self.RenderStruct.draw_origin:
            self.__draw_tetromino_position()
              
        if self.RenderStruct.draw_pivot:
            self.__draw_pivot_position()
                
    def draw_current_tetromino_shadow(self, matrix_surface_rect:pygame.Rect):
            
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        if self.GameInstanceStruct.current_tetromino.shadow_position.y <= self.GameInstanceStruct.current_tetromino.position.y:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.current_tetromino, self.GameInstanceStruct.current_tetromino.shadow_position, matrix_surface_rect)
        
        blend_colour = (0, 0, 0)
        piece_alpha = 0.33
        
        self.__draw_tetromino_blocks(self.GameInstanceStruct.current_tetromino.blocks, rect, blend_colour, piece_alpha)
    
    def draw_next_tetromino(self, matrix_surface_rect:pygame.Rect):
        
        if self.GameInstanceStruct.next_tetromino is None:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.next_tetromino, self.GameInstanceStruct.next_tetromino.position, matrix_surface_rect)
        
        self.__draw_danger_crosses(self.GameInstanceStruct.next_tetromino.blocks, rect)
            
    def __get_rect(self, tetromino, position, matrix_surface_rect):
        
        tetromino_rect_length = self.Config.GRID_SIZE * len(tetromino.blocks[0])
        tetromino_rect_width = self.Config.GRID_SIZE * len(tetromino.blocks[1])
        
        tetromino_position_x =  matrix_surface_rect.x + position.x * self.Config.GRID_SIZE
        tetromino_position_y = matrix_surface_rect.y + position.y * self.Config.GRID_SIZE - (self.Config.MATRIX_HEIGHT * self.Config.GRID_SIZE)//2 
        
        return pygame.Rect(tetromino_position_x, tetromino_position_y , tetromino_rect_length, tetromino_rect_width)    
    
    def __draw_tetromino_blocks(self, tetromino_blocks, rect, blend_colour, alpha):
    
        for i, row in enumerate(tetromino_blocks):
            for j, value in enumerate(row):
                if value != 0:
                    if self.FlagStruct.GAME_OVER:
                        colour = lerpBlendRGBA(self.Config.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    else:
                        colour = self.Config.COLOUR_MAP[value]
                    pygame.draw.rect(
                        self.board_surface, lerpBlendRGBA(blend_colour, colour, alpha),
                        (rect.x + j * self.Config.GRID_SIZE, rect.y + i * self.Config.GRID_SIZE, self.Config.GRID_SIZE, self.Config.GRID_SIZE)
                    )
                    
    def __get_alpha(self, lock_delay_counter, lock_delay_in_ticks):
        if lock_delay_in_ticks == 0:
            return 1
        
        progress = lock_delay_counter / lock_delay_in_ticks
        smooth_progress = smoothstep(progress)
        alpha = 1 - max(0, min(0.25, smooth_progress))
        return alpha

    def __draw_danger_crosses(self, tetromino_blocks, rect):
        
        offset = self.Config.GRID_SIZE // 5
        thickness = 5
        
        for i, row in enumerate(tetromino_blocks):
            for j, value in enumerate(row):
                if value != 0:
                    pygame.draw.line(self.board_surface, (255, 0, 0), 
                                     (rect.x + j * self.Config.GRID_SIZE + offset, rect.y + i * self.Config.GRID_SIZE + offset), 
                                     (rect.x + (j + 1) * self.Config.GRID_SIZE - offset, rect.y + (i + 1) * self.Config.GRID_SIZE - offset), thickness)
                    
                    pygame.draw.line(self.board_surface, (255, 0, 0), 
                                     (rect.x + (j + 1) * self.Config.GRID_SIZE - offset, rect.y + i * self.Config.GRID_SIZE + offset), 
                                     (rect.x + j * self.Config.GRID_SIZE + offset, rect.y + (i + 1) * self.Config.GRID_SIZE - offset), thickness)
                   
    def __draw_grid(self, matrix_surface_rect:pygame.Rect):
        """
        Draw the grid in the background of the matrix
        
        args:
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        grid_colour = lerpBlendRGBA((0, 0, 0), self.__get_border_colour(), 0.25)
        
        for idx in range(self.Config.MATRIX_HEIGHT // 2, self.Config.MATRIX_HEIGHT + 1):
            pygame.draw.line(self.board_surface, grid_colour,
                             (matrix_surface_rect.x, matrix_surface_rect.y + idx * self.Config.GRID_SIZE - self.Config.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + self.Config.MATRIX_WIDTH * self.Config.GRID_SIZE, matrix_surface_rect.y + idx * self.Config.GRID_SIZE - self.Config.MATRIX_SURFACE_HEIGHT)
                             )
            
        for idx in range(self.Config.MATRIX_WIDTH + 1):
            pygame.draw.line(self.board_surface, grid_colour,
                             (matrix_surface_rect.x + idx * self.Config.GRID_SIZE, matrix_surface_rect.y + self.Config.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + idx * self.Config.GRID_SIZE, matrix_surface_rect.y + self.Config.MATRIX_HEIGHT // 2 * self.Config.GRID_SIZE - self.Config.MATRIX_SURFACE_HEIGHT)
                             )
            
    def __draw_matrix_blocks(self, matrix:Matrix, matrix_surface_rect:pygame.Rect):
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
                        colour = lerpBlendRGBA(self.Config.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    else:
                        colour = self.Config.COLOUR_MAP[value]
            
                    pygame.draw.rect(
                        self.board_surface, colour, 
                        (matrix_surface_rect.x + j * self.Config.GRID_SIZE, matrix_surface_rect.y + i * self.Config.GRID_SIZE - self.Config.MATRIX_SURFACE_HEIGHT, self.Config.GRID_SIZE, self.Config.GRID_SIZE)
                        )
    
    def __draw_UI_border(self):
        """
        Draw a border around the matrix, garbage, queue and hold
        """
        # ====== MATRIX ======
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # matrix left border
                 (self.matrix_rect_pos_x - self.Config.BORDER_WIDTH // 2 - 1, self.Config.MATRIX_SURFACE_HEIGHT + self.matrix_rect_pos_y), 
                 (self.matrix_rect_pos_x - self.Config.BORDER_WIDTH // 2 - 1, self.matrix_rect_pos_y), self.Config.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(),   # matrix right border
                        (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + self.Config.BORDER_WIDTH // 2, self.matrix_rect_pos_y), 
                        (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + self.Config.BORDER_WIDTH // 2, self.matrix_rect_pos_y + self.Config.MATRIX_SURFACE_HEIGHT - 1), 
                        self.Config.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(),  # matrix bottom border
                        (self.matrix_rect_pos_x  - self.Config.BORDER_WIDTH - self.Config.GRID_SIZE, self.matrix_rect_pos_y + self.Config.MATRIX_SURFACE_HEIGHT + self.Config.BORDER_WIDTH // 2 - 1), 
                        (self.matrix_rect_pos_x  + self.Config.MATRIX_SURFACE_WIDTH + self.Config.BORDER_WIDTH - 1, self.matrix_rect_pos_y + self.Config.MATRIX_SURFACE_HEIGHT + self.Config.BORDER_WIDTH // 2 - 1), 
                        self.Config.BORDER_WIDTH)

        # ====== GARBAGE =======
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # left garbage border
                        (self.matrix_rect_pos_x - self.Config.BORDER_WIDTH // 2 - 1 - self.Config.GRID_SIZE, self.matrix_rect_pos_y), 
                        (self.matrix_rect_pos_x  - self.Config.BORDER_WIDTH // 2 - 1 - self.Config.GRID_SIZE, self.matrix_rect_pos_y + self.Config.MATRIX_SURFACE_HEIGHT - 1), 
                        self.Config.BORDER_WIDTH)
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(),  
                        (self.matrix_rect_pos_x  - self.Config.BORDER_WIDTH - self.Config.GRID_SIZE, self.matrix_rect_pos_y + self.Config.MATRIX_SURFACE_HEIGHT - self.Config.GRID_SIZE * 8 + self.Config.BORDER_WIDTH // 2 - 1) , 
                        (self.matrix_rect_pos_x - self.Config.BORDER_WIDTH , self.matrix_rect_pos_y+ self.Config.MATRIX_SURFACE_HEIGHT - self.Config.GRID_SIZE * 8 + self.Config.BORDER_WIDTH // 2 - 1), 
                        self.Config.BORDER_WIDTH)
        
    def __draw_queue_border(self):

        match self.Config.QUEUE_LENGTH:
            case 1:
                queue_size = self.Config.GRID_SIZE * 4.5
            case 2: 
                queue_size = self.Config.GRID_SIZE * 7.5
            case 3:
                queue_size = self.Config.GRID_SIZE * 10.5
            case 4:
                queue_size = self.Config.GRID_SIZE * 13.5
            case 5:
                queue_size = self.Config.GRID_SIZE * 16.5
            case 6:
                queue_size = self.Config.GRID_SIZE * 19.5
            case _:
                queue_size = self.Config.GRID_SIZE * 19.5
      
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # queue left border
                        (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + 6 * self.Config.GRID_SIZE + self.Config.BORDER_WIDTH, self.matrix_rect_pos_y + self.Config.GRID_SIZE // 2 - 1),
                        (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + 6 * self.Config.GRID_SIZE + self.Config.BORDER_WIDTH, self.matrix_rect_pos_y + queue_size - self.Config.GRID_SIZE // 2 - 1),
                        self.Config.BORDER_WIDTH)
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # queue bottom border
                (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + self.Config.BORDER_WIDTH + 6 * self.Config.GRID_SIZE  + self.Config.BORDER_WIDTH // 2, self.matrix_rect_pos_y + queue_size - self.Config.GRID_SIZE // 2 - 1),
                (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + self.Config.BORDER_WIDTH // 2, self.matrix_rect_pos_y + queue_size - self.Config.GRID_SIZE // 2 - 1),
                self.Config.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(), # queue top border
                        (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + self.Config.BORDER_WIDTH + 6 * self.Config.GRID_SIZE  + self.Config.BORDER_WIDTH // 2, self.matrix_rect_pos_y + self.Config.GRID_SIZE // 2 - 1),
                        (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH + self.Config.BORDER_WIDTH // 2, self.matrix_rect_pos_y + self.Config.GRID_SIZE // 2 - 1),
                        self.Config.GRID_SIZE)
    
        text_surface = self.hun2_big.render('NEXT', True, (0, 0, 0))
        self.board_surface.blit(text_surface, (self.matrix_rect_pos_x + self.Config.MATRIX_SURFACE_WIDTH // 2 + self.Config.GRID_SIZE * 5.25, self.matrix_rect_pos_y + self.Config.GRID_SIZE * 0.15))
        
    def __draw_hold_border(self):
    
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # hold left border
                        (self.matrix_rect_pos_x - 7 * self.Config.GRID_SIZE - self.Config.BORDER_WIDTH //2 - 1, self.matrix_rect_pos_y + self.Config.GRID_SIZE // 2 - 1),
                        (self.matrix_rect_pos_x - 7 * self.Config.GRID_SIZE - self.Config.BORDER_WIDTH //2 - 1, self.matrix_rect_pos_y + 4 * self.Config.GRID_SIZE),
                        self.Config.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(), # hold bottom border
                        (self.matrix_rect_pos_x - 7 * self.Config.GRID_SIZE - self.Config.BORDER_WIDTH, self.matrix_rect_pos_y + 4 * self.Config.GRID_SIZE),
                        (self.matrix_rect_pos_x - self.Config.GRID_SIZE - self.Config.BORDER_WIDTH, self.matrix_rect_pos_y + 4 * self.Config.GRID_SIZE),
                        self.Config.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(), # hold top border
            (self.matrix_rect_pos_x - 7 * self.Config.GRID_SIZE - self.Config.BORDER_WIDTH, self.matrix_rect_pos_y + self.Config.GRID_SIZE // 2 - 1),
            (self.matrix_rect_pos_x - self.Config.GRID_SIZE - self.Config.BORDER_WIDTH, self.matrix_rect_pos_y + self.Config.GRID_SIZE // 2 - 1),
            self.Config.GRID_SIZE)
        
            
        text_surface = self.hun2_big.render('HOLD', True, (0, 0, 0))
        self.board_surface.blit(text_surface, (self.matrix_rect_pos_x - 7.25 * self.Config.GRID_SIZE + self.Config.GRID_SIZE * 0.25, self.matrix_rect_pos_y + self.Config.GRID_SIZE * 0.15))
        
    def __get_border_colour(self):
        """
        Get the colour of the border
        """
        if self.FlagStruct.DANGER:
            return (255, 0, 0)
        else:
            return (255, 255, 255)
                          
    def __render_matrix(self):
        """
        Render the matrix, current tetromino and its shadow onto the window
        
        args:
            four (Four): the Four instance to render
        """

        matrix_rect = pygame.Rect(self.matrix_rect_pos_x, self.matrix_rect_pos_y, self.Config.MATRIX_SURFACE_WIDTH, self.Config.MATRIX_SURFACE_HEIGHT)
        
        self.draw_current_tetromino_shadow(matrix_rect)
        self.__draw_grid(matrix_rect)
        self.__draw_matrix_blocks(self.GameInstanceStruct.matrix.matrix, matrix_rect)
        self.draw_current_tetromino(matrix_rect)
        
        if self.FlagStruct.DANGER:
            self.draw_next_tetromino(matrix_rect)

    def __render_queue(self):
        """
        Render the queue onto the window
        
        args0
            four (Four): the Four instance to render
        """
        queue_rect = self.__queue_rect()
        pygame.draw.rect(self.board_surface, (0, 2, 0), queue_rect)
        
        for idx, tetromino in enumerate(self.GameInstanceStruct.queue.queue):
            
            # split queue_rect into four.queue.length number of rows
            row_height = queue_rect.height // self.GameInstanceStruct.queue.length
            row_y = queue_rect.y + idx * row_height
            
            preview_rect = pygame.Rect(queue_rect.x, row_y, queue_rect.width, row_height)
            self.__render_tetromino_preview(tetromino, preview_rect)
            self.__draw_queue_border()
       
    def __queue_rect(self):
        """
        Get the rectangle for the queue
        """
        rect_x = self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH // 2 + self.queue_rect_width - self.Config.GRID_SIZE
        rect_y =  self.matrix_rect_pos_y + 1 * self.Config.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.queue_rect_width, self.queue_rect_height)	
        
    def __hold_rect(self):
        """
        Get the rectangle for the hold
        """
        rect_x = self.matrix_rect_pos_x - 7 * self.Config.GRID_SIZE
        rect_y =  self.matrix_rect_pos_y + 1 * self.Config.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.hold_rect_width, self.hold_rect_height)
    
    def __render_hold(self):
        """
        Render the hold onto the window
        
        args:
            four (Four): the Four instance
        """
        tetromino = self.GameInstanceStruct.held_tetromino    
        hold_rect = self.__hold_rect()
        pygame.draw.rect(self.board_surface, (0, 0, 0), hold_rect)
        
        self.__render_tetromino_preview(tetromino, hold_rect, can_hold = self.GameInstanceStruct.can_hold)
        self.__draw_hold_border()
    
    def __render_tetromino_preview(self, tetromino, rect, can_hold = True):
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
        
        tetromino_height = len(tetromino) * self.Config.GRID_SIZE
        tetromino_width = len(tetromino[0]) * self.Config.GRID_SIZE

        offset_x = (rect.width - tetromino_width) // 2
        offset_y = (rect.height - tetromino_height) // 2

        for i, row in enumerate(tetromino):
            for j, value in enumerate(row):
                if value != 0:
                    if can_hold:
                        colour = self.Config.COLOUR_MAP[value]
                    else:
                        colour = lerpBlendRGBA(self.Config.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    
                    pygame.draw.rect(self.board_surface, colour, 
                                    (rect.x + offset_x + j * self.Config.GRID_SIZE, rect.y + offset_y + i * self.Config.GRID_SIZE, self.Config.GRID_SIZE, self.Config.GRID_SIZE)
                                    )
                    
    def __draw_debug_menu(self):
        """
        Draw the debug information onto the window
        """
        if not self.FlagStruct.SHOW_DEBUG_MENU:
            return
        
        debug_surfaces = []

        if self.DebugStruct.Average_FrameRate < self.Config.FPS * 0.95:
            fps_colour = (255, 255, 0)
        elif self.DebugStruct.Average_FrameRate < self.Config.FPS * 0.5:
            fps_colour = (255, 0, 0)
        elif self.Config.UNCAPPED_FPS:
            fps_colour = (0, 255, 255)
        else:
            fps_colour = (0, 255, 0)

        # FPS debug information
        fps_text = f'FPS: {int(self.DebugStruct.Average_FrameRate)}'
        
        if self.Config.UNCAPPED_FPS:
            fps_text += ' (UNCAPPED)'
            
        debug_surfaces.append((self.hun2_big.render(fps_text, True, fps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE // 2)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_FrameRate)} | best: {int(self.DebugStruct.Best_FrameRate)} | current: {int(self.DebugStruct.Current_FrameRate)}', True, fps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 1.5)))

        debug_surfaces.append((self.hun2_small.render(f'Render Time: {get_prefix(self.DebugStruct.Average_RenderTime, "s")}', True, fps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 2)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_RenderTime, "s")} | best: {get_prefix(self.DebugStruct.Best_RenderTime, "s")} | current: {get_prefix(self.DebugStruct.Current_RenderTime, "s")}', True, fps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 2.5)))

        if self.DebugStruct.Average_TickRate < self.Config.TPS * 0.95:
            tps_colour = (255, 0, 0)
        else:
            tps_colour = (0, 255, 0)

        # # TPS debug information
        debug_surfaces.append((self.hun2_big.render(f'TPS: {int(self.DebugStruct.Average_TickRate)}', True, tps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 3.5)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_TickRate)} | best: {int(self.DebugStruct.Best_TickRate)} | current: {int(self.DebugStruct.Current_TickRate)}', True, tps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 4.5)))

        debug_surfaces.append((self.hun2_small.render(f'Execution Time: {get_prefix(self.DebugStruct.Average_ExecutionTime, "s")}', True, tps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 5)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_ExecutionTime, "s")} | best: {get_prefix(self.DebugStruct.Best_ExecutionTime, "s")} | current: {get_prefix(self.DebugStruct.Current_ExecutionTime, "s")}', True, tps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 5.5)))

        debug_surfaces.append((self.hun2_small.render(f'df: {self.DebugStruct.Average_DeltaTick:.2f}', True, tps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 6)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {self.DebugStruct.Worst_DeltaTick} | best: {self.DebugStruct.Best_DeltaTick} | current: {int(self.DebugStruct.Current_DeltaTick)}', True, tps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 6.5)))

        debug_surfaces.append((self.hun2_small.render(f'Tick: {self.DebugStruct.TickCounter}', True, tps_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 7)))
        
        # handling debug information
        
        if self.DebugStruct.Average_PollingRate < self.Config.POLLING_RATE * 0.95:
            poll_colour = (255, 0, 0)
        else:
            poll_colour = (0, 255, 0)
        
        debug_surfaces.append((self.hun2_big.render(f'POLL: {int(self.DebugStruct.Average_PollingRate)}', True, poll_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 8)))
        
        debug_surfaces.append((self.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_PollingRate)} | best: {int(self.DebugStruct.Best_PollingRate)} | current: {int(self.DebugStruct.Current_PollingRate)}', True, poll_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 9)))
        
        debug_surfaces.append((self.hun2_small.render(f'Polling Time: {get_prefix(self.DebugStruct.Average_PollingTime, "s")}', True, poll_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 9.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_PollingTime, "s")} | best: {get_prefix(self.DebugStruct.Best_PollingTime, "s")} | current: {get_prefix(self.DebugStruct.Current_PollingTime, "s")}', True, poll_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 10)))

        das_colour = (255, 255, 255)

        debug_surfaces.append((self.hun2_big.render(f'DAS: {int(self.DebugStruct.DAS_Left_Counter)} ms {int(self.DebugStruct.DAS_Right_Counter)} ms', True, das_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 11)))
        
        debug_surfaces.append((self.hun2_small.render(f'Threshold: {self.DebugStruct.DAS_Threshold} ms', True, das_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 12)))
        
        debug_surfaces.append((self.pfw_small.render(f'DCD: {self.DebugStruct.DCD} | DAS Cancel: {self.DebugStruct.DAS_Cancel} | Direction: {self.DebugStruct.Prioritise_Direction} (Priority: {self.DebugStruct.Direction})', True, das_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 12.5)))
        
        arr_colour = (255, 255, 255)
        
        debug_surfaces.append((self.hun2_big.render(f'ARR: {int(self.DebugStruct.ARR_Left_Counter)} ms {int(self.DebugStruct.ARR_Right_Counter)} ms', True, arr_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 13.5)))
        
        debug_surfaces.append((self.hun2_small.render(f'Threshold: {self.DebugStruct.ARR_Threshold} ms', True, arr_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 14.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'SDF: { self.DebugStruct.Soft_Drop_Factor} | PrefSD: {self.DebugStruct.Prefer_Soft_Drop} | On Floor: {self.DebugStruct.On_Floor}', True, (255, 255, 255)), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 15.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'Gravity: {self.DebugStruct.Gravity:.2f} G ({self.DebugStruct.G_in_ticks} ticks) | Multi: {self.DebugStruct.Gravity_Multiplier} | Counter: {self.DebugStruct.Gravity_Counter}', True, (255, 255, 255)), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 16)))
    
        debug_surfaces.append((self.pfw_small.render(f'Lock Delay: {self.DebugStruct.Lock_Delay} ({self.DebugStruct.Lock_Delay_Ticks} ticks) | Counter: {self.DebugStruct.Lock_Delay_Counter} | Resets Left: {self.DebugStruct.Max_Moves} | y: {self.DebugStruct.Lowest_Pivot}', True, (255, 255, 255)), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 16.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'PrevAccHD: {self.DebugStruct.Prevent_Accidental_Hard_Drop} | Delay: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Time} ticks| Counter: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Counter} | Flag: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Flag}', True, (255, 255, 255)), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 17)))
          
        for surface, coords in debug_surfaces:
            self.window.blit(surface, coords)

    def __draw_key_states(self):
        """
        Draw the key states onto the window
        """
        if self.RenderStruct.key_dict is None:
            return
        
        key_surfaces = []
        
        left_colour = (255, 255, 255)       if self.RenderStruct.key_dict['KEY_LEFT']               else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        right_colour = (255, 255, 255)      if self.RenderStruct.key_dict['KEY_RIGHT']              else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.3)
        softdrop_colour = (255, 255, 255)   if self.RenderStruct.key_dict['KEY_SOFT_DROP']          else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        ccw_colour = (255, 255, 255)        if self.RenderStruct.key_dict['KEY_COUNTERCLOCKWISE']   else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        cw_colour = (255, 255, 255)         if self.RenderStruct.key_dict['KEY_CLOCKWISE']          else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        colour_180 = (255, 255, 255)        if self.RenderStruct.key_dict['KEY_180']                else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        harddrop_colour = (255, 255, 255)   if self.RenderStruct.key_dict['KEY_HARD_DROP']          else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        hold_colour = (255, 255, 255)       if self.RenderStruct.key_dict['KEY_HOLD']               else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        
        key_surfaces.append((self.action_ui.render('B', True, left_colour), (self.Config.GRID_SIZE // 2, self.Config.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('A', True, right_colour), (self.Config.GRID_SIZE *2 , self.Config.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('C', True, softdrop_colour), (self.Config.GRID_SIZE * 3.5, self.Config.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('G', True, harddrop_colour), (self.Config.GRID_SIZE * 5, self.Config.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('E', True, ccw_colour), (self.Config.GRID_SIZE * 6.5, self.Config.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('D', True, cw_colour), (self.Config.GRID_SIZE * 8, self.Config.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('F', True, colour_180), (self.Config.GRID_SIZE * 9.5, self.Config.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('H', True, hold_colour), (self.Config.GRID_SIZE * 11, self.Config.GRID_SIZE * 26.5))) 
        
        for surface, coords in key_surfaces:
            self.window.blit(surface, coords)
    
    def __draw_pivot_position(self):
        
        loc = self.GameInstanceStruct.current_tetromino.position + self.GameInstanceStruct.current_tetromino.pivot
        
        x = self.Config.MATRIX_SCREEN_CENTER_X + loc.x * self.Config.GRID_SIZE 
        y = self.Config.MATRIX_SCREEN_CENTER_Y + loc.y * self.Config.GRID_SIZE - (self.Config.MATRIX_HEIGHT * self.Config.GRID_SIZE)//2

        length = self.Config.GRID_SIZE // 4

        pygame.draw.line(self.window, (255, 255, 255), (x - length, y), (x + length, y), 2)
        pygame.draw.line(self.window, (255, 255, 255), (x, y - length), (x, y + length), 2)
                
    def __draw_tetromino_position(self):
        loc = self.GameInstanceStruct.current_tetromino.position
        
        x = self.Config.MATRIX_SCREEN_CENTER_X + loc.x * self.Config.GRID_SIZE
        y = self.Config.MATRIX_SCREEN_CENTER_Y + loc.y * self.Config.GRID_SIZE - (self.Config.MATRIX_HEIGHT * self.Config.GRID_SIZE)//2 
        
        length = self.Config.GRID_SIZE // 4

        pygame.draw.line(self.window, (0, 255, 0), (x - length, y), (x + length, y), 2)
        pygame.draw.line(self.window, (0, 255, 0), (x, y - length), (x, y + length), 2)
    
    def __format_time(self):
        minutes = int((self.TimingStruct.current_time % 3600) // 60)
        seconds = int(self.TimingStruct.current_time % 60)
        milliseconds = int((self.TimingStruct.current_time % 1) * 1000)
        time_minsec = f"{minutes}:{seconds:02}"
        time_ms = f"{milliseconds:03}"
        return time_minsec, time_ms
    
    def __draw_timer(self): 
        pass
    #     if not self.FlagStruct.GAME_OVER:
    #         self.time_minsec, self.time_ms = self.__format_time()
            
    #     self.RenderStruct.surfaces.append((self.hun2_med.render('Time', True, (255, 255, 255)), (self.Config.GRID_SIZE * 4.33, self.Config.GRID_SIZE * 22.33)))
    #     self.RenderStruct.surfaces.append((self.hun2_big.render(f'{self.time_minsec}.', True, (255, 255, 255)), (self.Config.GRID_SIZE * 4.5 - (len(self.time_minsec) * self.Config.GRID_SIZE//2 + 1), self.Config.GRID_SIZE * 23.25)))
    #     self.RenderStruct.surfaces.append((self.hun2_med.render(f'{self.time_ms}', True, (255, 255, 255)), (self.Config.GRID_SIZE * 4.66, self.Config.GRID_SIZE * 23.45)))