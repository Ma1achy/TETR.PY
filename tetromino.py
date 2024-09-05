from vec2 import Vec2
from rotation import TSZLJ_OFFSETS, I_OFFSETS, O_OFFSETS, TSZLKJ_180_OFFSETS, I_180_OFFSETS
from matrix import Matrix

# probably want to change how pieces are defined, copying the SRS internal states is probably not ideal
# O can just be a 2x2 matrix, I and be a 1x4 matrix, the rest can be 3x2 matrices.
# rotations will then just have to be calculated about the "pivot"/origin of the piece, which remains in the same position (unless a kick is applied)

# Movement will also need to be changed to allow for DAS and ARR along with input buffering from the asynchronous input system
# rather than the actions being passed directly from the pygame instance to here, they should be passed to a handling object that will
# maintains a buffer of fixed length and decides when to apply the actions to the piece based on their time stamps and the tick time stamps
# actions that are too old compared to future or current ticks outside a threshold will be discarded
# if the tick rate drops (delta tick increases) you can expand the threshold to allow for more input buffering up to a certain point
# if the tick rate increases (delta tick decreases) you can reduce the threshold to reduce input buffering to make it less sticky
# das and arr can also be implemented there
class Tetromino():
    def __init__(self, type:str, state:int, x:int, y:int, matrix:Matrix):
        """
        Type (str): Type of the piece: ['T', 'S', 'Z', 'L', 'J', 'I', 'O'] 
        State (int): Rotation state of the piece: [0, 1, 2, 3]
        x (int): x position of the piece
        y (int): y position of the piece
        matrix (Matrix): The matrix object that contains the blocks that are already placed
        """
        
        self.type = type
        self.state = state
        self.position = self.get_origin(x, y)
        self.matrix = matrix
        
        self.blocks = self.get_tetromino_blocks()
        self.ghost_position = Vec2(self.position.x, self.position.y)
        self.on_floor = False
        
        # default state is 0, but this is allows for pre-rotation
        if self.state == 1:
            self.blocks = self.__rotate_cw()
        elif self.state == 2:
            self.blocks = self.__rotate_180()
        elif self.state == 3:
            self.blocks = self.__rotate_ccw()
    
    def get_origin(self, x:int, y:int):
        """
        Get the origin of the piece
        
        x (int): x position of the piece
        y (int): y position of the piece
        """
        
        if self.type in ['S', 'Z', 'J', 'L', 'T', 'O']:  
           x -= 1                                       
           y -= 1
        
        elif self.type == 'I':                 
            x -= 2
            y -= 2
        
        return Vec2(x, y)
            
    def rotate(self, direction:str):
        """
        Rotate the piece in the given direction
        
        direction (str): The direction to rotate the piece in: ['CW', 'CCW', '180']
        """
        if direction == 'CW':     
            desired_state = (self.state + 1) % 4
            rotated_piece = self.__rotate_cw()
        
        elif direction == 'CCW': 
            desired_state = (self.state - 1) % 4
            rotated_piece = self.__rotate_ccw()

        elif direction == '180':
            desired_state = (self.state + 2) % 4
            rotated_piece = self.__rotate_180()
        
        self.__SRS(direction, rotated_piece, desired_state, offset = 0)
        
    def move(self, direction:str):
        """
        Move the piece in the given direction
        
        args:
        direction (str): The direction to move the piece in: ['LEFT', 'RIGHT', 'UP' 'DOWN']
        """
        if direction == 'LEFT':
            desired_position = Vec2(self.position.x - 1, self.position.y)
        
        elif direction == 'RIGHT':
            desired_position = Vec2(self.position.x + 1, self.position.y)

        elif direction == 'UP':
            desired_position = Vec2(self.position.x, self.position.y - 1)
            
        elif direction == 'DOWN':
            desired_position = Vec2(self.position.x, self.position.y + 1)
            
        if not self.collision(self.blocks, desired_position):
            self.position = desired_position
        
    def collision(self, desired_piece_blocks:list, desired_position:Vec2):
        """
        Check if the piece at the desired position will collide with the matrix bounds or other blocks
        
        args:
        desired_piece_blocks (list): The blocks of the piece at the desired position
        desired_position (Vec2): The desired position of the piece
        matrix (Matrix): The matrix object that contains the blocks that are already placed
        
        returns
        (bool): True if the piece will collide, False otherwise
        """
        for y, row in enumerate(desired_piece_blocks):
            for x, val in enumerate(row):
                if val != 0: 
                    if desired_position.x + x < 0 or desired_position.x + x >= self.matrix.WIDTH: # check x bounds
                        return True
                    if desired_position.y + y <= 0 or desired_position.y + y >= self.matrix.HEIGHT: # check y bounds
                        return True
                    if self.matrix.matrix[desired_position.y + y][desired_position.x + x] != 0: # check if piece will overlap with an already placed block
                        return True            
        
    def __rotate_cw(self):
        """
        Rotate the piece clockwise
        """
        return [list(reversed(col)) for col in zip(*self.blocks)]
    
    def __rotate_ccw(self):
        """
        Rotate the piece counter clockwise
        """
        return [list(col) for col in reversed(list(zip(*self.blocks)))]
    
    def __rotate_180(self):
        """
        Rotate the piece 180 degrees
        """
        return [row[::-1] for row in reversed(self.blocks)]
                       
    def __SRS(self, rotation:str, rotated_piece:list, desired_state:int, offset:int):
        """
        Apply the Super Rotation System to the piece by recursively applying kick translations to the piece
        until a valid rotation is found or no more offsets are available
        
        rotation (str): Rotation direction ['CW', 'CCW', '180']
        rotated_piece (list): The rotated piece
        desired_state (int): Desired rotation state of the piece [0, 1, 2, 3]
        offset (int): Offset order to use when calculating the kick translation
        """
        kick = self.get_kick(rotation, self.type, desired_state, offset)
        
        if kick is None: # no more offsets to try => rotation is invalid
            return

        kick = Vec2(kick.x, -kick.y) # have to invert y as top left of the matrix is (0, 0)
         
        if self.collision(rotated_piece, self.position + kick): 
            self.__SRS(rotation, rotated_piece, desired_state, offset + 1)
        else:
            if self.type == 'T':
                self.__Is_T_Spin(offset, desired_state, kick)
                
            self.state = desired_state
            self.blocks = rotated_piece
            self.position += kick
    
    def get_kick(self, rotation:str, piece:str, desired_state:int, offset_order:int):
        """
        Get the kick translation to apply to the piece
        kick = initial_state_offset - desired_state_offset
        
        args:
        rotation (str): Rotation direction: ['CW', 'CCW', '180']
        piece (str): Type of the piece: ['T', 'S', 'Z', 'L', 'J', 'I', 'O']
        initial_state (int): Initial rotation state of the piece: [0, 1, 2, 3]
        desired_state (int): Desired rotation state of the piece: [0, 1, 2, 3]
        offset_order (int): Offset order to use 
        
        returns:
        kick (Vec2): The kick translation to apply to the piece
        """
        if rotation in ['CW', 'CCW']:
            if piece in ['T', 'S', 'Z', 'L', 'J']:
                
                if offset_order > len(TSZLJ_OFFSETS[0]) - 1:
                    return None
                else:
                    desired_state_offset = TSZLJ_OFFSETS[desired_state][offset_order]
                    initial_state_offset = TSZLJ_OFFSETS[self.state][offset_order]
                
            elif piece == 'O':
                
                if offset_order > len(O_OFFSETS[0]) - 1:
                    return None
                else:
                    desired_state_offset = O_OFFSETS[desired_state][offset_order]
                    initial_state_offset = O_OFFSETS[self.state][offset_order]
                
            elif piece == 'I':
                
                if offset_order > len(I_OFFSETS[0]) - 1:
                    return None
                else:
                    desired_state_offset = I_OFFSETS[desired_state][offset_order]
                    initial_state_offset = I_OFFSETS[self.state][offset_order]
                
        elif rotation == '180':
            if piece in ['T', 'S', 'Z', 'L', 'J']:
                
                if offset_order > len(TSZLKJ_180_OFFSETS[0]) - 1:
                    return None
                else:
                    desired_state_offset = TSZLKJ_180_OFFSETS[desired_state][offset_order]
                    initial_state_offset = TSZLKJ_180_OFFSETS[self.state][offset_order]
                
            elif piece == 'O':
                
                if offset_order > len(O_OFFSETS[0]) - 1:
                    return None
                else:
                    desired_state_offset = O_OFFSETS[desired_state][offset_order]
                    initial_state_offset = O_OFFSETS[self.state][offset_order]
                
            elif piece == 'I':
                
                if offset_order > len(I_180_OFFSETS[0]) - 1:
                    return None
                else:
                    desired_state_offset = I_180_OFFSETS[desired_state][offset_order]
                    initial_state_offset = I_180_OFFSETS[self.state][offset_order]
                    
        return initial_state_offset - desired_state_offset
            
    def __Is_T_Spin(self, offset:int, desired_state:int, kick:Vec2):
        """
        Test if the T piece rotation is a T-spin.
        
        A Spin is a T spin if:
            1/ 3 out of 4 corners of the T piece are filled and the piece "faces" 2 of the filled corners.
            2/ The direction a T piece faces is the direction the non-flat side of the T piece "points".
        
        A Spin is a T-Spin Mini if:
            1/ 1 corner of the T piece is filled and the piece "faces" the filled corner.
            2/ The 2 back corners of the T piece are filled.
        
            Exceptions to T-Spin Mini:
                If the last kick translation was used when rotating from 0 to 3, it is a full T-spin despite not meeting the above conditions.
                If the last kick translation was used when rotating from 2 to 1, it is a full T-spin despite not meeting the above conditions.  
        
        args:
        offset (int): Offset order to use when calculating the kick translation
        desired_state (int): Desired rotation state of the piece [0, 1, 2, 3]
        kick (Vec2): The kick translation to apply       
        """
        corner_pairs = {
            0: [Vec2(0, 0), Vec2(2, 0)],
            1: [Vec2(2, 0), Vec2(2, 2)],
            2: [Vec2(2, 2), Vec2(0, 2)],
            3: [Vec2(0, 2), Vec2(0, 0)]
        }
        
        def set_t_sin_flag(flag):
            pass
            
        filled_corners = self.__test_corners(corner_pairs[desired_state], kick) # do facing test
            
        if len(filled_corners) == 1: # 1 corner test for T-Spin Mini
    
            filled_corners = self.__test_corners(corner_pairs[(desired_state + 2) % 4], kick) # do back corner test
            
            if len(filled_corners) > 1:
                
                if (self.state == 0 and desired_state == 3 and offset == 4) or (self.state == 2 and desired_state == 1 and offset == 4): # exception to T-Spin Mini https://four.lol/srs/t-spin#exceptions
                    set_t_sin_flag("T-Spin")
                else:
                    set_t_sin_flag("T-Spin Mini")
            
        elif len(filled_corners) == 2: # 2 corner test for T-Spin
        
            corners = [Vec2(0, 0), Vec2(2, 0), Vec2(0, 2), Vec2(2, 2)]
            filled_corners = self.__test_corners(corners, kick)
            
            if len(filled_corners) >= 3: # 3 corner test for T-Spin
                set_t_sin_flag("T-Spin")
        else:
            set_t_sin_flag(None)
        
    def __test_corners(self, corners:list, kick:Vec2):
        """
        Test if the corners of the pieces bounding box are occupied
        
        args:
        corners (list): The corners of the piece bounding box
        kick (Vec2): The kick translation to apply
        
        returns:
        filled_corners (list): The corners that are occupied
        """
        filled_corners = []
        
        for idx, corner in enumerate(corners):
            
            corner_pos = self.position + kick + corner
            
            if corner_pos.x < 0 or corner_pos.x >= self.matrix.WIDTH or corner_pos.y < 0 or corner_pos.y >= self.matrix.HEIGHT:
                filled_corners.append(corner)
            else:
                if self.matrix.matrix[corner_pos.y][corner_pos.x] != 0:
                    filled_corners.append(corner)
                                        
        return filled_corners     
       
    def ghost(self):
        """
        Create a ghost piece that shows where the piece will land
        """
        self.ghost_position = Vec2(self.position.x, self.position.y)
        
        while not self.collision(self.blocks, self.ghost_position):
            self.ghost_position.y += 1
            
        self.ghost_position.y -= 1
        self.ghost_position.x = self.position.x 
          
        if not self.collision(self.blocks, self.ghost_position):
            self.matrix.ghost = self.matrix.empty_matrix()
            self.matrix.insert_blocks(self.blocks, self.ghost_position, self.matrix.ghost)

    def get_tetromino_blocks(self):
        """
        Get the blocks for the given tetromino.
        This is the 0th rotation state of the piece that SRS uses.
        
        args:
        type (str): The type of tetromino
        
        returns:
        blocks (list): The pieces blocks
        """
        blocks = {
            'T':
                [
                    (0, 1, 0),
                    (1, 1, 1),
                    (0, 0, 0)
                ],
            'S': 
                [
                    (0, 2, 2),
                    (2, 2, 0),
                    (0, 0, 0)
                ],
                
            'Z':
                [
                    (3, 3, 0),
                    (0, 3, 3),
                    (0, 0, 0)
                ],
            'L': 
                [
                    (0, 0, 4),
                    (4, 4, 4),
                    (0, 0, 0)
                ],
            'J':
                [
                    (5, 0, 0),
                    (5, 5, 5),
                    (0, 0, 0)
                ],
            'O': 
                [
                    (0, 6, 6), 
                    (0, 6, 6),
                    (0, 0, 0)
                ],
            'I': 
                [
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 7, 7, 7, 7),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0)
                ] 
        }
        return blocks[self.type]