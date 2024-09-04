import pygame
import os

def lerpBlendRGBA(base:tuple, overlay:tuple, alpha:float):
    """
    linearly interpolate between two colours
    
    args:æ
    base (triple): a RGB colour to blend with the transparent overlay colour
    overlay (triple): a RGB colour to simulate the transparency of 
    alpha (float): 0 - 1, to simulate transparency of overlay colour
    
    returns
    (triple) a RGB colour
    """
    r1, g1, b1 = base
    r2, g2, b2 = overlay

    blend = lambda b, o: alpha * o + (1 - alpha) * b    # noqa: E731

    return (blend(r1, r2), blend(g1, g2), blend(b1, b2))

class Font():
    def __init__(self, size: int = 20):
        self.size = size
        self.base_path = os.path.join(os.path.dirname(__file__), 'font')
    
    def hun2(self):
        font_path = os.path.join(self.base_path, 'hun2.ttf')
        return pygame.font.Font(font_path, self.size)
    
    def pfw(self):
        font_path = os.path.join(self.base_path, 'pfw.ttf')
        return pygame.font.Font(font_path, self.size)
    
    def cr(self):
        font_path = os.path.join(self.base_path, 'cr.ttf')
        return pygame.font.Font(font_path, self.size)
    
def get_tetromino_blocks(type:str):
    """
    Get the blocks for the given tetromino to render previews.
  
    args:
    type (str): The type of tetromino
    
    returns:
    blocks (list): The pieces blocks
    """
    blocks = {
        'T':
            [
                (0, 1, 0),
                (1, 1, 1),
            ],
        'S': 
            [
                (0, 2, 2),
                (2, 2, 0),
            ],
            
        'Z':
            [
                (3, 3, 0),
                (0, 3, 3),
            ],
        'L': 
            [
                (0, 0, 4),
                (4, 4, 4),
            ],
        'J':
            [
                (5, 0, 0),
                (5, 5, 5),
            ],
        'O': 
            [
                (6, 6), 
                (6, 6),
            ],
        'I': 
            [
                (7, 7, 7, 7),
            ] 
    }
    return blocks[type]