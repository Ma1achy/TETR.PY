from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from render.board.struct_board import StructBoardConsts
import pygame
import copy
from utils import lerpBlendRGBA, smoothstep, tint_texture

class Matrix():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, BoardConsts:StructBoardConsts):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.BoardConts = BoardConsts
        
        self.piece_surface = pygame.Surface((1, 1), pygame.SRCALPHA) # these surfaces have to be recreated as the size of the tetromino changes
        self.piece_blocks = 'PLACEHOLDER'
        
        self.blocks_surface = self.blocks_surface = pygame.Surface((self.BoardConts.MATRIX_SURFACE_WIDTH, self.BoardConts.MATRIX_SURFACE_HEIGHT * 2), pygame.SRCALPHA)
        self.placed_blocks = 'PLACEHOLDER'
        
        self.shadow_surface = pygame.Surface((1, 1), pygame.SRCALPHA)  
        self.shadow_blocks = 'PLACEHOLDER'
        
        self.warning_surface = pygame.Surface((1, 1), pygame.SRCALPHA) 
        self.warning_type = 'PLACEHOLDER'
        
        self.RenderStruct.textures = {
            'Z': None,
            'L': None,
            'O': None,
            'S': None,
            'I': None,
            'J': None,
            'T': None,
            'Garbage': None,
            'Hurry': None,
            'Locked': None,
            'Shadow': None,
            'Warning': None,
        }
        
        self.tinted_shadow_textures = {
            'Z': None,
            'L': None,
            'O': None,
            'S': None,
            'I': None,
            'J': None,
            'T': None,
        }
        
        self.pre_scale_textures()
        self.pre_tint_textures()
    
    def draw(self, surface):
        """
        Draw the matrix, current tetromino and its shadow onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        matrix_rect = pygame.Rect(self.BoardConts.matrix_rect_pos_x, self.BoardConts.matrix_rect_pos_y, self.BoardConts.MATRIX_SURFACE_WIDTH, self.BoardConts.MATRIX_SURFACE_HEIGHT)
        
        self.__draw_current_tetromino_shadow(surface, matrix_rect)
        self.__draw_placed_blocks(surface, matrix_rect)
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
        
        rect = self.__get_rect(self.GameInstanceStruct.current_tetromino.blocks, self.GameInstanceStruct.current_tetromino.position, matrix_surface_rect)
        
        if self.GameInstanceStruct.current_tetromino.blocks != self.piece_blocks: # only draw if the blocks have changed
            self.blocks = self.GameInstanceStruct.current_tetromino.blocks
            self.piece_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
            blend_colour = (0, 0, 0)
            piece_alpha = self.__get_lock_delay_alpha(self.GameInstanceStruct.current_tetromino.lock_delay_counter, self.GameInstanceStruct.lock_delay_in_ticks)
            
            self.__draw_tetromino_blocks(self.piece_surface, self.GameInstanceStruct.current_tetromino.blocks, self.piece_surface.get_rect(), blend_colour, piece_alpha) 
            
        self.piece_surface.set_alpha(255)
        surface.blit(self.piece_surface, (rect.x, rect.y))
        
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
        
        self.shadow_rect = self.__get_rect(self.GameInstanceStruct.current_tetromino.blocks, self.GameInstanceStruct.current_tetromino.shadow_position, matrix_surface_rect)
        
        if self.shadow_blocks != self.GameInstanceStruct.current_tetromino.blocks:
            self.shadow_blocks = self.GameInstanceStruct.current_tetromino.blocks
            self.shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.SRCALPHA)
   
            self.__draw_shadow_blocks(self.shadow_surface, self.GameInstanceStruct.current_tetromino.blocks, self.shadow_surface.get_rect(), (0, 0, 0), 1)
        
        self.shadow_surface.set_alpha(self.RenderStruct.shadow_opacity)
        surface.blit(self.shadow_surface, (self.shadow_rect.x, self.shadow_rect.y))
    
    def __draw_next_tetromino_warning(self, surface, matrix_surface_rect:pygame.Rect):
        """
        Draw the warning crosses of the next tetromino
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn in
        """
        if self.GameInstanceStruct.next_tetromino is None:
            return
        
        rect = self.__get_rect(self.GameInstanceStruct.next_tetromino.blocks, self.GameInstanceStruct.next_tetromino.position, matrix_surface_rect)
        
        if self.GameInstanceStruct.next_tetromino.type != self.warning_type:
            self.warning_type = self.GameInstanceStruct.next_tetromino.type
            self.warning_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            self.__DrawWarningCrosses(self.warning_surface, self.GameInstanceStruct.next_tetromino.blocks, self.warning_surface.get_rect())
            
        self.warning_surface.set_alpha(128)
        surface.blit(self.warning_surface, (rect.x, rect.y))
    
    def __draw_placed_blocks(self, surface, matrix_surface_rect:pygame.Rect):
        """
        Draw the placed blocks in the matrix
        
        args:
            surface (pygame.Surface): The surface to draw onto
            matrix (list): the matrix to draw
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn
        """
        rect = pygame.Rect(matrix_surface_rect.x, matrix_surface_rect.y, matrix_surface_rect.width, matrix_surface_rect.height * 2) # matrix is double the height of the board

        if self.placed_blocks != self.GameInstanceStruct.matrix.matrix:	# only draw the matrix if it has changed
            self.placed_blocks = copy.deepcopy(self.GameInstanceStruct.matrix.matrix) # if I just do the logical thing here: self.placed_blocks = self.GameInstanceStruct.matrix.matrix 
                                                                                      # this doesn't work properly and nothing renders?????? neither does self.GameInstanceStruct.matrix.matrix.copy() ???????
                                                                                      # WTF is deepcopy ???? This has given me an aneurysm
            self.blocks_surface.fill((0, 0, 0, 0))
            self.__draw_tetromino_blocks(self.blocks_surface, self.GameInstanceStruct.matrix.matrix, self.blocks_surface.get_rect(), (0, 0, 0), 1)
        
        self.blocks_surface.set_alpha(255)  
        surface.blit(self.blocks_surface, (rect.x, rect.y - rect.height//2)) # since matrix is double the board height, we need to shift it up
        
    def __get_rect(self, blocks, position, matrix_surface_rect):
        """
        Get the rectangle for the tetromino
        
        args:
            blocks (list): the blocks of the tetromino
            position (Vector2): the position of the tetromino
            matrix_surface_rect (pygame.Rect): the rectangle that the matrix is drawn
        """
        tetromino_rect_length = self.RenderStruct.GRID_SIZE * len(blocks[0])
        tetromino_rect_width = self.RenderStruct.GRID_SIZE * len(blocks[1])
        
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
             
        if self.RenderStruct.use_textures:
            for i, row in enumerate(tetromino_blocks):
                for j, value in enumerate(row):
                    if value != 0:
                        texture = self.RenderStruct.textures[value]
                        surface.blit(texture, (rect.x + j * self.RenderStruct.GRID_SIZE, rect.y + i * self.RenderStruct.GRID_SIZE))
                        
        else:
            for i, row in enumerate(tetromino_blocks):
                for j, value in enumerate(row):
                    if value != 0:
                        colour = self.RenderStruct.COLOUR_MAP[value]
                        pygame.draw.rect(
                            surface, 
                            lerpBlendRGBA(blend_colour, colour, alpha),
                            (rect.x + j * self.RenderStruct.GRID_SIZE, rect.y + i * self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE)
                        )
    
    def __draw_shadow_blocks(self, surface, tetromino_blocks, rect, blend_colour, alpha):
        if self.RenderStruct.use_textures:
            for i, row in enumerate(tetromino_blocks):
                for j, value in enumerate(row):
                    if value != 0:
                        if self.RenderStruct.coloured_shadow: # tint the non transparent parts of this texture with self.RenderStruct.COLOUR_MAP[value]
                            texture = self.tinted_shadow_textures[value]
                        else:
                            texture = self.RenderStruct.textures['Shadow']
                            
                        surface.blit(texture, (rect.x + j * self.RenderStruct.GRID_SIZE, rect.y + i * self.RenderStruct.GRID_SIZE))
        else:
            for i, row in enumerate(tetromino_blocks):
                for j, value in enumerate(row):
                    if value != 0:
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
        
        if self.RenderStruct.use_textures:
            for i, row in enumerate(tetromino_blocks):
                for j, value in enumerate(row):
                    if value != 0:
                        texture = self.RenderStruct.textures['Warning']
                        surface.blit(texture, (rect.x + j * self.RenderStruct.GRID_SIZE, rect.y + i * self.RenderStruct.GRID_SIZE))
        else:
            for i, row in enumerate(tetromino_blocks):
                for j, value in enumerate(row):
                    if value != 0:
                        pygame.draw.line(surface, (255, 0, 0), 
                                        (rect.x + j * self.RenderStruct.GRID_SIZE + padding, rect.y + i * self.RenderStruct.GRID_SIZE + padding), 
                                        (rect.x + (j + 1) * self.RenderStruct.GRID_SIZE - padding, rect.y + (i + 1) * self.RenderStruct.GRID_SIZE - padding), thickness)
                        
                        pygame.draw.line(surface, (255, 0, 0), 
                                        (rect.x + (j + 1) * self.RenderStruct.GRID_SIZE - padding, rect.y + i * self.RenderStruct.GRID_SIZE + padding), 
                                        (rect.x + j * self.RenderStruct.GRID_SIZE + padding, rect.y + (i + 1) * self.RenderStruct.GRID_SIZE - padding), thickness)
                
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
        
    def get_texture(self, idx):
        """
        Get a texture from the texture atlas
        
        args:
            idx (int): The index of the texture in the texture atlas
        """
        x = idx % self.RenderStruct.TEXTURES_PER_ROW * (self.RenderStruct.TEXTURE_ATLAS.get_width() // self.RenderStruct.TEXTURES_PER_ROW)
        y = idx // self.RenderStruct.TEXTURES_PER_COLUMN * (self.RenderStruct.TEXTURE_ATLAS.get_height() // self.RenderStruct.TEXTURES_PER_COLUMN)

        return self.RenderStruct.TEXTURE_ATLAS.subsurface((x, y, 256, 256))

    def pre_scale_textures(self):
        """
        Pre-scale the textures
        """
        for t in self.RenderStruct.textures:
            texture = self.get_texture(self.RenderStruct.TEXTURE_MAP[t])
            self.RenderStruct.textures[t] = pygame.transform.smoothscale(texture, (self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE))
    
    def pre_tint_textures(self):
        """
        Pre-tint the textures
        """
        for t in self.tinted_shadow_textures:
            texture = self.get_texture(self.RenderStruct.TEXTURE_MAP['Shadow'])
            texture = pygame.transform.smoothscale(texture, (self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE))
            self.tinted_shadow_textures[t] = tint_texture(texture, self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR[t])
            
    

            