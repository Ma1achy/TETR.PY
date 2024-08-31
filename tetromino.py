from vec2 import Vec2
from srs import pieces, get_kick

class Tetromino():
    def __init__(self, type:str, state:int, x:int, y:int):
        """
        Type (str): Type of the piece S, Z, J, L, I, T, O
        State (int): Rotation state of the piece 0, 1, 2, 3
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
        
        if self.type in ['S', 'Z', 'J', 'L', 'T']:  # 3x3 box, origin is at the center
           x -= 1                                       
           y -= 1
        
        elif self.type == 'O': 
            x -= 1
            y -= 1
           
        elif self.type == 'I': # 5x5 box, origin is at the center                 
            x -= 2
            y -= 1
        
        return Vec2(x, y)
            
    def rotate(self, direction:str, matrix):
        """
        Rotate the piece in the given direction
        
        direction (str): 'CW' or 'CCW'
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
        
    def move(self, direction:str, matrix):
        """
        Move the piece in the given direction
        
        direction (str): 'LEFT', 'RIGHT', 'DOWN', 'UP'
        """
        if direction == 'LEFT':
            desired_position = Vec2(self.position.x - 1, self.position.y)
        
        elif direction == 'RIGHT':
            desired_position = Vec2(self.position.x + 1, self.position.y)

        elif direction == 'DOWN':
            desired_position = Vec2(self.position.x, self.position.y + 1)

        elif direction == 'UP':
            desired_position = Vec2(self.position.x, self.position.y - 1)
            
        if not self.collision(self.blocks, desired_position, matrix):
            self.position = desired_position
        
    def collision(self, desired_piece_blocks, desired_position, matrix):
    
        # check if piece at desired position will overlap with a matrix block (non zero value)
        # check if part of piece (non zero value) is outside the matrix
        
        for y, row in enumerate(desired_piece_blocks):
            for x, val in enumerate(row):
                if val != 0: 
                    # check x bounds
                    if desired_position.x + x < 0 or desired_position.x + x >= matrix.WIDTH:
                        return True
                    
                    # check y bounds
                    if desired_position.y + y <= 0 or desired_position.y + y >= matrix.HEIGHT:
                        return True
                    
                    # check if piece will overlap with an already placed block
                    if matrix.matrix[desired_position.y + y][desired_position.x + x] != 0:
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
                       
    def __SRS(self, rotation, rotated_piece, desired_state, matrix, offset):
    
        kick = get_kick(rotation, self.type, self.state, desired_state, offset)
        
        if kick is None:
            return

        kick = Vec2(kick.x, -kick.y) # have to invert y as top left of the matrix is (0, 0)
         
        if self.collision(rotated_piece, self.position + kick, matrix):
            self.__SRS(rotation, rotated_piece, desired_state, matrix, offset + 1)
        else:
            self.state = desired_state
            self.blocks = rotated_piece
            self.position += kick
    
    def place(self, matrix):
        """
        Place the piece in the matrix
        """
        if not self.collision(self.blocks, self.position, matrix):
            matrix.place_piece(self)
            
    def ghost(self, matrix):
        """
        Get the ghost piece
        """
        self.ghost_position = Vec2(self.position.x, self.position.y)
        while not self.collision(self.blocks, self.ghost_position, matrix):
            self.ghost_position.y += 1
        self.ghost_position.y -= 1
        self.ghost_position.x = self.position.x 
          
        if not self.collision(self.blocks, self.ghost_position, matrix):
            matrix.ghost_blocks = matrix.init_matrix()
            matrix.insert_ghost_blocks(self)
        