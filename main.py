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

# === rendering ===
#         - make blocks use textures
#         - animations

# change queue generation, need to generate a bag and insert into queue, make sure queue always has 2 bags in it, 3 max.
# rather than now where it shuffles the bag and removes the first tetromino from the bag and inserts it into the queue and ensures a fixed queue length

async def main():
    game_instance = Core()
    four = Four(game_instance, rotation_system = 'SRS')
    await game_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())
