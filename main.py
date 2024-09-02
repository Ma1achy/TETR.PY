import pygame
from matrix import Matrix
from tetromino import Tetromino
import random
import config
import pygame_config

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

def main():

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
                    
                    #four.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.rotate('CW', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                    
                if event.key == pygame.K_z:
                    
                    #four.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.rotate('CCW', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                    
                if event.key == pygame.K_c:
                    
                    #four.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece() 
                    PIECE.rotate('180', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                    
                if event.key == pygame.K_LEFT:
                    
                    #four.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)   
                    MATRIX.clear_piece()
                    PIECE.move('LEFT', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                
                if  event.key == pygame.K_RIGHT:
                    
                    #four.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.move('RIGHT', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                
                if event.key == pygame.K_UP:
                    
                   # four.T_SPIN_FLAG = None
                    PIECE.ghost(MATRIX)
                    MATRIX.clear_piece()
                    PIECE.move('UP', MATRIX)
                    MATRIX.insert_blocks(PIECE.blocks, PIECE.position, MATRIX.piece)
                         
                if event.key == pygame.K_DOWN:
                    
                  #  four.T_SPIN_FLAG = None
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
        
    pygame.quit()

if __name__ == "__main__":
    pass