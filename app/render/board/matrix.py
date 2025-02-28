from old_state.struct_render import StructRender
from instance.state.flags import Flags
from instance.state.game_state import GameState
from render.board.struct_board import StructBoardConsts
import pygame
import copy
from app.utils import lerpBlendRGBA, smoothstep, tint_texture
import numpy as np
# FIXME: line clear particles dont draw always since I will need to add the cleared lines/blocks to a queue in the game instance and then draw them
class Matrix():
    def __init__(self, RenderStruct:StructRender, FlagStruct:Flags, GameInstanceStruct:GameState, TimingStruct, BoardConsts:StructBoardConsts, RNG):
        
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.BoardConsts = BoardConsts
        
        self.current_time = 0
        self.previous_time = 0
        self.dt = 0
        
        self.line_clear_particles = np.zeros(0, dtype = [
            ('x', 'f4'), ('y', 'f4'), ('x_vel', 'f4'), ('y_vel', 'f4'), ('scale', 'f4'), ('block', 'O'), ('time', 'f4'), ('max_time', 'f4')
        ])
        
        self.game_over_fizzle_particles = np.zeros(0, dtype = [
            ('x', 'f4'), ('y', 'f4'), ('x_vel', 'f4'), ('y_vel', 'f4'), ('scale', 'f4'), ('block', 'O'), ('time', 'f4'), ('max_time', 'f4')
        ]) 
        
        self.RNG = RNG
        
        self.piece_surface = pygame.Surface((1, 1), pygame.SRCALPHA|pygame.HWSURFACE) # these surfaces have to be recreated as the size of the tetromino changes
        self.lock_delay_surface = pygame.Surface((1, 1), pygame.SRCALPHA|pygame.HWSURFACE)
        self.piece_blocks = 'PLACEHOLDER'
        
        self.blocks_surface_alpha = 255
        self.blocks_surface = self.blocks_surface = pygame.Surface((self.BoardConsts.MATRIX_SURFACE_WIDTH, self.BoardConsts.MATRIX_SURFACE_HEIGHT * 2), pygame.SRCALPHA|pygame.HWSURFACE)
        self.placed_blocks = 'PLACEHOLDER'
        
        self.shadow_surface = pygame.Surface((1, 1), pygame.SRCALPHA|pygame.HWSURFACE)
        self.shadow_blocks = 'PLACEHOLDER'
        
        self.warning_surface = pygame.Surface((1, 1), pygame.SRCALPHA|pygame.HWSURFACE)
        self.warning_type = 'PLACEHOLDER'
        
        self.line_clear_animation_surface = pygame.Surface((self.BoardConsts.MATRIX_SURFACE_WIDTH * 4, self.BoardConsts.MATRIX_SURFACE_HEIGHT * 3 + self.RenderStruct.GRID_SIZE * 5), pygame.SRCALPHA|pygame.HWSURFACE)
        self.game_over_fizzle_animation_surface = pygame.Surface((self.BoardConsts.MATRIX_SURFACE_WIDTH * 4, self.BoardConsts.MATRIX_SURFACE_HEIGHT * 3 + self.RenderStruct.GRID_SIZE * 5), pygame.SRCALPHA|pygame.HWSURFACE)
        
        self.got_fizzle_particles = False
        self.do_fizzle_game_over = False
        self.wait_time = 1
        
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
        matrix_rect = pygame.Rect(self.BoardConsts.matrix_rect_pos_x, self.BoardConsts.matrix_rect_pos_y, self.BoardConsts.MATRIX_SURFACE_WIDTH, self.BoardConsts.MATRIX_SURFACE_HEIGHT)
        
        if self.TimingStruct.FPS == 0:
            self.dt = 1
        else:
            self.dt = 1 / self.TimingStruct.FPS
        
        self.__draw_current_tetromino_shadow(surface, matrix_rect)
        self.__draw_placed_blocks(surface, matrix_rect)
        self.__draw_current_tetromino(surface, matrix_rect)
        self.__do_line_clear_animation(surface, matrix_rect)
        
        if self.do_fizzle_game_over:
            self.__do_fizzle_animation(surface, matrix_rect)
        
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
            self.lock_delay_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
            self.__draw_tetromino_blocks(self.piece_surface, self.GameInstanceStruct.current_tetromino.blocks, self.piece_surface.get_rect())
            self.lockdelay_animation(self.GameInstanceStruct.current_tetromino.blocks, self.piece_surface.get_rect())
            
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
            
        self.warning_surface.set_alpha(self.BoardConsts.warning_cross_opacity)
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
            self.__draw_tetromino_blocks(self.blocks_surface, self.GameInstanceStruct.matrix.matrix, self.blocks_surface.get_rect())
        
        self.blocks_surface.set_alpha(self.blocks_surface_alpha)  
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
    
    def __draw_tetromino_blocks(self, surface, tetromino_blocks, rect):
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
                        pygame.draw.rect(
                            surface, 
                            self.RenderStruct.COLOUR_MAP[value],
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
      
    def __do_line_clear_animation(self, surface, matrix_rect):
        
        self.line_clear_animation_surface.fill((0, 0, 0, 0)) 
        self.play_line_clear_animation(surface, matrix_rect)
        self.get_line_clear_particles()
        
        if self.GameInstanceStruct.lines_cleared is None:
            return

    def play_line_clear_animation(self, surface, matrix_rect):
        
        if self.line_clear_particles.size == 0:
            return
        
        g = 60 * self.RenderStruct.GRID_SIZE
        d = 0.85
        
        self.line_clear_particles['time'] -= self.dt
        x_dirs = -np.sign(self.line_clear_particles['x_vel'])
        self.line_clear_particles['x_vel'] += np.abs(self.line_clear_particles['x_vel']) * d * self.dt * x_dirs
        self.line_clear_particles['y_vel'] += g * self.dt
        
        self.line_clear_particles['x'] += self.line_clear_particles['x_vel'] * self.dt
        self.line_clear_particles['y'] += self.line_clear_particles['y_vel'] * self.dt
        
        prog = 1 - (self.line_clear_particles['max_time'] - self.line_clear_particles['time']) / self.line_clear_particles['max_time']
        self.line_clear_particles['scale'] = self.line_clear_particles['scale'] * smoothstep(prog)
        
        valid = (self.line_clear_particles['time'] > 0) & (self.line_clear_particles['scale'] > 0.001) & self.in_y_bounds(matrix_rect, self.line_clear_particles['y'], self.line_clear_particles['scale'])
        updated_particles = self.line_clear_particles[valid]
        self.line_clear_particles = updated_particles
        
        x_positions = updated_particles['x'] + self.line_clear_animation_surface.get_width() // 2 - matrix_rect.width // 2
        y_positions = updated_particles['y'] + matrix_rect.height // 2 + self.RenderStruct.GRID_SIZE * 6
        scales = updated_particles['scale']
        blocks = updated_particles['block']

        for x, y, scale, block in zip(x_positions, y_positions, scales, blocks):
            self.draw_block(
                self.line_clear_animation_surface,
                block,
                x,
                y,
                scale,
                matrix_rect
    )
        
        self.line_clear_animation_surface.set_alpha(200)
        
        surface.blit(
            self.line_clear_animation_surface,
            (matrix_rect.x - self.line_clear_animation_surface.get_width() // 2 + matrix_rect.width // 2 + self.BoardConsts.GarbageWidth // 2,
            matrix_rect.y - matrix_rect.height + self.RenderStruct.GRID_SIZE // 2 - self.RenderStruct.BORDER_WIDTH)
        )
    
    def draw_block(self, surface, block, x, y, scale, matrix_rect):
        if self.RenderStruct.use_textures:
            texture = self.RenderStruct.textures[block]
        else:
            texture = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA)
            texture.fill(self.RenderStruct.COLOUR_MAP[block])    
        
        texture = pygame.transform.scale(texture, (int(self.RenderStruct.GRID_SIZE * scale), int(self.RenderStruct.GRID_SIZE * scale)))
        rect = texture.get_rect(center = (x, y))
        surface.blit(texture, (rect.x, rect.y - matrix_rect.y))
    
    def in_y_bounds(self, matrix_rect, y, scale):
        return np.any(y < self.line_clear_animation_surface.get_height() - matrix_rect.height + self.RenderStruct.GRID_SIZE * 5 + scale * self.RenderStruct.GRID_SIZE)
                
    def get_line_clear_particles(self):
        
        if self.GameInstanceStruct.cleared_blocks is None or self.GameInstanceStruct.cleared_idxs is None or self.GameInstanceStruct.lines_cleared is None:
            return
        
        num_particles = sum(sum(1 for _ in line) for line in self.GameInstanceStruct.cleared_blocks)
  
        line_clear_particles = np.zeros(num_particles, dtype = [
            ('x', 'f4'), ('y', 'f4'), ('x_vel', 'f4'), ('y_vel', 'f4'), ('scale', 'f4'), ('block', 'O'), ('time', 'f4'), ('max_time', 'f4')
        ])
        
        particle_index = 0

        for idx, line in zip(self.GameInstanceStruct.cleared_idxs, self.GameInstanceStruct.cleared_blocks):
            for pos, block in enumerate(line):
                if particle_index >= num_particles:
                    break
                
                particle_index = self.__generate_line_clear_particles(pos, idx, block, line_clear_particles, particle_index)
                    
        self.line_clear_particles = np.concatenate((self.line_clear_particles, line_clear_particles))
      
        
    def __generate_line_clear_particles(self, pos, idx, block, line_clear_particles, particle_index):	
    
        offset_x = (self.RNG.next_float() - 0.5) * self.RenderStruct.GRID_SIZE + self.RenderStruct.GRID_SIZE // 4
        offset_y = (self.RNG.next_float() - 0.5) * self.RenderStruct.GRID_SIZE - self.RenderStruct.GRID_SIZE // 4
        
        x = pos * self.RenderStruct.GRID_SIZE + offset_x
        y = idx * self.RenderStruct.GRID_SIZE + offset_y
        
        x_vel = (self.RNG.next_float() - 0.5) * self.RenderStruct.GRID_SIZE * 10 * self.GameInstanceStruct.lines_cleared
        y_vel = (self.RNG.next_float() - 0.5) * self.RenderStruct.GRID_SIZE * 7 * self.GameInstanceStruct.lines_cleared
        
        scale = (1 - self.RNG.next_float()) + 0.15
        max_time = self.RNG.next_float() * 2 + 1.75 + 1 / self.GameInstanceStruct.lines_cleared
        time = max_time
        
        line_clear_particles[particle_index] = (x, y, x_vel, y_vel, scale, block[0], time, max_time)
        
        return particle_index + 1 
                  
    def lockdelay_animation(self, tetromino_blocks, rect):
        """
        Animate the lock delay
        """        
        if self.GameInstanceStruct.is_on_floor:
            for i, row in enumerate(tetromino_blocks):
                for j, value in enumerate(row):
                    if value != 0:
                        pygame.draw.rect(
                            self.lock_delay_surface, 
                            (0, 0, 0),
                            (rect.x + j * self.RenderStruct.GRID_SIZE, rect.y + i * self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE)
                        )

            alpha = 1 - self.__get_lock_delay_alpha(self.GameInstanceStruct.current_tetromino.lock_delay_counter, self.GameInstanceStruct.lock_delay_in_ticks)
            self.lock_delay_surface.set_alpha(255 * alpha)
            self.piece_surface.blit(self.lock_delay_surface, (rect.x, rect.y))
    
    def piece_placement_animation(self, tetromino_blocks, rect):
        # if the blocks are on the board, draw an overlay on them that then disappears after a short time
        # if the blocks are removed by a line clear dont draw the overlay
        
        if not self.RenderStruct.use_textures:
            return
        
        if self.GameInstanceStruct.lines_cleared is not None: # logic to check if to move the animated cells down
      
        
        # need to track the blocks that are placed, want it so multiple pieces being placed at the same time don't interfere with each other
        
            pass
    
    def __do_fizzle_animation(self, surface, rect):
        
        if not self.FlagStruct.GAME_OVER:
            return
        
        self.game_over_fizzle_animation_surface.fill((0, 0, 0, 0))
        
        if not self.got_fizzle_particles:
            self.get_fizzle_particles()
            
        if self.wait_time > 0:
            self.wait_time -= self.dt
            return
        else:
            self.GameInstanceStruct.matrix.matrix = self.GameInstanceStruct.matrix.empty_matrix() # clear the matrix
            self.GameInstanceStruct.current_tetromino = None 
        
        self.play_fizzle_animation(surface, rect)
      
    def play_fizzle_animation(self, surface, rect):
       
        if self.game_over_fizzle_particles.size == 0:
            self.got_fizzle_particles = False
            self.do_fizzle_game_over = False
            self.wait_time = 1
            return
    
        d = 0.3
        g = -self.RenderStruct.GRID_SIZE 
        
        self.game_over_fizzle_particles['time'] -= self.dt
        x_dir = np.sign(self.game_over_fizzle_particles['x_vel'])
        y_dir = np.sign(self.game_over_fizzle_particles['y_vel'])
        
        x_boundary = (self.game_over_fizzle_particles['x'] - self.game_over_fizzle_particles['scale'] <= 0) | \
                    (self.game_over_fizzle_particles['x'] - self.game_over_fizzle_particles['scale'] + self.BoardConsts.GarbageWidth >= rect.width)
        y_boundary = self.game_over_fizzle_particles['y'] + self.game_over_fizzle_particles['scale'] >= rect.height * 2 - self.RenderStruct.GRID_SIZE + self.RenderStruct.BORDER_WIDTH + 1

        self.game_over_fizzle_particles['x_vel'][x_boundary] *= -1
        self.game_over_fizzle_particles['y_vel'][y_boundary] = -abs(self.game_over_fizzle_particles['y_vel'][y_boundary])
                
        self.game_over_fizzle_particles['x_vel'] -= np.abs(self.game_over_fizzle_particles['x_vel']) * d * self.dt * x_dir
        self.game_over_fizzle_particles['y_vel'] += g * self.dt - np.abs(self.game_over_fizzle_particles['y_vel']) * d * self.dt * y_dir
        
        self.game_over_fizzle_particles['x'] += self.game_over_fizzle_particles['x_vel'] * self.dt
        self.game_over_fizzle_particles['y'] += self.game_over_fizzle_particles['y_vel'] * self.dt
        
        prog = 1 - (self.game_over_fizzle_particles['max_time'] - self.game_over_fizzle_particles['time']) / self.game_over_fizzle_particles['max_time']
        self.game_over_fizzle_particles['scale'] = self.game_over_fizzle_particles['scale'] * smoothstep(prog)
        
        valid = (self.game_over_fizzle_particles['time'] > 0) & (self.game_over_fizzle_particles['scale'] > 0.001) & self.in_y_bounds(rect, self.game_over_fizzle_particles['y'], self.game_over_fizzle_particles['scale'])
        updated_particles = self.game_over_fizzle_particles[valid]
        self.game_over_fizzle_particles = updated_particles
        
        x_positions = updated_particles['x'] + self.game_over_fizzle_animation_surface.get_width() // 2 - rect.width // 2
        y_positions = updated_particles['y'] + rect.height // 2 + self.RenderStruct.GRID_SIZE * 6
        scales = updated_particles['scale']
        blocks = updated_particles['block']
        
        for x, y, scale, block in zip(x_positions, y_positions, scales, blocks):
            self.draw_block(
                self.game_over_fizzle_animation_surface,
                block,
                x,
                y,
                scale,
                rect
            )
            
            surface.blit(
                self.game_over_fizzle_animation_surface,
                (rect.x - self.game_over_fizzle_animation_surface.get_width() // 2 + rect.width // 2 + self.BoardConsts.GarbageWidth // 2,
                rect.y - rect.height + self.RenderStruct.GRID_SIZE // 2 - self.RenderStruct.BORDER_WIDTH)
            )
        
    def get_fizzle_particles(self):
        
        num_particles = sum(sum(1 for block in row if block != 0) for row in self.GameInstanceStruct.matrix.matrix)
        
        if self.GameInstanceStruct.current_tetromino is not None:
            num_particles += sum(sum(1 for value in row if value != 0) for row in self.GameInstanceStruct.current_tetromino.blocks)
            
        fizzle_particles = np.zeros(num_particles, dtype=[
        ('x', 'f4'), ('y', 'f4'), ('x_vel', 'f4'), ('y_vel', 'f4'),
        ('scale', 'f4'), ('block', 'O'), ('time', 'f4'), ('max_time', 'f4')
        ])
        
        particle_index = 0
        
        for idx, row in enumerate(self.GameInstanceStruct.matrix.matrix):
            for pos, block in enumerate(row):
                if block != 0:
                    particle_index = self.generate_fizzle_particles(pos, idx, block, fizzle_particles, particle_index)
                    
        if self.GameInstanceStruct.current_tetromino is not None:
            for i, row in enumerate(self.GameInstanceStruct.current_tetromino.blocks):
                for j, value in enumerate(row):
                    if value != 0:
                        particle_index = self.generate_fizzle_particles(self.GameInstanceStruct.current_tetromino.position.x + j, self.GameInstanceStruct.current_tetromino.position.y + i, value, fizzle_particles, particle_index)    
        
        self.game_over_fizzle_particles = np.concatenate((self.game_over_fizzle_particles, fizzle_particles))
        self.got_fizzle_particles = True             
                        
        
    def generate_fizzle_particles(self, pos, idx, block, fizzle_particles, particle_index):
        x = pos * self.RenderStruct.GRID_SIZE
        y = idx * self.RenderStruct.GRID_SIZE

        x_dir = -1 if self.RNG.next_float() < 0.5 else 1
        y_dir = -1 if self.RNG.next_float() < 0.5 else 1

        x_vel = self.RNG.next_float() * self.RenderStruct.GRID_SIZE * x_dir
        y_vel = self.RNG.next_float() * self.RenderStruct.GRID_SIZE * y_dir
        scale = 1
        max_time = (self.RNG.next_float() + 0.5) * 2 + 15
        time = max_time

        fizzle_particles[particle_index] = (x, y, x_vel, y_vel, scale, block, time, max_time)
        return particle_index + 1    
    

