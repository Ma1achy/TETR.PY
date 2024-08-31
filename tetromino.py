from vec2 import Vec2
from rotation import pieces, get_kick
from matrix import Matrix

class Tetromino():
    def __init__(self, type:str, state:int, x:int, y:int):
        """
        Type (str): Type of the piece: ['T', 'S', 'Z', 'L', 'J', 'I', 'O'] 
        State (int): Rotation state of the piece: [0, 1, 2, 3]
        x (int): x position of the piece
        y (int): y position of the piece
        """
        
        self.type = type
        self.state = state
        self.position = self.get_origin(x, y)
        self.blocks = pieces(self.type)
        self.ghost_position = Vec2(self.position.x, self.position.y)
        
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
            y -= 1
        
        return Vec2(x, y)
            
    def rotate(self, direction:str, matrix:Matrix):
        """
        Rotate the piece in the given direction
        
        direction (str): The direction to rotate the piece in: ['CW', 'CCW', '180']
        matrix (Matrix): The matrix object that contains the blocks that are already placed
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
        
        self.__SRS(direction, rotated_piece, desired_state, matrix, offset = 0)
        
    def move(self, direction:str, matrix: Matrix):
        """
        Move the piece in the given direction
        
        args:
        direction (str): The direction to move the piece in: ['LEFT', 'RIGHT', 'UP' 'DOWN']
        matrix (Matrix): The matrix object that contains the blocks that are already placed
        """
        if direction == 'LEFT':
            desired_position = Vec2(self.position.x - 1, self.position.y)
        
        elif direction == 'RIGHT':
            desired_position = Vec2(self.position.x + 1, self.position.y)

        elif direction == 'UP':
            desired_position = Vec2(self.position.x, self.position.y - 1)
            
        elif direction == 'DOWN':
            desired_position = Vec2(self.position.x, self.position.y + 1)
            
        if not self.collision(self.blocks, desired_position, matrix):
            self.position = desired_position
        
    def collision(self, desired_piece_blocks:list, desired_position:Vec2, matrix:Matrix):
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
                    if desired_position.x + x < 0 or desired_position.x + x >= matrix.WIDTH: # check x bounds
                        return True
                    if desired_position.y + y <= 0 or desired_position.y + y >= matrix.HEIGHT: # check y bounds
                        return True
                    if matrix.matrix[desired_position.y + y][desired_position.x + x] != 0: # check if piece will overlap with an already placed block
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
                       
    def __SRS(self, rotation:str, rotated_piece:list, desired_state:int, matrix:list, offset:int):
        """
        Apply the Super Rotation System to the piece by recursively applying kick translations to the piece
        until a valid rotation is found or no more offsets are available
        
        rotation (str): Rotation direction ['CW', 'CCW', '180']
        rotated_piece (list): The rotated piece
        desired_state (int): Desired rotation state of the piece [0, 1, 2, 3]
        matrix (Matrix): The matrix object that contains the blocks that are already placed
        offset (int): Offset order to use when calculating the kick translation
        """
        kick = get_kick(rotation, self.type, self.state, desired_state, offset)
        
        if kick is None: # no more offsets to try => rotation is invalid
            return

        kick = Vec2(kick.x, -kick.y) # have to invert y as top left of the matrix is (0, 0)
         
        if self.collision(rotated_piece, self.position + kick, matrix): 
            self.__SRS(rotation, rotated_piece, desired_state, matrix, offset + 1)
        else:
            self.state = desired_state
            self.blocks = rotated_piece
            self.position += kick
                
    def ghost(self, matrix:Matrix):
        """
        Create a ghost piece that shows where the piece will land
        
        matrix (Matrix): The matrix object that contains the blocks that are already placed
        """
        self.ghost_position = Vec2(self.position.x, self.position.y)
        
        while not self.collision(self.blocks, self.ghost_position, matrix):
            self.ghost_position.y += 1
            
        self.ghost_position.y -= 1
        self.ghost_position.x = self.position.x 
          
        if not self.collision(self.blocks, self.ghost_position, matrix):
            matrix.ghost_blocks = matrix.init_matrix()
            matrix.insert_blocks(self.blocks, self.ghost_position, matrix.ghost_blocks)
        