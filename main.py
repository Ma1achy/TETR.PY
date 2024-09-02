from pygame_instance import PyGameInstance
from four import Four
from tetromino import Tetromino

#TODO:

# Having to refactor to handle inputs better to allow for DAS and ARR + multiple inputs at once
# plus to implement other features, such as hold, piece spawning, game over conditions, gravity, lock delay, perfect clear detection, combo detection, scoring, levels etc.
# Four class will handle the game loop/logic, Render class will handle rendering the game to the screen, PyGameInstance will handle the pygame instance and pygame events.

# movement/inputs needs to be done via Actions
# pygame key events will trigger actions (can be multiple at once)
# actions will be performed in the game loop actions will be performed in the order they are received in the list for the frame
# actions will be buffered if they cannot be performed immediately (e.g. rotating or holding a piece when it is not spawned yet)
# this will also allow for bots to be implemented easily as they can just send Actions to the game loop

# NEED TO FIRST GET BASIC INPUT HANDLING WORKING AGAIN IN A BASIC GAME LOOP

# DAS and ARR can be implemented by checking if the action for (moving left/right or soft dropping (seperate das & arr)) was performed last frame,
# and that it is being performed this frame, if so, increment a counter, if the counter reaches a certain value, perform the action again automatically (DAS)
# and perform it by a certain amount every frame (ARR)

# - DAS AND ARR (FOR LEFT AND RIGHT MOVEMENT AND DOWN MOVEMENT)
# - HOLD PIECE	
# - PIECE SPAWNING (SPAWN ABOVE THE FIELD IN A BOX, SEE WIKI) 
# - GAME OVER CONDITIONS
# - GRAVITY
# - LOCK DELAY
# - PERFECT CLEAR DETECTION
# - COMBO DETECTION
# - SCORING
# - LEVELS

def main():
    
    pygame_instance = PyGameInstance()
    four = Four(pygame_instance)  
    pygame_instance.run(four)

if __name__ == "__main__":
    main()