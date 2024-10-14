import asyncio
from core.core import Core
from instance.four import Four

#TODO:

# - check if when prefSD is true if the order of preform actions and gravity needs to be swapped in game loop. 90% sure i dont have to worry about this but lmao icba to check

#  === game logic ===
# - PERFECT CLEAR DETECTION 
# - COMBO DETECTION
# - SCORING
# - LEVELS
# - GAME OVER CONDITIONS

# redo render code it is a 3 course itallian meal rn
#           - make coordinates less stupid lol
#           - render directly to window surface instead of "four_surface"
#           - change how the current tetromino is rendered, to similar to how the queue is rendered currently is very jank
#           - refactor the code to be more maintainable and readable

# move debug stuff into sep obj & file

# change queue generation, need to generate a bag and insert into queue, make sure queue always has 2 bags in it, 3 max.
# rather than now where it shuffles the bag and removes the first tetromino from the bag and inserts it into the queue and ensures a fixed queue length

async def main():
    game_instance = Core()
    four = Four(game_instance, rotation_system = 'SRS')
    await game_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())
