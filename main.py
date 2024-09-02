from pygame_instance import PyGameInstance
from four import Four


#TODO:

# MAKE GAME LOOP AND RENDERING USE DELTA TIME INSTEAD OF FIXED TIME STEP

# DAS and ARR can be implemented by checking if the action for (moving left/right or soft dropping (seperate das & arr)) was performed last frame,
# and that it is being performed this frame, if so, increment a counter, if the counter reaches a certain value, perform the action again automatically (DAS)
# and perform it by a certain amount every frame (ARR)

# - DAS AND ARR (FOR LEFT AND RIGHT MOVEMENT AND DOWN MOVEMENT)
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