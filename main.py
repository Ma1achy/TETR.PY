import pygame
from matrix import Matrix
from tetromino import Tetromino
import random

def lerpBlendRGBA(base, overlay, alpha):
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

    blend = lambda b, o: alpha * o + (1 - alpha) * b    # noqa: E731

    return (blend(r1, r2), blend(g1, g2), blend(b1, b2))

def seven_bag(bag):
   
    piece = random.choice(bag)
    bag.remove(piece)
        
    return piece

def draw_blocks(matrix, color_map, window, field, grid_size, field_height, blend=False, blend_color=(0, 0, 0), blend_factor=0.33):
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value != 0:
                color = color_map[value]
                if blend:
                    color = lerpBlendRGBA(blend_color, color, blend_factor)
                pygame.draw.rect(window, color, (field.x + j * grid_size, field.y + i * grid_size - field_height, grid_size, grid_size))
    
def main(WIDTH, HEIGHT, MATRIX_WIDTH, MATRIX_HEIGHT, GRID_SIZE, FPS):
    bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
     
    pygame.init()
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Four")
    
    MATRIX = Matrix(MATRIX_WIDTH, MATRIX_HEIGHT)
    PIECE = Tetromino(seven_bag(bag), 0, 4, 18)
    MATRIX.insert_piece_blocks(PIECE)
   
    COLOUR_MAP = {
        0: (0, 0, 0),
        1: (168, 34, 139), # T
        2: (99, 177, 0), # S
        3: (206, 0, 43), # Z
        4: (219, 87, 0), # L
        5: (38, 64, 202), # J
        6: (221, 158, 0), # O
        7: (51, 156, 218), # I
        8: (105, 105, 105) # garbage
    }

    running = True
    
    while running:   
        
        PIECE.ghost(MATRIX)
        
        if len(bag) == 0:
            bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
          
        FIELD_WIDTH = MATRIX_WIDTH * GRID_SIZE
        FIELD_HEIGHT = MATRIX_HEIGHT // 2 * GRID_SIZE

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if event.key == pygame.K_x:
                    
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece(PIECE)
                    PIECE.rotate('CW', MATRIX)
                    MATRIX.insert_piece_blocks(PIECE)
                    
                if event.key == pygame.K_z:
                    
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece(PIECE)
                    PIECE.rotate('CCW', MATRIX)
                    MATRIX.insert_piece_blocks(PIECE)
                    
                if event.key == pygame.K_c:
                    
                    PIECE.ghost(MATRIX)
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece(PIECE) 
                    PIECE.rotate('180', MATRIX)
                    MATRIX.insert_piece_blocks(PIECE)
                    
                if event.key == pygame.K_LEFT:
                    
                    PIECE.ghost(MATRIX)   
                    MATRIX.clear_piece(PIECE)
                    PIECE.move('LEFT', MATRIX)
                    MATRIX.insert_piece_blocks(PIECE)
                
                if  event.key == pygame.K_RIGHT:
                    
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece(PIECE)
                    PIECE.move('RIGHT', MATRIX)
                    MATRIX.insert_piece_blocks(PIECE)
                
                if event.key == pygame.K_UP:
                    
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece(PIECE)
                    PIECE.move('UP', MATRIX)
                    MATRIX.insert_piece_blocks(PIECE)
                         
                if event.key == pygame.K_DOWN:
                    
                    PIECE.ghost(MATRIX)  
                    MATRIX.clear_piece(PIECE)
                    PIECE.move('DOWN', MATRIX)
                    MATRIX.insert_piece_blocks(PIECE)
                
                if event.key == pygame.K_SPACE:
                    
                    PIECE.position = PIECE.ghost_position
                    MATRIX.clear_piece(PIECE)
                    PIECE.place(MATRIX)
                    PIECE = Tetromino(seven_bag(bag), 0, 4, 18)
                    MATRIX.insert_piece_blocks(PIECE)
                
        WINDOW.fill((0, 0, 0))
        
        field = pygame.Rect((WIDTH - FIELD_WIDTH)//2, (HEIGHT - FIELD_HEIGHT)//2, FIELD_WIDTH, FIELD_HEIGHT)
        
        BORDER_WIDTH = 10
        pygame.draw.line(WINDOW, (255, 255, 255), (field.x - BORDER_WIDTH//2 - 1, field.y), (field.x - BORDER_WIDTH//2 - 1, field.y + field.height), BORDER_WIDTH )
        pygame.draw.line(WINDOW, (255, 255, 255), (field.x + field.width + BORDER_WIDTH//2 - 1 , field.y), (field.x + field.width + BORDER_WIDTH//2 - 1, field.y + field.height), BORDER_WIDTH )
        pygame.draw.line(WINDOW, (255, 255, 255), (field.x - BORDER_WIDTH, field.y + field.height + BORDER_WIDTH//2 - 1), (field.x + field.width + BORDER_WIDTH - 1, field.y + field.height + BORDER_WIDTH//2 - 1), BORDER_WIDTH )

        draw_blocks(MATRIX.matrix, COLOUR_MAP, WINDOW, field, GRID_SIZE, FIELD_HEIGHT)
        draw_blocks(MATRIX.ghost_blocks, COLOUR_MAP, WINDOW, field, GRID_SIZE, FIELD_HEIGHT, blend=True)
        draw_blocks(MATRIX.piece, COLOUR_MAP, WINDOW, field, GRID_SIZE, FIELD_HEIGHT)
                                
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)
            
    pygame.quit()

if __name__ == "__main__":
   
    WIDTH, HEIGHT = 1000, 1200
    MATRIX_WIDTH, MATRIX_HEIGHT = 10, 40
    GRID_SIZE = 40
    FPS = 60
      
    main(WIDTH, HEIGHT, MATRIX_WIDTH, MATRIX_HEIGHT, GRID_SIZE, FPS)