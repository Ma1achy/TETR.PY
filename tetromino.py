class Tetromino():
    def __init__(self, type:str, x:int, y:int):
        """
        Type (str): Type of the piece S, Z, J, L, I, T, O
        State (int): Rotation state of the piece 0, 1, 2, 3
        x (int): x position of the piece
        y (int): y position of the piece
        """
        
        self.type = type
        self.state = 0
        self.positon = (x, y)
        self.blocks = self.get_blocks()[self.type]
     
        
    def rotate(self, direction:str):
        """
        Rotate the piece in the given direction
        
        direction (str): 'CW' or 'CCW'
        """
        if direction == 'CW': 
            rotated_piece = list(zip(*self.blocks[::-1])) # rotate the piece and copy it to a temporary array to check if the rotation is valid
            # always apply the 0th kick for a rotation
            
            # check if the rotation is valid by checking if the piece is within the grid or if it overlaps with another block.
            # if the rotated piece overlaps with another block or is outside the grid, recursively check if the piece can be kicked to a new position.
            # if all possible kicks have been tried and the piece still cannot be rotated, fail the rotation.
            # if the piece can be rotated, update the piece's blocks to the rotated blocks and update the piece's position to the new position.
           
            pass 
        
        elif direction == 'CCW': 
            rotated_piece = list(zip(*self.blocks))
    
            
    def get_blocks(self):
        blocks = {
            'T': [
                (0, 1, 0),
                (1, 1, 1),
                (0, 0, 0)
                ],
            'S': [
                (0, 2, 2),
                (2, 2, 0),
                (0, 0, 0)
                ],
            'Z': [
                (3, 3, 0),
                (0, 3, 3),
                (0, 0, 0)
                ],
            'L': [
                (0, 0, 4),
                (4, 4, 4),
                (0, 0, 0)
                ],
            'J': [
                (5, 0, 0),
                (5, 5, 5),
                (0, 0, 0)
                ],
            'I': [
                (0, 0, 0, 0),
                (6, 6, 6, 6),
                (0, 0, 0, 0),
                (0, 0, 0, 0)
                ],
            'O': [
                (0, 7, 7),
                (0, 7, 7),
                (0, 0, 0),
                ]
        }
        return blocks
        
piece = Tetromino('I', 0, 0)
print(piece.blocks)

piece.rotate('CCW')
print(piece.blocks)
