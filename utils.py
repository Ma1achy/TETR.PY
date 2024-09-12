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
    
    def action_ui(self):
        font_path = os.path.join(self.base_path, 'action-icons.ttf')
        return pygame.font.Font(font_path, self.size)

def get_prefix(number, unit, precision = 1):
    prefixes = [
        (1e-24, "y"),  # yocto
        (1e-21, "z"),  # zepto
        (1e-18, "a"),  # atto
        (1e-15, "f"),  # femto
        (1e-12, "p"),  # pico
        (1e-9, "n"),   # nano
        (1e-6, "u"),   # micro
        (1e-3, "m"),   # milli
        (1, ""),       
        (1e3, "k"),    # kilo
        (1e6, "M"),    # mega
        (1e9, "G"),    # giga
        (1e12, "T"),   # tera
        (1e15, "P"),   # peta
        (1e18, "E"),   # exa
        (1e21, "Z"),   # zetta
        (1e24, "Y")    # yotta
    ]

    # get exponent of number
    num_exp = int(f"{number:.0e}".split("e")[1])
    # get decimal component of number
    diffs = []
        
    # get prefix of number from exp by finding the closest prefix
    for (value, prefix) in prefixes:
        prefix_exp = int(f"{value:.0e}".split("e")[1])
        diff = prefix_exp - num_exp
        diffs.append((prefix, diff, value))
    
    prefix, _, value = min(diffs, key = lambda x: (abs(x[1]), x[0]))
    num = number / value
    
    return f"{num:.{precision}f} {prefix}{unit}" 
  
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