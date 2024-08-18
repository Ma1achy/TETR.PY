from maths import Vec2
from srs import get_rotation_state

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
        print(self.state)
        self.positon = (x, y)
        self.blocks = get_rotation_state(self.type, self.state)
        
    def rotate(self, direction:str):
        """
        Rotate the piece in the given direction
        
        direction (str): 'CW' or 'CCW'
        """
        if direction == 'CW':     
            desired_state = (self.state + 1) % 4
            print(desired_state)
            rotated_piece = get_rotation_state(self.type, desired_state)
            
            pass 
        
        elif direction == 'CCW': 
            desired_state = (self.state - 1) % 4
            print(desired_state)
            rotated_piece = get_rotation_state(self.type, desired_state)
            
            pass
        
        elif direction == '180':
            desired_state = (self.state + 2) % 4
            print(desired_state)
            rotated_piece = get_rotation_state(self.type, desired_state)
         
            pass
        
        self.blocks = rotated_piece
        
        pass
        
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

        2/ kicks are calculated by taking the desired rotation state offset and subtracting the initial rotation state offset from it to obtain a translation vector. 

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

piece.rotate('180')
print(piece.blocks)
