import pygame.gfxdraw
from instance.matrix import Matrix
import pygame, math
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
        
        self.angle = 0
        
        self.BORDER_WIDTH = 7
        
        self.GRID_SIZE = self.Config.WINDOW_WIDTH // 46
        self.MATRIX_SURFACE_WIDTH = self.Config.MATRIX_WIDTH * self.GRID_SIZE
        self.MATRIX_SURFACE_HEIGHT = self.Config.MATRIX_HEIGHT // 2 * self.GRID_SIZE
        
        self.board_rect_width = self.MATRIX_SURFACE_WIDTH + 17 * self.GRID_SIZE
        self.board_rect_height = self.MATRIX_SURFACE_HEIGHT * 2 + self.BORDER_WIDTH + 4 * self.GRID_SIZE
        
        self.board_rect_x_pos = self.Config.WINDOW_WIDTH // 2 -  15.5 * self.GRID_SIZE 
        self.board_rect_y_pos = 0
         
        self.matrix_rect_pos_x = self.board_rect_width //2 - self.MATRIX_SURFACE_WIDTH //2 
        self.matrix_rect_pos_y = self.MATRIX_SURFACE_HEIGHT  + self.GRID_SIZE * 4 + self.BORDER_WIDTH // 2
        
        self.queue_rect_width = 6 * self.GRID_SIZE + self.BORDER_WIDTH // 2 + 1
        self.queue_rect_height = 3 * self.Config.QUEUE_LENGTH * self.GRID_SIZE - self.BORDER_WIDTH // 2
        
        self.hold_rect_width = 6 * self.GRID_SIZE - self.BORDER_WIDTH // 2
        self.hold_rect_height = 3 * self.GRID_SIZE - self.BORDER_WIDTH // 2
        
        # pivot
        self.board_center_x_board_space = self.board_rect_width // 2
        self.board_center_y_board_space = self.board_rect_height // 2 + 2 * self.GRID_SIZE + self.MATRIX_SURFACE_HEIGHT // 2
        
        # origin
        self.board_center_screen_pos_x = self.Config.WINDOW_WIDTH // 2 
        self.board_center_screen_pos_y = self.Config.WINDOW_HEIGHT // 2
      
        self.window = window
        
        # fonts
        pygame.font.init()
        self.hun2_big = Font(self.GRID_SIZE).hun2()
        self.hun2_med = Font(3 * self.GRID_SIZE // 4).hun2()
        self.hun2_small = Font(self.GRID_SIZE//2).hun2()
        self.pfw_small = Font(self.GRID_SIZE//2).pfw()
        self.action_ui = Font(self.GRID_SIZE).action_ui()
      
    def render_frame(self):
        """
        Render the frame of the Four Instance
        """
        self.RenderStruct.surfaces = []

        self.window.fill((0, 0, 0))
        
        self.board_surface = pygame.Surface((self.board_rect_width, self.board_rect_height), pygame.SRCALPHA)
        
        
        rect = self.board_surface.get_rect()
        pygame.draw.rect(self.board_surface, (0, 0, 255), rect, 2)
        
        self.__render_matrix()
        self.__render_hold()
        self.__render_queue()
        self.__draw_UI_border()
        self.__draw_timer()
    
        self.angle += 0.5
        offset_x, offset_y = 0, 0
        scale = math.sin(math.radians(self.angle))**2 + 0.1
    
        transformed_surface, transformed_rect = self.TransformSurface(self.board_surface, scale, self.angle, (self.board_center_x_board_space, self.board_center_y_board_space), (self.board_center_screen_pos_x, self.board_center_screen_pos_y), (offset_x, offset_y))
        self.RenderStruct.surfaces.append((transformed_surface, transformed_rect.topleft))
    
        for surface, coords in self.RenderStruct.surfaces:
            self.window.blit(surface, coords)
        
        if self.RenderStruct.draw_guide_lines:
            pygame.draw.line(self.window, (255, 0, 255), (self.Config.WINDOW_WIDTH // 2, 0), (self.Config.WINDOW_WIDTH // 2, self.Config.WINDOW_HEIGHT), 1)
            pygame.draw.line(self.window, (255, 0, 255), (0, self.Config.WINDOW_HEIGHT // 2), (self.Config.WINDOW_WIDTH, self.Config.WINDOW_HEIGHT // 2), 1)
            pygame.draw.line(self.window, (0, 255, 0), (self.Config.WINDOW_WIDTH // 4, 0), (self.Config.WINDOW_WIDTH // 4, self.Config.WINDOW_HEIGHT), 1)
            pygame.draw.line(self.window, (0, 255, 0), (0, self.Config.WINDOW_HEIGHT // 4), (self.Config.WINDOW_WIDTH, self.Config.WINDOW_HEIGHT // 4), 1)
            pygame.draw.line(self.window, (0, 255, 0), (self.Config.WINDOW_WIDTH // 4 * 3, 0), (self.Config.WINDOW_WIDTH // 4 * 3, self.Config.WINDOW_HEIGHT), 1)
            pygame.draw.line(self.window, (0, 255, 0), (0, self.Config.WINDOW_HEIGHT // 4 * 3), (self.Config.WINDOW_WIDTH, self.Config.WINDOW_HEIGHT // 4 * 3), 1)
    
        self.__draw_debug_menu()
        self.__draw_key_states()
        
        pygame.display.update()

    def RotateSurface(self, surf, angle, pivot, origin):
        """
        Rotate a surface around a pivot point.

        Args:
            surf (pygame.Surface): The surface to rotate.
            angle (float): The angle to rotate the surface.
            pivot (tuple): The pivot point to rotate around.
            origin (tuple): The origin point of the surface.

        Returns:
            pygame.Surface: The rotated surface.
            pygame.Rect: The rectangle of the rotated surface.
        """
        # Convert pivot and origin to pygame vectors for calculations
        pivot = pygame.Vector2(pivot)
        origin = pygame.Vector2(origin)
        
        surf_rect = surf.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
        offset_center_to_pivot = pygame.math.Vector2(origin) - surf_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_surface_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
        rotated_surface = pygame.transform.rotate(surf, angle)
        rotated_surface_rect = rotated_surface.get_rect(center = rotated_surface_center)
        
        return rotated_surface, rotated_surface_rect
    
    def ScaleSurface(self, surf, scale, pivot, origin):
        """
        Scale a surface around a pivot point.
        
        Args:
            surf (pygame.Surface): The surface to scale.
            scale (float): The scale factor.
            pivot (tuple): The pivot point to scale around.
            origin (tuple): The origin point of the surface.
        
        Returns:
            pygame.Surface: The scaled surface.
            pygame.Rect: The rectangle of the scaled surface.
        """
        pivot = pygame.Vector2(pivot)
        origin = pygame.Vector2(origin)
        surf_rect = surf.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
        offset_center_to_pivot = pygame.math.Vector2(origin) - surf_rect.center
        scaled_offset = offset_center_to_pivot * scale
        scaled_surface_center = (origin[0] - scaled_offset.x, origin[1] - scaled_offset.y)
        scaled_surface = pygame.transform.scale(surf, (int(surf.get_width() * scale), int(surf.get_height() * scale)))
        scaled_surface_rect = scaled_surface.get_rect(center = scaled_surface_center)
        
        return scaled_surface, scaled_surface_rect

    def TransformSurface(self, surf, scale, angle, pivot, origin, offset):
        pivot = pygame.Vector2(pivot)
        origin = pygame.Vector2(origin)
        offset = pygame.Vector2(offset)
        
        scaled_surface, _ = self.ScaleSurface(surf, scale, pivot, origin + offset)
        rotated_surface, rotated_surface_rect = self.RotateSurface(scaled_surface, angle, pivot * scale, origin + offset)
        return rotated_surface, rotated_surface_rect
        
        
    def draw_current_tetromino(self, matrix_surface_rect:pygame.Rect):
        
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.current_tetromino, self.GameInstanceStruct.current_tetromino.position, matrix_surface_rect)
        
        blend_colour = (0, 0, 0)
        piece_alpha = self.__get_alpha(self.GameInstanceStruct.current_tetromino.lock_delay_counter, self.GameInstanceStruct.lock_delay_in_ticks)
        
        self.__draw_tetromino_blocks(self.GameInstanceStruct.current_tetromino.blocks, rect, blend_colour, piece_alpha)
        
        if self.RenderStruct.draw_bounding_box:
            pygame.draw.rect(self.board_surface, (0, 255, 0), rect, 2)
        
        if self.RenderStruct.draw_origin:
            self.__draw_tetromino_position(matrix_surface_rect)
              
        if self.RenderStruct.draw_pivot:
            self.__draw_pivot_position(matrix_surface_rect)
                
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
        
        tetromino_rect_length = self.GRID_SIZE * len(tetromino.blocks[0])
        tetromino_rect_width = self.GRID_SIZE * len(tetromino.blocks[1])
        
        tetromino_position_x =  matrix_surface_rect.x + position.x * self.GRID_SIZE
        tetromino_position_y = matrix_surface_rect.y + position.y * self.GRID_SIZE - (self.Config.MATRIX_HEIGHT * self.GRID_SIZE)//2 
        
        return pygame.Rect(tetromino_position_x, tetromino_position_y , tetromino_rect_length, tetromino_rect_width)    
    
    def __draw_tetromino_blocks(self, tetromino_blocks, rect, blend_colour, alpha):
    
        for i, row in enumerate(tetromino_blocks):
            for j, value in enumerate(row):
                if value != 0:
                    if self.FlagStruct.GAME_OVER:
                        colour = lerpBlendRGBA(self.Config.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    else:
                        colour = self.Config.COLOUR_MAP[value]
                    pygame.gfxdraw.box(
                        self.board_surface, 
                        (rect.x + j * self.GRID_SIZE, rect.y + i * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE),
                        lerpBlendRGBA(blend_colour, colour, alpha)
                    )
                    
    def __get_alpha(self, lock_delay_counter, lock_delay_in_ticks):
        if lock_delay_in_ticks == 0:
            return 1
        
        progress = lock_delay_counter / lock_delay_in_ticks
        smooth_progress = smoothstep(progress)
        alpha = 1 - max(0, min(0.25, smooth_progress))
        return alpha

    def __draw_danger_crosses(self, tetromino_blocks, rect):
        
        offset = self.GRID_SIZE // 5
        thickness = 5
        
        for i, row in enumerate(tetromino_blocks):
            for j, value in enumerate(row):
                if value != 0:
                    pygame.draw.line(self.board_surface, (255, 0, 0), 
                                     (rect.x + j * self.GRID_SIZE + offset, rect.y + i * self.GRID_SIZE + offset), 
                                     (rect.x + (j + 1) * self.GRID_SIZE - offset, rect.y + (i + 1) * self.GRID_SIZE - offset), thickness)
                    
                    pygame.draw.line(self.board_surface, (255, 0, 0), 
                                     (rect.x + (j + 1) * self.GRID_SIZE - offset, rect.y + i * self.GRID_SIZE + offset), 
                                     (rect.x + j * self.GRID_SIZE + offset, rect.y + (i + 1) * self.GRID_SIZE - offset), thickness)
                   
    def __draw_grid(self, matrix_surface_rect:pygame.Rect):
        """
        Draw the grid in the background of the matrix
        
        args:
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        grid_colour = lerpBlendRGBA((0, 0, 0), self.__get_border_colour(), 0.25)
        width = 1
        
        for idx in range(self.Config.MATRIX_HEIGHT // 2, self.Config.MATRIX_HEIGHT + 1):
            pygame.draw.line(self.board_surface, grid_colour,
                             (matrix_surface_rect.x, matrix_surface_rect.y + idx * self.GRID_SIZE - self.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + self.Config.MATRIX_WIDTH * self.GRID_SIZE, matrix_surface_rect.y + idx * self.GRID_SIZE - self.MATRIX_SURFACE_HEIGHT),
                             width
                             )
            
        for idx in range(self.Config.MATRIX_WIDTH + 1):
            pygame.draw.line(self.board_surface, grid_colour,
                             (matrix_surface_rect.x + idx * self.GRID_SIZE, matrix_surface_rect.y + self.MATRIX_SURFACE_HEIGHT),
                             (matrix_surface_rect.x + idx * self.GRID_SIZE, matrix_surface_rect.y + self.Config.MATRIX_HEIGHT // 2 * self.GRID_SIZE - self.MATRIX_SURFACE_HEIGHT),
                             width
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
                        (matrix_surface_rect.x + j * self.GRID_SIZE, matrix_surface_rect.y + i * self.GRID_SIZE - self.MATRIX_SURFACE_HEIGHT, self.GRID_SIZE, self.GRID_SIZE)
                        )
    
    def __draw_UI_border(self):
        """
        Draw a border around the matrix, garbage, queue and hold
        """
        # ====== MATRIX ======
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # matrix left border
                 (self.matrix_rect_pos_x - self.BORDER_WIDTH // 2 - 1, self.MATRIX_SURFACE_HEIGHT + self.matrix_rect_pos_y), 
                 (self.matrix_rect_pos_x - self.BORDER_WIDTH // 2 - 1, self.matrix_rect_pos_y), self.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(),   # matrix right border
                        (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + self.BORDER_WIDTH // 2, self.matrix_rect_pos_y), 
                        (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + self.BORDER_WIDTH // 2, self.matrix_rect_pos_y + self.MATRIX_SURFACE_HEIGHT - 1), 
                        self.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(),  # matrix bottom border
                        (self.matrix_rect_pos_x  - self.BORDER_WIDTH - self.GRID_SIZE, self.matrix_rect_pos_y + self.MATRIX_SURFACE_HEIGHT + self.BORDER_WIDTH // 2 - 1), 
                        (self.matrix_rect_pos_x  + self.MATRIX_SURFACE_WIDTH + self.BORDER_WIDTH - 1, self.matrix_rect_pos_y + self.MATRIX_SURFACE_HEIGHT + self.BORDER_WIDTH // 2 - 1), 
                        self.BORDER_WIDTH)

        # ====== GARBAGE =======
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # left garbage border
                        (self.matrix_rect_pos_x - self.BORDER_WIDTH // 2 - 1 - self.GRID_SIZE, self.matrix_rect_pos_y), 
                        (self.matrix_rect_pos_x  - self.BORDER_WIDTH // 2 - 1 - self.GRID_SIZE, self.matrix_rect_pos_y + self.MATRIX_SURFACE_HEIGHT - 1), 
                        self.BORDER_WIDTH)
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(),  
                        (self.matrix_rect_pos_x  - self.BORDER_WIDTH - self.GRID_SIZE, self.matrix_rect_pos_y + self.MATRIX_SURFACE_HEIGHT - self.GRID_SIZE * 8 + self.BORDER_WIDTH // 2 - 1) , 
                        (self.matrix_rect_pos_x - self.BORDER_WIDTH , self.matrix_rect_pos_y+ self.MATRIX_SURFACE_HEIGHT - self.GRID_SIZE * 8 + self.BORDER_WIDTH // 2 - 1), 
                        self.BORDER_WIDTH)
        
    def __draw_queue_border(self):

        match self.Config.QUEUE_LENGTH:
            case 1:
                queue_size = self.GRID_SIZE * 4.5
            case 2: 
                queue_size = self.GRID_SIZE * 7.5
            case 3:
                queue_size = self.GRID_SIZE * 10.5
            case 4:
                queue_size = self.GRID_SIZE * 13.5
            case 5:
                queue_size = self.GRID_SIZE * 16.5
            case 6:
                queue_size = self.GRID_SIZE * 19.5
            case _:
                queue_size = self.GRID_SIZE * 19.5
      
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # queue left border
                        (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + 6 * self.GRID_SIZE + self.BORDER_WIDTH, self.matrix_rect_pos_y + self.GRID_SIZE // 2 - 1),
                        (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + 6 * self.GRID_SIZE + self.BORDER_WIDTH, self.matrix_rect_pos_y + queue_size - self.GRID_SIZE // 2 - 1),
                        self.BORDER_WIDTH)
        
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # queue bottom border
                (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + self.BORDER_WIDTH + 6 * self.GRID_SIZE  + self.BORDER_WIDTH // 2, self.matrix_rect_pos_y + queue_size - self.GRID_SIZE // 2 - 1),
                (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + self.BORDER_WIDTH // 2, self.matrix_rect_pos_y + queue_size - self.GRID_SIZE // 2 - 1),
                self.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(), # queue top border
                        (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + self.BORDER_WIDTH + 6 * self.GRID_SIZE  + self.BORDER_WIDTH // 2, self.matrix_rect_pos_y + self.GRID_SIZE // 2 - 1),
                        (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH + self.BORDER_WIDTH // 2, self.matrix_rect_pos_y + self.GRID_SIZE // 2 - 1),
                        self.GRID_SIZE)
    
        text_surface = self.hun2_big.render('NEXT', True, (0, 0, 0))
        self.board_surface.blit(text_surface, (self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH // 2 + self.GRID_SIZE * 5.2, self.matrix_rect_pos_y + self.GRID_SIZE * 0.15))
        
    def __draw_hold_border(self):
    
        pygame.draw.line(self.board_surface, self.__get_border_colour(), # hold left border
                        (self.matrix_rect_pos_x - 7 * self.GRID_SIZE - self.BORDER_WIDTH //2 - 1, self.matrix_rect_pos_y + self.GRID_SIZE // 2 - 1),
                        (self.matrix_rect_pos_x - 7 * self.GRID_SIZE - self.BORDER_WIDTH //2 - 1, self.matrix_rect_pos_y + 4 * self.GRID_SIZE),
                        self.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(), # hold bottom border
                        (self.matrix_rect_pos_x - 7 * self.GRID_SIZE - self.BORDER_WIDTH, self.matrix_rect_pos_y + 4 * self.GRID_SIZE),
                        (self.matrix_rect_pos_x - self.GRID_SIZE - self.BORDER_WIDTH, self.matrix_rect_pos_y + 4 * self.GRID_SIZE),
                        self.BORDER_WIDTH)

        pygame.draw.line(self.board_surface, self.__get_border_colour(), # hold top border
            (self.matrix_rect_pos_x - 7 * self.GRID_SIZE - self.BORDER_WIDTH, self.matrix_rect_pos_y + self.GRID_SIZE // 2 - 1),
            (self.matrix_rect_pos_x - self.GRID_SIZE - self.BORDER_WIDTH, self.matrix_rect_pos_y + self.GRID_SIZE // 2 - 1),
            self.GRID_SIZE)
        
            
        text_surface = self.hun2_big.render('HOLD', True, (0, 0, 0))
        self.board_surface.blit(text_surface, (self.matrix_rect_pos_x - 7.25 * self.GRID_SIZE + self.GRID_SIZE * 0.25, self.matrix_rect_pos_y + self.GRID_SIZE * 0.15))
        
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

        matrix_rect = pygame.Rect(self.matrix_rect_pos_x, self.matrix_rect_pos_y, self.MATRIX_SURFACE_WIDTH, self.MATRIX_SURFACE_HEIGHT)
        
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
        pygame.gfxdraw.box(self.board_surface, queue_rect, (0, 0, 0))
        
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
        rect_x = self.matrix_rect_pos_x + self.MATRIX_SURFACE_WIDTH // 2 + self.queue_rect_width - self.GRID_SIZE
        rect_y =  self.matrix_rect_pos_y + 1 * self.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.queue_rect_width, self.queue_rect_height)	
        
    def __hold_rect(self):
        """
        Get the rectangle for the hold
        """
        rect_x = self.matrix_rect_pos_x - 7 * self.GRID_SIZE
        rect_y =  self.matrix_rect_pos_y + 1 * self.GRID_SIZE
    
        return pygame.Rect(rect_x, rect_y, self.hold_rect_width, self.hold_rect_height)
    
    def __render_hold(self):
        """
        Render the hold onto the window
        
        args:
            four (Four): the Four instance
        """
        tetromino = self.GameInstanceStruct.held_tetromino    
        hold_rect = self.__hold_rect()
        pygame.gfxdraw.box(self.board_surface, hold_rect, (0, 0, 0))
        
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
        
        tetromino_height = len(tetromino) * self.GRID_SIZE
        tetromino_width = len(tetromino[0]) * self.GRID_SIZE

        offset_x = (rect.width - tetromino_width) // 2
        offset_y = (rect.height - tetromino_height) // 2

        for i, row in enumerate(tetromino):
            for j, value in enumerate(row):
                if value != 0:
                    if can_hold:
                        colour = self.Config.COLOUR_MAP[value]
                    else:
                        colour = lerpBlendRGBA(self.Config.COLOUR_MAP[value], (75, 75, 75), 0.85)
                    
                    pygame.gfxdraw.box(self.board_surface, 
                                    (rect.x + offset_x + j * self.GRID_SIZE, rect.y + offset_y + i * self.GRID_SIZE, self.GRID_SIZE, self.GRID_SIZE),
                                    colour
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
            
        debug_surfaces.append((self.hun2_big.render(fps_text, True, fps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE // 2)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_FrameRate)} | best: {int(self.DebugStruct.Best_FrameRate)} | current: {int(self.DebugStruct.Current_FrameRate)}', True, fps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 1.5)))

        debug_surfaces.append((self.hun2_small.render(f'Render Time: {get_prefix(self.DebugStruct.Average_RenderTime, "s")}', True, fps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 2)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_RenderTime, "s")} | best: {get_prefix(self.DebugStruct.Best_RenderTime, "s")} | current: {get_prefix(self.DebugStruct.Current_RenderTime, "s")}', True, fps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 2.5)))

        if self.DebugStruct.Average_TickRate < self.Config.TPS * 0.95:
            tps_colour = (255, 0, 0)
        else:
            tps_colour = (0, 255, 0)

        # # TPS debug information
        debug_surfaces.append((self.hun2_big.render(f'TPS: {int(self.DebugStruct.Average_TickRate)}', True, tps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 3.5)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_TickRate)} | best: {int(self.DebugStruct.Best_TickRate)} | current: {int(self.DebugStruct.Current_TickRate)}', True, tps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 4.5)))

        debug_surfaces.append((self.hun2_small.render(f'Execution Time: {get_prefix(self.DebugStruct.Average_ExecutionTime, "s")}', True, tps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 5)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_ExecutionTime, "s")} | best: {get_prefix(self.DebugStruct.Best_ExecutionTime, "s")} | current: {get_prefix(self.DebugStruct.Current_ExecutionTime, "s")}', True, tps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 5.5)))

        debug_surfaces.append((self.hun2_small.render(f'Delta Tick: {self.DebugStruct.Average_DeltaTick:.2f}', True, tps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 6)))

        debug_surfaces.append((self.pfw_small.render(f'worst: {self.DebugStruct.Worst_DeltaTick} | best: {self.DebugStruct.Best_DeltaTick} | current: {int(self.DebugStruct.Current_DeltaTick)}', True, tps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 6.5)))

        debug_surfaces.append((self.hun2_small.render(f'Tick: {self.DebugStruct.TickCounter}', True, tps_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 7)))
        
        # handling debug information
        
        if self.DebugStruct.Average_PollingRate < self.Config.POLLING_RATE * 0.95:
            poll_colour = (255, 0, 0)
        else:
            poll_colour = (0, 255, 0)
        
        debug_surfaces.append((self.hun2_big.render(f'POLL: {int(self.DebugStruct.Average_PollingRate)}', True, poll_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 8)))
        
        debug_surfaces.append((self.pfw_small.render(f'worst: {int(self.DebugStruct.Worst_PollingRate)} | best: {int(self.DebugStruct.Best_PollingRate)} | current: {int(self.DebugStruct.Current_PollingRate)}', True, poll_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 9)))
        
        debug_surfaces.append((self.hun2_small.render(f'Polling Time: {get_prefix(self.DebugStruct.Average_PollingTime, "s")}', True, poll_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 9.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'worst: {get_prefix(self.DebugStruct.Worst_PollingTime, "s")} | best: {get_prefix(self.DebugStruct.Best_PollingTime, "s")} | current: {get_prefix(self.DebugStruct.Current_PollingTime, "s")}', True, poll_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 10)))

        das_colour = (255, 255, 255)

        debug_surfaces.append((self.hun2_big.render(f'DAS: {int(self.DebugStruct.DAS_Left_Counter)} ms {int(self.DebugStruct.DAS_Right_Counter)} ms', True, das_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 11)))
        
        debug_surfaces.append((self.hun2_small.render(f'Threshold: {self.DebugStruct.DAS_Threshold} ms', True, das_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 12)))
        
        debug_surfaces.append((self.pfw_small.render(f'DCD: {self.DebugStruct.DCD} | DAS Cancel: {self.DebugStruct.DAS_Cancel} | Direction: {self.DebugStruct.Prioritise_Direction} (Priority: {self.DebugStruct.Direction})', True, das_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 12.5)))
        
        arr_colour = (255, 255, 255)
        
        debug_surfaces.append((self.hun2_big.render(f'ARR: {int(self.DebugStruct.ARR_Left_Counter)} ms {int(self.DebugStruct.ARR_Right_Counter)} ms', True, arr_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 13.5)))
        
        debug_surfaces.append((self.hun2_small.render(f'Threshold: {self.DebugStruct.ARR_Threshold} ms', True, arr_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 14.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'SDF: { self.DebugStruct.Soft_Drop_Factor} | PrefSD: {self.DebugStruct.Prefer_Soft_Drop} | On Floor: {self.DebugStruct.On_Floor}', True, (255, 255, 255)), (self.GRID_SIZE // 2, self.GRID_SIZE * 15.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'Gravity: {self.DebugStruct.Gravity:.2f} G ({self.DebugStruct.G_in_ticks} ticks) | Multi: {self.DebugStruct.Gravity_Multiplier} | Counter: {self.DebugStruct.Gravity_Counter}', True, (255, 255, 255)), (self.GRID_SIZE // 2, self.GRID_SIZE * 16)))
    
        debug_surfaces.append((self.pfw_small.render(f'Lock Delay: {self.DebugStruct.Lock_Delay} ({self.DebugStruct.Lock_Delay_Ticks} ticks) | Counter: {self.DebugStruct.Lock_Delay_Counter} | Resets Left: {self.DebugStruct.Max_Moves} | y: {self.DebugStruct.Lowest_Pivot}', True, (255, 255, 255)), (self.GRID_SIZE // 2, self.GRID_SIZE * 16.5)))
        
        debug_surfaces.append((self.pfw_small.render(f'PrevAccHD: {self.DebugStruct.Prevent_Accidental_Hard_Drop} | Delay: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Time} ticks| Counter: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Counter} | Flag: {self.DebugStruct.Prevent_Accidental_Hard_Drop_Flag}', True, (255, 255, 255)), (self.GRID_SIZE // 2, self.GRID_SIZE * 17)))
          
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
        
        key_surfaces.append((self.action_ui.render('B', True, left_colour), (self.GRID_SIZE // 2, self.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('A', True, right_colour), (self.GRID_SIZE *2 , self.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('C', True, softdrop_colour), (self.GRID_SIZE * 3.5, self.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('G', True, harddrop_colour), (self.GRID_SIZE * 5, self.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('E', True, ccw_colour), (self.GRID_SIZE * 6.5, self.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('D', True, cw_colour), (self.GRID_SIZE * 8, self.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('F', True, colour_180), (self.GRID_SIZE * 9.5, self.GRID_SIZE * 26.5)))

        key_surfaces.append((self.action_ui.render('H', True, hold_colour), (self.GRID_SIZE * 11, self.GRID_SIZE * 26.5))) 
        
        for surface, coords in key_surfaces:
            self.window.blit(surface, coords)
    
    def __draw_pivot_position(self, matrix_surface_rect):
        
        loc = self.GameInstanceStruct.current_tetromino.position + self.GameInstanceStruct.current_tetromino.pivot
        
        x = matrix_surface_rect.x + loc.x * self.GRID_SIZE 
        y = matrix_surface_rect.y + loc.y * self.GRID_SIZE - (self.Config.MATRIX_HEIGHT * self.GRID_SIZE)//2

        length = self.GRID_SIZE // 4

        pygame.draw.line(self.board_surface, (255, 255, 255), (x - length, y), (x + length, y), 2)
        pygame.draw.line(self.board_surface, (255, 255, 255), (x, y - length), (x, y + length), 2)
                
    def __draw_tetromino_position(self, matrix_surface_rect):
        loc = self.GameInstanceStruct.current_tetromino.position
        
        x = matrix_surface_rect.x + loc.x * self.GRID_SIZE
        y = matrix_surface_rect.y + loc.y * self.GRID_SIZE - (self.Config.MATRIX_HEIGHT * self.GRID_SIZE)//2 
        
        length = self.GRID_SIZE // 4

        pygame.draw.line(self.board_surface, (0, 255, 0), (x - length, y), (x + length, y), 2)
        pygame.draw.line(self.board_surface, (0, 255, 0), (x, y - length), (x, y + length), 2)
    
    def __format_time(self):
        minutes = int((self.TimingStruct.current_time % 3600) // 60)
        seconds = int(self.TimingStruct.current_time % 60)
        milliseconds = int((self.TimingStruct.current_time % 1) * 1000)
        time_minsec = f"{minutes}:{seconds:02}"
        time_ms = f"{milliseconds:03}"
        return time_minsec, time_ms
    
    def __draw_timer(self): 
        
        if not self.FlagStruct.GAME_OVER:
            self.time_minsec, self.time_ms = self.__format_time()
            
        self.board_surface.blit(self.hun2_med.render('Time', True, (255, 255, 255)), (self.GRID_SIZE * 5.33, self.GRID_SIZE * 22.33 + self.MATRIX_SURFACE_HEIGHT))
        self.board_surface.blit(self.hun2_big.render(f'{self.time_minsec}.', True, (255, 255, 255)), (self.GRID_SIZE * 5.5 - (len(self.time_minsec) * self.GRID_SIZE//2 + 1), self.GRID_SIZE * 23.25 + self.MATRIX_SURFACE_HEIGHT))
        self.board_surface.blit(self.hun2_med.render(f'{self.time_ms}', True, (255, 255, 255)), (self.GRID_SIZE * 5.66, self.GRID_SIZE * 23.45 + self.MATRIX_SURFACE_HEIGHT))