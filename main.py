import pygame
from matrix import Matrix
from tetromino import Tetromino
from render import render_matrix
import random
import flags

#TODO:
# - DAS AND ARR (FOR LEFT AND RIGHT MOVEMENT AND DOWN MOVEMENT)
# - HOLD PIECE	
# - SEEDED 7 BAG & NEXT QUEUE
# - PIECE SPAWNING (SPAWN ABOVE THE FIELD IN A BOX, SEE WIKI) 
# - GAME OVER CONDITIONS
# - GRAVITY
# - LOCK DELAY
# - PERFECT CLEAR DETECTION
# - COMBO DETECTION
# - SCORING
# - LEVELS

def seven_bag(bag:list):

    piece = random.choice(bag)
    bag.remove(piece)
        
    return piece

def main(WIDTH, HEIGHT, MATRIX_WIDTH, MATRIX_HEIGHT, GRID_SIZE, FPS, SEED):
    bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
     
    pygame.init()
    pygame.mixer.init()
    
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Four")
   
    MATRIX = Matrix(MATRIX_WIDTH, MATRIX_HEIGHT)
    PIECE = Tetromino(seven_bag(bag), 0, 4, 18)
    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
   
    running = True
    
    while running:   
    
        MATRIX.clear_lines()
        PIECE.ghost(MATRIX)
        
        if len(bag) == 0:
            bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
          
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if event.key == pygame.K_x:
                    
                    flags.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.rotate('CW', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                    
                if event.key == pygame.K_z:
                    
                    flags.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.rotate('CCW', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                    
                if event.key == pygame.K_c:
                    
                    flags.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece() 
                    PIECE.rotate('180', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                    
                if event.key == pygame.K_LEFT:
                    
                    flags.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)   
                    MATRIX.clear_piece()
                    PIECE.move('LEFT', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                
                if  event.key == pygame.K_RIGHT:
                    
                    flags.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.move('RIGHT', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                
                if event.key == pygame.K_UP:
                    
                    flags.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.move('UP', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                         
                if event.key == pygame.K_DOWN:
                    
                    flags.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)  
                    MATRIX.clear_piece()
                    PIECE.move('DOWN', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                
                if event.key == pygame.K_SPACE:
                    
                    PIECE.position = PIECE.ghost_position
                    MATRIX.clear_piece()
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.matrix)
                    PIECE = Tetromino(seven_bag(bag), 0, 4, 18)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
        
        render_matrix(WINDOW, WIDTH, HEIGHT, MATRIX, GRID_SIZE)
        # print(MATRIX, end="\r", flush=True) 
        
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)
        print(flags.T_SPIN_FLAG)
        
    pygame.quit()

if __name__ == "__main__":
   
    WIDTH, HEIGHT = 1000, 1200
    MATRIX_WIDTH, MATRIX_HEIGHT = 10, 40
    GRID_SIZE = 40
    FPS = 60
    SEED = 0
      
    main(WIDTH, HEIGHT, MATRIX_WIDTH, MATRIX_HEIGHT, GRID_SIZE, FPS, SEED)