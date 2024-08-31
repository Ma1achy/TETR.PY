import os
from vec2 import Vec2
class Matrix():
    def __init__(self, WIDTH:int, HEIGHT:int):
        """
        Create a matrix that represents the game field
        
        args:
        WIDTH (int): The width of the matrix
        HEIGHT (int): The height of the matrix
        """
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.matrix = self.init_matrix() # blocks that are already placed
        self.piece = self.init_matrix() 
        self.ghost_blocks = self.init_matrix()
        
    def init_matrix(self):
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
        for y, row in enumerate(blocks):
            for x, val in enumerate(row):
                if val != 0:
                    target_matrix[position.y + y][position.x + x] = val
                    
    def clear_piece(self):
        """
        Remove the piece from the matrix
        """
        self.piece = self.init_matrix()
    
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
        
        for y, row in enumerate(self.ghost_blocks):
            for x, val in enumerate(row):
                if val != 0:
                    display_matrix[y][x] = -val  # use negative value for ghost piece
                    
        for y, row in enumerate(self.piece):
            for x, val in enumerate(row):
                if val != 0:
                    display_matrix[y][x] = val
                    
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
        