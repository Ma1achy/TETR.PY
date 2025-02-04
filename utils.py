import pygame
import numpy as np
from scipy.ndimage import gaussian_filter
import json
import subprocess
import platform
import math

def lerpBlendRGBA(base:tuple, overlay:tuple, alpha:float):
    """
    linearly interpolate between two colours
    
    args:
        base (triple): a RGB colour to blend with the transparent overlay colour
        overlay (triple): a RGB colour to simulate the transparency of 
        alpha (float): 0 - 1, to simulate transparency of overlay colour
    .
    returns
        (triple) a RGB colour
    """
    r1, g1, b1 = base
    r2, g2, b2 = overlay

    blend = lambda b, o: alpha * o + (1 - alpha) * b # noqa: E731

    return (blend(r1, r2), blend(g1, g2), blend(b1, b2))

def smoothstep(x):
    """
    Smoothstep function to interpolate between two values
    
    args:
        x (float): The interpolation factor
    """
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
        
def comma_separate(number: int) -> str:
    """
    Add commas to a number for readability.

    Args:
        number (int): The number to add commas to.

    Returns:
        str: The number with commas.
    """
    return "{:,}".format(number)
  
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
        'Z':
            [
                ('Z', 'Z',  0 ),
                ( 0 , 'Z', 'Z'),
                ( 0 ,  0 ,  0 )
            ],
        'L': 
            [
                ( 0 ,  0 , 'L'),
                ('L', 'L', 'L'),
                ( 0 ,  0 ,  0 )
            ],
        'O': 
            [
                ('O', 'O'), 
                ('O', 'O'),
            ],
        'S': 
            [
                ( 0 , 'S', 'S'),
                ('S', 'S',  0 ),
                ( 0 ,  0 ,  0 )
            ],
        'I': 
            [
                ( 0 ,  0 ,  0 ,  0 ),
                ('I', 'I', 'I', 'I'),
                ( 0 ,  0 ,  0 ,  0 ),
                ( 0 ,  0 ,  0 ,  0 ),
            ],
        'J':
            [
                ('J',  0 ,  0 ),
                ('J', 'J', 'J'),
                ( 0 ,  0 ,  0 )
            ],    
        'T':
            [
                ( 0 , 'T',  0 ),
                ('T', 'T', 'T'),
                ( 0 ,  0 ,  0 )
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
    if angle == 0:
        return surface, surface.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    
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
    if scale == 1:
        return surface, surface.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    
    surf_rect = surface.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pygame.math.Vector2(origin) - surf_rect.center
    scaled_offset = offset_center_to_pivot * scale
    scaled_surface_center = (origin[0] - scaled_offset.x, origin[1] - scaled_offset.y)
    scaled_surface = pygame.transform.smoothscale(surface, (int(surface.get_width() * scale), int(surface.get_height() * scale)))
    scaled_surface_rect = scaled_surface.get_rect(center = scaled_surface_center)
    
    return scaled_surface, scaled_surface_rect

def TransformSurface(surface, scale, angle, pivot, origin, offset):
    """
    Transform a surface by scaling and rotating it around a pivot point.
    
    args:
        surface (pygame.Surface): The surface to transform.
        scale (float): The scale factor.
        angle (float): The angle to rotate the surface.
        pivot (tuple): The pivot point to rotate around.
        origin (tuple): The origin point of the surface.
        offset (tuple): The offset of the surface."""
    if scale < 0:
        scale = 1e-6
        
    scaled_surface, _ = ScaleSurface(surface, scale, pivot, origin + offset)
    rotated_surface, rotated_surface_rect = RotateSurface(scaled_surface, angle, pivot * scale, origin + offset)
    return rotated_surface, rotated_surface_rect

def tint_texture(texture, tint_color):
    """
    Tint the non-transparent parts of a texture with a given color.
    
    Args:
        texture (pygame.Surface): The texture to tint.
        tint_color (tuple): The color to tint with (R, G, B).
    
    Returns:
        pygame.Surface: The tinted texture.
    """
    tinted_texture = texture.copy()
    tinted_texture.lock()
    
    for x in range(tinted_texture.get_width()):
        for y in range(tinted_texture.get_height()):
            pixel_color = tinted_texture.get_at((x, y))
            if pixel_color.a != 0:  # Check if the pixel is not transparent
                # Blend the pixel color with the tint color
                blended_color = (
                    (pixel_color.r * tint_color[0]) // 255,
                    (pixel_color.g * tint_color[1]) // 255,
                    (pixel_color.b * tint_color[2]) // 255,
                    pixel_color.a
                )
                tinted_texture.set_at((x, y), blended_color)
    
    tinted_texture.unlock()
    return tinted_texture

def to_grey_scale(image):
    """
    convert a RGBA image to greyscale
    
    args:
        image (pygame.Surface): The image to convert
    """
    width, height = image.get_size()
    grey_image = pygame.Surface((width, height), flags=pygame.SRCALPHA)
    image.lock()
    grey_image.lock()

    for x in range(width):
        for y in range(height):
            r, g, b, a = image.get_at((x, y))
            grey = int(0.299 * r + 0.587 * g + 0.114 * b)
            grey_image.set_at((x, y), (grey, grey, grey, a))

    image.unlock()
    grey_image.unlock()
    
    return grey_image

def ease(current, target, t):
    """
    Easing function to interpolate between two values
    
    args:
        current (float): The current value
        target (float): The target value
        t (float): The interpolation factor
    """
    t = max(0, min(1, t)) 
    t = t * t * (3 - 2 * t)  
    return current + (target - current) * t

def ease_in_out_quad(start, end, t):
    """
    Ease in out quad function to interpolate between two values
    
    args:
        start (float): The start value
        end (float): The end value
        t (float): The interpolation factor
    """
    change = end - start
    if t < 0.5:
        return start + change * (2 * t ** 2)
    else:
        return start + change * (-1 + (4 - 2 * t) * t)
    
def ease_out_cubic(start, end, t):
    """
    Ease out cubic function to interpolate between two values
    
    args:
        start (float): The start value
        end (float): The end value
        t (float): The interpolation factor
    """
    change = end - start
    t -= 1
    return start + change * (t ** 3 + 1) 

def lerp(current, target, t):
    """
    Linear interpolation between two values
    
    args:
        current (float): The current value
        target (float): The target value
        t (float): The interpolation factor
    """
    return current + (target - current) * t 

def apply_gaussian_blur_with_alpha(surface, sigma):
    """	
    Apply a gaussian blur to a surface with an alpha channel
    
    args:
        surface (pygame.Surface): The surface to blur
        sigma (float): The standard deviation of the gaussian blur kernel
    """
    # straight alpha
    pixel_array = pygame.surfarray.array3d(surface).astype(np.float32)
    alpha_channel = pygame.surfarray.pixels_alpha(surface).astype(np.float32) / 255.0

    # convert to pre-multiplied alpha
    rgba_array = np.dstack([pixel_array * alpha_channel[:, :, None], alpha_channel])

    # apply a gaussian blur to each RGB channel and the alpha channel separately
    blurred_rgba_array = np.dstack([gaussian_filter(rgba_array[:, :, i], sigma=sigma) for i in range(4)])

    # convert back to straight alpha by dividing the RGB channels by the alpha matte
    nonzero_alpha = np.maximum(blurred_rgba_array[:, :, 3], 1e-32) # to avoid division by zero
    final_rgb = (blurred_rgba_array[:, :, :3] / nonzero_alpha[:, :, None]).clip(0, 255).astype(np.uint8)
    final_alpha = (blurred_rgba_array[:, :, 3] * 255).clip(0, 255).astype(np.uint8)

    blurred_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    pygame.surfarray.blit_array(blurred_surface, final_rgb)
    pygame.surfarray.pixels_alpha(blurred_surface)[:, :] = final_alpha

    return blurred_surface

def hex_to_rgb(hex_color):
    """Convert a hex colour to an RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def align_element(container, element_width, element_height, h_padding = 0, v_padding = 0, alignment = 'center'):
    match alignment:
        case 'top':
            return align_top_edge(container, element_width, element_height, h_padding, v_padding)
        case 'bottom':
            return align_bottom_edge(container, element_width, element_height, h_padding, v_padding)
        case 'left':
            return align_left_edge(container, element_width, element_height, h_padding, v_padding)
        case 'right':
            return align_right_edge(container, element_width, element_height, h_padding, v_padding)
        case 'top_left':
            return align_top_left(container, element_width, element_height, h_padding, v_padding)
        case 'top_right':
            return align_top_right(container, element_width, element_height, h_padding, v_padding)
        case 'bottom_left':
            return align_bottom_left(container, element_width, element_height, h_padding, v_padding)
        case 'bottom_right':
            return align_bottom_right(container, element_width, element_height, h_padding, v_padding)
        case 'center':
            return align_centre(container, element_width, element_height, h_padding, v_padding)
        case 'center_left':
            return align_center_left(container, element_width, element_height, h_padding, v_padding)
        case 'center_right':
            return align_center_right(container, element_width, element_height, h_padding, v_padding)
        case _:
            return align_centre(container, element_width, element_height, h_padding, v_padding)

def align_top_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.top + v_padding, element_width, element_height)

def align_bottom_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.bottom - element_height - v_padding, element_width, element_height)

def align_right_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.right - element_width - h_padding, container.top + v_padding, element_width, element_height)

def align_left_edge(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.top + v_padding, element_width, element_height)

def align_centre(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + (container.width - element_width) // 2 + h_padding, container.top + (container.height - element_height)//2 + v_padding, element_width, element_height)

def align_bottom_left(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.bottom - element_height - v_padding, element_width, element_height)

def align_bottom_right(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.right - element_width - h_padding, container.bottom - element_height - v_padding, element_width, element_height)

def align_top_right(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.right - element_width - h_padding, container.top + v_padding, element_width, element_height)

def align_top_left(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.top + v_padding, element_width, element_height)

def align_center_right(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.right - element_width - h_padding, container.top + (container.height - element_height)//2 + v_padding, element_width, element_height)

def align_center_left(container, element_width, element_height, h_padding = 0, v_padding = 0):
    return pygame.Rect(container.left + h_padding, container.top + (container.height - element_height)//2 + v_padding, element_width, element_height)

def load_image(image_path):
    """
    Load an image from a file path
    
    args:
        image_path (str): The path to the image file
    """
    try:
        image = pygame.image.load(image_path).convert_alpha()
    except FileNotFoundError:
        image = pygame.surface.Surface((128, 128), pygame.HWSURFACE|pygame.SRCALPHA)
        image.fill((255, 0, 255))
    return image

def draw_linear_gradient(surface, start_colour, end_colour, rect):
    """
    Draw a linear gradient on a rectangle
    
    args:
        surface (pygame.Surface): The surface to draw the gradient on
        start_colour (str): The start colour of the gradient
        end_colour (str): The end colour of the gradient
        rect (pygame.Rect): The rectangle to draw the gradient
    """
    start_colour = hex_to_rgb(start_colour)
    end_colour = hex_to_rgb(end_colour)
    for y in range(rect.height):
        colour = [int(start_colour[i] + (y / rect.height) * (end_colour[i] - start_colour[i])) for i in range(3)]
        pygame.draw.line(surface, colour, (rect.left, rect.top + y), (rect.right, rect.top + y))

def draw_solid_colour(surface, colour, rect):
    """
    Draw a solid colour rectangle
    
    args:
        surface (pygame.Surface): The surface to draw the rectangle on
        colour (str): The colour of the rectangle
        rect (pygame.Rect): The rectangle to draw
    """
    pygame.draw.rect(surface, hex_to_rgb(colour), rect)

def draw_border(surface, border, rect, RENDER_SCALE = 1):
    """
    Draw a border around a rectangle
    
    args:
        surface (pygame.Surface): The surface to draw the border on
        border (dict): The border to draw
        rect (pygame.Rect): The rectangle to draw the border around
    """
    for side, value in border.items():
        width, colour = value
        width = int(width * RENDER_SCALE)
        
        if side == 'top':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.left, rect.top, rect.width, width))
        elif side == 'bottom':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.left, rect.bottom - width, rect.width, width))
        elif side == 'left':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.left, rect.top, width, rect.height))
        elif side == 'right':
            pygame.draw.rect(surface, hex_to_rgb(colour), pygame.Rect(rect.right - width, rect.top, width, rect.height))
            
def brightness(surface, brightness_factor):
    """
    Adjust the brightness of a surface
    
    args:
        surface (pygame.Surface): The surface to adjust the brightness of
        brightness_factor (float): The factor to adjust the brightness by (< 1 = darken, > 1 = brighten)
    """
    pygame.surfarray.blit_array(
        surface,  
        np.clip((np.multiply(
                pygame.surfarray.array3d(surface), 
                brightness_factor
                )
            ),
            0,
            255
        )
    )

def brightness_maintain_alpha(surface, brightness_factor):
    """
    Adjust the brightness of a surface preserving the alpha channel, slower!
    
    args:
        surface (pygame.Surface): The surface to adjust the brightness of
        brightness_factor (float): The factor to adjust the brightness by (< 1 = darken, > 1 = brighten)
    """
    pixel_array = pygame.surfarray.array3d(surface).astype(np.float32)
    alpha_channel = pygame.surfarray.pixels_alpha(surface).astype(np.float32)

    pixel_array = np.clip(pixel_array * brightness_factor, 0, 255).astype(np.uint8)
    pygame.surfarray.blit_array(surface, pixel_array)

    alpha_channel = np.clip(alpha_channel, 0, 255).astype(np.uint8)
    pygame.surfarray.pixels_alpha(surface)[:, :] = alpha_channel

def peek_queue(q):
    with q.mutex:
        if q.queue:
            return q.queue[0]
        else:
            return None
        
def add_to_queue(q, item):
    with q.mutex:
        q.put(item)

def remove_from_queue(q):
    with q.mutex:
        if not q.empty():
            return q.get()
        else:
            return None

def copy2clipboard(text):
    """
    Copy text to the clipboard
    
    args:
        text (str): The text to copy
    """
    if isinstance(text, dict):
        text = json.dumps(text, indent=4)
        
    if platform.system() == "Darwin":
        subprocess.run("pbcopy", universal_newlines = True, input = text)
    elif platform.system() == "Windows":
        subprocess.run("clip", universal_newlines = True, input = text)

def smoothstep_interpolate(start, end, progress):
    """Interpolate between start and end using smoothstep."""
    return smoothstep(progress) * (end - start) + start

def ease_out_elastic_interpolate(start, end, progress, amplitude = 1, frequency = 1):
    """Interpolate between start and end using easeOutElastic."""
    c4 = (2 * math.pi) / 3 

    if progress == 0:
        return start
    elif progress == 1:
        return end
    else:
        return (math.pow(2, -10 * progress) * math.sin((progress * 10 * frequency - 0.75) * c4) * amplitude + 1) * (end - start) + start

def ease_out_back_interpolate(start, end, progress, amplitude = 1):
    """Interpolate between start and end using easeOutBack."""
    c1 = 1.70158 * amplitude
    c3 = c1 + 1

    return (1 + c3 * math.pow(progress - 1, 3) + c1 * math.pow(progress - 1, 2)) * (end - start) + start