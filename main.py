from pygame_instance import PyGameInstance
from four import Four
from render import Render

#TODO:

# Having to refactor to handle inputs better to allow for DAS and ARR + multiple inputs at once
# plus to implement other features, such as hold, piece spawning, game over conditions, gravity, lock delay, perfect clear detection, combo detection, scoring, levels etc.
# Four class will handle the game loop/logic, Render class will handle rendering the game to the screen, PyGameInstance will handle the pygame instance and pygame events.

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
    four = Four()
    four.loop()
    render = Render(pygame_instance.window)
    
    while True:
        render.render_frame(four)

if __name__ == "__main__":
    main()