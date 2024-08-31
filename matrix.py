import os
class Matrix():
    def __init__(self, WIDTH:int, HEIGHT:int):
        
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.matrix = self.init_matrix() # blocks that are already placed
        self.piece = self.init_matrix() 
        self.ghost_blocks = self.init_matrix()
        
    def init_matrix(self):
        return [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
    
    def __str__(self):
        
        os.system('cls' if os.name == 'nt' else 'clear')
        
        color_map = {
            0: "\033[30m",  # Black
            1: "\033[35m",  # Purple
            2: "\033[32m",  # Lime
            3: "\033[31m",  # Red
            4: "\033[33m",  # Orange
            5: "\033[34m",  # Blue
            6: "\033[93m",  # Yellow
            7: "\033[36m",  # Cyan
        }

        # Create a copy of the matrix to include the current piece and ghost piece
        display_matrix = [row[:] for row in self.matrix]

        # Insert ghost piece into the display matrix
        for y, row in enumerate(self.ghost_blocks):
            for x, val in enumerate(row):
                if val != 0:
                    display_matrix[y][x] = -val  # Use negative value for ghost piece

        # Insert current piece into the display matrix
        for y, row in enumerate(self.piece):
            for x, val in enumerate(row):
                if val != 0:
                    display_matrix[y][x] = val

        # Generate the string representation
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
    
    def insert_blocks(self, blocks, position, target_matrix):
        for y, row in enumerate(blocks):
            for x, val in enumerate(row):
                if val != 0:
                    target_matrix[position.y + y][position.x + x] = val
                    
    def clear_piece(self):
        self.piece = self.init_matrix()
        
   
        