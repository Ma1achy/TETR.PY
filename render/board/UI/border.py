from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from render.board.struct_board import StructBoardConsts
import pygame
from utils import lerpBlendRGBA
from scipy.ndimage import gaussian_filter, binary_dilation
import numpy as np

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
    
        self.get_glow()
        
    def draw(self, surface):
        """
        Draw the border around the matrix, hold, and queue onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """

        self.__draw_matrix_grid(surface)
        self.__draw_border(surface)
         
        if self.BoardConsts.draw_garbage_bar:
            self.__draw_garbage_border(surface, True)
        
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
        grid_colour = lerpBlendRGBA((0, 0, 0), self.BoardConsts.top_out_colour, 0.25)
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
        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # matrix left border
                 (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH // 2 - 1, self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.BoardConsts.matrix_rect_pos_y), 
                 (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH // 2 - 1, self.BoardConsts.matrix_rect_pos_y), self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.BoardConsts.top_out_colour,   # matrix right border
                        (self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y), 
                        (self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT), 
                        self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.BoardConsts.top_out_colour,  # matrix bottom border
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2), 
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH - 1, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2), 
                        self.RenderStruct.BORDER_WIDTH)

    def __draw_garbage_border(self, surface, draw_background = True):
        """
        Draw a border around the garbage bar
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        if draw_background:
            self.garbage_bar_background_surface.fill((0, 0, 0, 200))
            surface.blit(self.garbage_bar_background_surface, self.garbage_bar_background_rect.topleft)
        
        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # left garbage border
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH // 2 - 1 - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y), 
                        (self.BoardConsts.matrix_rect_pos_x   - self.RenderStruct.BORDER_WIDTH // 2 - 1 - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT), 
                        self.RenderStruct.BORDER_WIDTH)
        
        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # horizontal line inside bar
                        (self.BoardConsts.matrix_rect_pos_x   - self.RenderStruct.BORDER_WIDTH - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT - self.RenderStruct.GRID_SIZE * 8 + self.RenderStruct.BORDER_WIDTH // 2) , 
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH , self.BoardConsts.matrix_rect_pos_y+ self.BoardConsts.MATRIX_SURFACE_HEIGHT - self.RenderStruct.GRID_SIZE * 8 + self.RenderStruct.BORDER_WIDTH // 2), 
                        self.RenderStruct.BORDER_WIDTH)
        
        pygame.draw.line(surface, self.BoardConsts.top_out_colour,# bottom garbage border
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH - self.RenderStruct.GRID_SIZE, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2) , 
                        (self.BoardConsts.matrix_rect_pos_x  - self.RenderStruct.BORDER_WIDTH , self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH // 2), 
                        self.RenderStruct.BORDER_WIDTH)
        
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
      
        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # queue right border
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + 6 * self.RenderStruct.GRID_SIZE + self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2 - 1),
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + 6 * self.RenderStruct.GRID_SIZE + self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + queue_size - self.RenderStruct.GRID_SIZE // 2 + 1),
                        self.RenderStruct.BORDER_WIDTH)
        
        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # queue bottom border
                (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH + 6 * self.RenderStruct.GRID_SIZE  + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + queue_size - self.RenderStruct.GRID_SIZE // 2 + 1),
                (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + queue_size - self.RenderStruct.GRID_SIZE // 2 + 1),
                self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # queue top border
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH + 6 * self.RenderStruct.GRID_SIZE  + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
                        (self.BoardConsts.matrix_rect_pos_x  + self.BoardConsts.MATRIX_SURFACE_WIDTH + self.RenderStruct.BORDER_WIDTH // 2, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
                        self.RenderStruct.GRID_SIZE)
        
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
            
        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # hold left border
                        (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH //2 - 1, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2 - 1),
                        (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH //2 - 1, self.BoardConsts.matrix_rect_pos_y + 4 * self.RenderStruct.GRID_SIZE),
                        self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # hold bottom border
                        (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + 4 * self.RenderStruct.GRID_SIZE),
                        (self.BoardConsts.matrix_rect_pos_x  + end - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + 4 * self.RenderStruct.GRID_SIZE),
                        self.RenderStruct.BORDER_WIDTH)

        pygame.draw.line(surface, self.BoardConsts.top_out_colour, # hold top border
            (self.BoardConsts.matrix_rect_pos_x  - start * self.RenderStruct.GRID_SIZE - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
            (self.BoardConsts.matrix_rect_pos_x  + end - self.RenderStruct.BORDER_WIDTH, self.BoardConsts.matrix_rect_pos_y + self.RenderStruct.GRID_SIZE // 2),
            self.RenderStruct.GRID_SIZE)
                
    def get_glow(self):
        self.__draw_glow(sigma = 12)
        self.__draw_glow(sigma = 10)
        self.__draw_glow(sigma = 5)
    
    def __draw_glow(self, sigma):
        surf = self.BoardConsts.board_glow_surface.copy()
        self.__draw_border(surf)
        
        if self.BoardConsts.draw_garbage_bar:
            self.__draw_garbage_border(surf, False)
        
        if self.GameInstanceStruct.hold:  
            self.__draw_hold_border(surf)
        
        if self.GameInstanceStruct.queue_previews > 0:
            self.__draw_queue_border(surf)
        
        
        
        blurred_surf = self.apply_gaussian_blur_with_alpha(surf, sigma)
        self.BoardConsts.board_glow_surface.blit(blurred_surf ,(0, 0))
        
    def apply_gaussian_blur_with_alpha(self, surface, sigma):
      
        pixel_array = pygame.surfarray.array3d(surface).astype(np.float32)
        alpha_channel = pygame.surfarray.pixels_alpha(surface).astype(np.float32) / 255.0  

    
        rgba_array = np.zeros((pixel_array.shape[0], pixel_array.shape[1], 4), dtype=np.float32)
        rgba_array[:, :, :3] = pixel_array * alpha_channel[:, :, None]
        rgba_array[:, :, 3] = alpha_channel  

        blurred_rgb_array = np.zeros_like(rgba_array[:, :, :3])
        blurred_alpha_channel = gaussian_filter(rgba_array[:, :, 3], sigma=sigma)

        for i in range(3):
            blurred_rgb_array[:, :, i] = gaussian_filter(rgba_array[:, :, i], sigma=sigma)

        smoothed_alpha_channel = np.clip(blurred_alpha_channel, 0, 1)
        smoothed_alpha_channel = gaussian_filter(smoothed_alpha_channel, sigma=0.5) 

        # avoid division by zero in fully transparent areas
        nonzero_alpha = np.maximum(smoothed_alpha_channel, 1e-5)

        final_rgb = (blurred_rgb_array / nonzero_alpha[:, :, None]).clip(0, 255).astype(np.uint8)
        final_alpha = (smoothed_alpha_channel * 255).clip(0, 255).astype(np.uint8)

        blurred_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.surfarray.blit_array(blurred_surface, final_rgb)
        pygame.surfarray.pixels_alpha(blurred_surface)[:, :] = final_alpha

        return blurred_surface