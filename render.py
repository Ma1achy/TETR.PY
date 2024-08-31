from matrix import Matrix
import pygame

COLOUR_MAP = {
        0: (0, 0, 0),
        1: (168, 34, 139), # T
        2: (99, 177, 0), # S
        3: (206, 0, 43), # Z
        4: (219, 87, 0), # L
        5: (38, 64, 202), # J
        6: (221, 158, 0), # O
        7: (51, 156, 218), # I
        8: (105, 105, 105), # garbage
        50: (255, 0, 0), # ghost
        51: (0, 255, 0), # ghost
        52: (0, 0, 255), # ghost
        53: (255, 255, 255), # ghost 
    }

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

def draw_grid(window:pygame, field:pygame, grid_size:int, field_height:int, matrix:Matrix):
    grid_colour = lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.25)
    
    for idx in range(matrix.HEIGHT//2, matrix.HEIGHT + 1):
        pygame.draw.line(window, grid_colour, (field.x, field.y + idx * grid_size - field_height), (field.x + matrix.WIDTH * grid_size, field.y + idx * grid_size - field_height))
    for idx in range(matrix.WIDTH + 1):
        pygame.draw.line(window, grid_colour, (field.x + idx * grid_size, field.y + field_height), (field.x + idx * grid_size, field.y + matrix.HEIGHT//2 * grid_size - field_height))
        
def draw_blocks(matrix:Matrix, colour_map:dict, window:pygame, field:pygame, grid_size:int, field_height:int, blend:bool, alpha:float):
    """
    Draw the blocks in the matrix
    
    args:
    matrix (Matrix): The matrix object that contains the blocks
    colour_map (dict): A dictionary that maps the block values to RGB colours
    window (pygame): The window to draw the blocks on
    field (pygame): The field to draw the blocks on
    grid_size (int): The size of the grid
    field_height (int): The height of the field
    blend (bool): Whether to blend the blocks
    alpha (float): The alpha value to blend the blocks
    """
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value != 0:
                colour = colour_map[value]
                if blend:
                    colour = lerpBlendRGBA((0, 0, 0), colour, alpha)
                pygame.draw.rect(window, colour, (field.x + j * grid_size, field.y + i * grid_size - field_height, grid_size, grid_size))
                
def render_matrix(WINDOW, WIDTH, HEIGHT, MATRIX, GRID_SIZE):
    
    FIELD_WIDTH = MATRIX.WIDTH * GRID_SIZE
    FIELD_HEIGHT = MATRIX.HEIGHT // 2 * GRID_SIZE
    BORDER_WIDTH = 10
        
    WINDOW.fill((0, 0, 0))
    
    field = pygame.Rect((WIDTH - FIELD_WIDTH)//2, (HEIGHT - FIELD_HEIGHT)//2, FIELD_WIDTH, FIELD_HEIGHT)
    
    draw_blocks(MATRIX.ghost_blocks, COLOUR_MAP, WINDOW, field, GRID_SIZE, FIELD_HEIGHT, blend = True, alpha = 0.33)
    draw_grid(WINDOW, field, GRID_SIZE, FIELD_HEIGHT, MATRIX)
    draw_blocks(MATRIX.matrix, COLOUR_MAP, WINDOW, field, GRID_SIZE, FIELD_HEIGHT, blend = False, alpha = 1)
    draw_blocks(MATRIX.piece, COLOUR_MAP, WINDOW, field, GRID_SIZE, FIELD_HEIGHT, blend = False, alpha = 1)
    
    pygame.draw.line(WINDOW, (255, 255, 255), (field.x - BORDER_WIDTH//2 - 1, field.y), (field.x - BORDER_WIDTH//2 - 1, field.y + field.height), BORDER_WIDTH )
    pygame.draw.line(WINDOW, (255, 255, 255), (field.x + field.width + BORDER_WIDTH//2 - 1 , field.y), (field.x + field.width + BORDER_WIDTH//2 - 1, field.y + field.height), BORDER_WIDTH )
    pygame.draw.line(WINDOW, (255, 255, 255), (field.x - BORDER_WIDTH, field.y + field.height + BORDER_WIDTH//2 - 1), (field.x + field.width + BORDER_WIDTH - 1, field.y + field.height + BORDER_WIDTH//2 - 1), BORDER_WIDTH )