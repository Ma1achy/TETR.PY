class Matrix():
    def __init__(self, WIDTH:int, HEIGHT:int):
        
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.matrix = self.__init_matrix()
        
    def __init_matrix(self):
        return [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
    
    def __str__(self):
        
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
        reset_color = "\033[0m"
        
        rows = [
            "| " + " ".join(f"{color_map[val]}{val}{reset_color}" for val in row) + " |"
            for row in self.matrix
        ]
        bottom_border = "=" * (self.WIDTH * 2 + 3)  # 2 chars per element + 2 spaces + 2 '|' + 1 space
        return "\n\n\n" + "\n".join(rows) + "\n" + bottom_border
        
matrix = Matrix(10, 20)
print(matrix)