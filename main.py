import asyncio
from core.core import Core
from instance.four import Four

#TODO:

# - Implement Prevent Accidental Hard Drops: When a piece locks on its own, the harddrop action is disabled for a few frames (use flag system)
# - check if when prefSD is true if the order of preform actions and gravity needs to be swapped in game loop.

#  === game logic ===
# - PERFECT CLEAR DETECTION 
# - COMBO DETECTION
# - SCORINGz
# - LEVELS
# - GAME OVER CONDITIONS

# redo render code it is a 3 course itallian meal rn

async def main():
    game_instance = Core()
    four = Four(game_instance, rotation_system = 'SRS')
    await game_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())
