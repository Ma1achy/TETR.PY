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
        self.HEIGHT = HEIGHT
        self.matrix = self.empty_matrix() # blocks that are already placed
        self.piece = self.empty_matrix() 
        self.ghost = self.empty_matrix()
        self.danger = self.empty_matrix()
        
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
        
    def clear_piece(self):
        """
        Remove the piece from the matrix
        """
        self.piece = self.empty_matrix()
        
    def clear_lines(self):
        """
        Remove full lines from the matrix
        """
        full_lines = [row for row in self.matrix if all(val != 0 for val in row)]
        
        [self.matrix.insert(0, [0 for _ in range(self.WIDTH)]) for row in full_lines if self.matrix.remove(row) is None]

        if len(full_lines) > 0:
            return len(full_lines)
    
    def __str__(self):
        """
        String representation of the matrix
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        
        color_map = {
            0: "\033[30m",  # black
            1: "\033[35m",  # purple
            2: "\033[32m",  # lime
            3: "\033[31m",  # red
            4: "\033[33m",  # orange
            5: "\033[34m",  # blue
            6: "\033[93m",  # yellow
            7: "\033[36m",  # cyan
        }

        display_matrix = [row[:] for row in self.matrix]
            
        [
            display_matrix[y].__setitem__(x, -val)
            
            for y, row in enumerate(self.piece)
            for x, val in enumerate(row)
            if val != 0
        ]
                    
        [
            display_matrix[y].__setitem__(x, val)
            
            for y, row in enumerate(self.ghost)
            for x, val in enumerate(row)
            if val != 0
        ]
                    
        rows = [
            "| " + " ".join(
                f"{color_map[abs(val)]}#\033[0m" if 1 <= val <= 7 else
                f"{color_map[abs(val)]}.\033[0m" if val < 0 else
                f"{color_map[0]}.\033[0m" for val in row
            ) + " |"
            for row in display_matrix[20:40]
        ]
        bottom_border = "=" * (self.WIDTH * 2 + 3)  # 2 chars per element + 2 spaces + 2 '|' + 1 space
        return "\n\n"+ "\n".join(rows) + "\n" + bottom_border
        