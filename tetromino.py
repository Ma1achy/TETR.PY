from vec2 import Vec2
from srs import pieces

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
        y = -y # invert y coordinates as the origin is at the top left for the matrix
        
        if self.type in ['S', 'Z', 'J', 'L', 'T', 'O']:  # 3x3 box, origin is at the center
           y -= 2
           x -= 1                                       
           
        elif self.type == 'I': # 5x5 box, origin is at the center                 
            x -= 2
            y -= 2
        
        return Vec2(x, y)
            
    def rotate(self, direction:str):
        """
        Rotate the piece in the given direction
        
        direction (str): 'CW' or 'CCW'
        """
        if direction == 'CW':     
            desired_state = (self.state + 1) % 4
            print(desired_state)
            rotated_piece = self.__rotate_cw()
            print (rotated_piece)
            
            pass 
        
        elif direction == 'CCW': 
            desired_state = (self.state - 1) % 4
            print(desired_state)
            rotated_piece = self.__rotate_ccw()
            print (rotated_piece)
            
            pass
        
        elif direction == '180':
            desired_state = (self.state + 2) % 4
            print(desired_state)
            rotated_piece = self.__rotate_180()
            print (rotated_piece)
         
            pass
        
        pass
    
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
               
    def __validate_rotation(self, rotated_piece, desired_state):
        """
        Check if the rotated piece is valid
        
        rotated_piece (list): The rotated piece
        desired_state (int): The desired rotation state of the piece
        """
        pass
    
    def __SRS(self, rotated_piece, desired_state):
        """
        Apply the Super Rotation System algorithm
        
        1 / apply a kick to the piece starting from the 0th kick. 

        2/ kicks are calculated by taking the desired rotation state offset and subtracting it from the initial rotation state offset to obtain a translation vector. 

        3/ if the kicked and rotated piece would overlap with another block or is outside the grid (invalid rotation), recursively check if the piece can be kicked to a new (valid) position.

        4/ if the rotation and kick is valid apply the kick and the rotation

        5/ if all possible kicks have been exhausted and the piece still cannot be rotated, fail the rotation.
            
        rotated_piece (list): The rotated piece
        desired_state (int): The desired rotation state of the piece
        """
        
        if self.type == 'I':
            pass
        pass
                    
piece = Tetromino('T', 0, 0, 0)
print(piece.blocks)

piece.rotate('CW')
