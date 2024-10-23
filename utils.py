import pygame
import os
import numpy as np

def lerpBlendRGBA(base:tuple, overlay:tuple, alpha:float):
    """
    linearly interpolate between two colours
    
    args:
        base (triple): a RGB colour to blend with the transparent overlay colour
        overlay (triple): a RGB colour to simulate the transparency of 
        alpha (float): 0 - 1, to simulate transparency of overlay colour
    
    returns
        (triple) a RGB colour
    """
    r1, g1, b1 = base
    r2, g2, b2 = overlay

    blend = lambda b, o: alpha * o + (1 - alpha) * b # noqa: E731

    return (blend(r1, r2), blend(g1, g2), blend(b1, b2))

def smoothstep(x):
        return x * x * x * (x * (6 * x - 15) + 10)

def get_prefix(number: float, unit: str, precision: int = 1) -> str:
    """
    Get the number in scientific notation with the correct prefix.

    Args:
        number (float): The number to convert.
        unit (str): The unit of the number.
        precision (int): The number of decimal places to round to.

    Returns:
        str: The formatted number with the appropriate SI prefix.
    """
    prefixes = [
        (1e-24, "y"),  # yocto
        (1e-21, "z"),  # zepto
        (1e-18, "a"),  # atto
        (1e-15, "f"),  # femto
        (1e-12, "p"),  # pico
        (1e-9, "n"),   # nano
        (1e-6, "u"),   # micro
        (1e-3, "m"),   # milli
        (1, ""),       # no prefix
        (1e3, "k"),    # kilo
        (1e6, "M"),    # mega
        (1e9, "G"),    # giga
        (1e12, "T"),   # tera
        (1e15, "P"),   # peta
        (1e18, "E"),   # exa
        (1e21, "Z"),   # zetta
        (1e24, "Y")    # yotta
    ]
    
    if number == 0:
        return f"{0:.{precision}f} {unit}"

    for value, prefix in reversed(prefixes):
        if abs(number) >= value:
            num = number / value
            return f"{num:.{precision}f} {prefix}{unit}"
  
def get_tetromino_blocks(type:str):
    """
    Get the blocks for the given tetromino.
    This is the 0th rotation state of the piece that SRS uses.
    
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
                (0, 0, 0)
            ],
        'S': 
            [
                (0, 2, 2),
                (2, 2, 0),
                (0, 0, 0)
            ],
            
        'Z':
            [
                (3, 3, 0),
                (0, 3, 3),
                (0, 0, 0)
            ],
        'L': 
            [
                (0, 0, 4),
                (4, 4, 4),
                (0, 0, 0)
            ],
        'J':
            [
                (5, 0, 0),
                (5, 5, 5),
                (0, 0, 0)
            ],
        'O': 
            [
                (6, 6), 
                (6, 6),
            ],
        'I': 
            [
                (0, 0, 0, 0),
                (7, 7, 7, 7),
                (0, 0, 0, 0),
                (0, 0, 0, 0),
            ] 
    }
    return blocks[type]

class Vec2():
    def __init__(self, x, y):
        """
        Construct a 2D vector (x , y)
        
        args:
            x (float): the x component of the vector
            y (float): the y component of the vector
        """
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"<Vec2 | x={self.x} y={self.y}>" 
    
    def __repr__(self):
        return f"<Vec2 | x={self.x} y={self.y}>"
        
    def __truediv__(self, scalar): 
        return Vec2(self.x/scalar , self.y/scalar) 
    
    def __add__(self, vec): 
        return Vec2(self.x + vec.x , self.y + vec.y)
    
    def __sub__(self, vec): 
        return Vec2((self.x - vec.x) , (self.y - vec.y))
    
    def magnitude(self): 
        return np.sqrt(self.x**2 + self.y**2)
    
    def normalise(a): 
        return a / a.magnitude()
    
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)
    
    def distance(a, b): 
        return np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)
    
def RotateSurface(surface, angle, pivot, origin):
    """
    Rotate a surface around a pivot point.

    Args:
        surf (pygame.Surface): The surface to rotate.
        angle (float): The angle to rotate the surface.
        pivot (tuple): The pivot point to rotate around.
        origin (tuple): The origin point of the surface.

    Returns:
        pygame.Surface: The rotated surface.
        pygame.Rect: The rectangle of the rotated surface.
    """
    # Convert pivot and origin to pygame vectors for calculations
    pivot = pygame.Vector2(pivot)
    origin = pygame.Vector2(origin)
    
    surf_rect = surface.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pygame.math.Vector2(origin) - surf_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_surface_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotated_surface = pygame.transform.rotate(surface, angle)
    rotated_surface_rect = rotated_surface.get_rect(center = rotated_surface_center)
    
    return rotated_surface, rotated_surface_rect

def ScaleSurface(surface, scale, pivot, origin):
    """
    Scale a surface around a pivot point.
    
    Args:
        surf (pygame.Surface): The surface to scale.
        scale (float): The scale factor.
        pivot (tuple): The pivot point to scale around.
        origin (tuple): The origin point of the surface.
    
    Returns:
        pygame.Surface: The scaled surface.
        pygame.Rect: The rectangle of the scaled surface.
    """
    pivot = pygame.Vector2(pivot)
    origin = pygame.Vector2(origin)
    surf_rect = surface.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pygame.math.Vector2(origin) - surf_rect.center
    scaled_offset = offset_center_to_pivot * scale
    scaled_surface_center = (origin[0] - scaled_offset.x, origin[1] - scaled_offset.y)
    scaled_surface = pygame.transform.scale(surface, (int(surface.get_width() * scale), int(surface.get_height() * scale)))
    scaled_surface_rect = scaled_surface.get_rect(center = scaled_surface_center)
    
    return scaled_surface, scaled_surface_rect

def TransformSurface(surface, scale, angle, pivot, origin, offset):
    pivot = pygame.Vector2(pivot)
    origin = pygame.Vector2(origin)
    offset = pygame.Vector2(offset)
    
    scaled_surface, _ = ScaleSurface(surface, scale, pivot, origin + offset)
    rotated_surface, rotated_surface_rect = RotateSurface(scaled_surface, angle, pivot * scale, origin + offset)
    return rotated_surface, rotated_surface_rect