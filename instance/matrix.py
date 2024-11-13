import os
from  utils import Vec2

class Matrix():
    def __init__(self, WIDTH:int, HEIGHT:int):
        """
        Represents the game matrix (or board) where the tetrominoes are placed and interact.
        
        Manages the state of the game matrix, including the static blocks, active piece, and the ghost piece.
        
        args:
            WIDTH (int): The width of the matrix
            HEIGHT (int): The height of the matrix
            
        methods:
            empty_matrix(): Create a matrix filled with zeros
            insert_blocks(blocks, position, target_matrix): Insert the piece blocks into the target matrix
            clear_piece(): Remove the piece from the matrix
            clear_lines(): Remove full lines from the matrix
            __str__(): String representation of the matrix
        """
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT * 2
        self.matrix = self.empty_matrix() # blocks that are already placed
        self.spawn_overlap = self.empty_matrix() 

    def empty_matrix(self):
        """
        Create a matrix filled with zeros	
        """
        return [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
    
    def insert_blocks(self, blocks:list, position:Vec2, target_matrix:list):
        """
        Insert the piece blocks into the target matrix
        
        args:
            blocks (list): The piece blocks
            position (Vec2): The position of the piece
            target_matrix (list): The matrix to insert the piece blocks into
        """
        [
            target_matrix[position.y + y].__setitem__(position.x + x, val)
            
            for y, row in enumerate(blocks)
            for x, val in enumerate(row)
            if val != 0
        ]
        
    def clear_lines(self):
        """
        Remove full lines from the matrix and return the number of lines cleared,
        the full lines, and their indices.
        """
        full_idxs = [idx for idx, row in enumerate(self.matrix) if all(val != 0 for val in row)]
        full_lines = [self.matrix[idx] for idx in full_idxs]
        [self.matrix.insert(0, [0 for _ in range(self.WIDTH)]) for row in full_lines if self.matrix.remove(row) is None]
        
        if len(full_lines) > 0:
            return len(full_idxs), full_lines, full_idxs
        else:
            return None, None, None
    
    def __str__(self):
        """
        String representation of the matrix
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        
        color_map = {
            0: "\033[30m",  # black
            'T': "\033[35m",  # purple
            'S': "\033[32m",  # lime
            'Z': "\033[31m",  # red
            'L': "\033[33m",  # orange
            'J': "\033[34m",  # blue
            'O': "\033[93m",  # yellow
            'I': "\033[36m",  # cyan
        }

        display_matrix = [row[:] for row in self.matrix]
                    
        rows = [
            "| " + " ".join(
                f"{color_map[val]}#\033[0m" if val != 0 else
                f"{color_map[val]}.\033[0m" if val < 0 else
                f"{color_map[0]}.\033[0m" for val in row
            ) + " |"
            for row in display_matrix[20:40]
        ]
        bottom_border = "=" * (self.WIDTH * 2 + 3)  # 2 chars per element + 2 spaces + 2 '|' + 1 space
        return "\n\n"+ "\n".join(rows) + "\n" + bottom_border
        