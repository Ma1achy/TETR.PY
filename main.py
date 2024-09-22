import asyncio
from core.core import Core
from instance.four import Four

#TODO:

# FIX: lock delay reset mechanics (currently is half right): 
# - Lock delay is reset every time a piece is moved or rotated (successfully) (the maximum amount of resets is 15 and every reset subtracts 1 from the total resets)
# - If 15 resets are reached, the piece locks instantly on contact with the floor
# - The move resets are replenished if the piece falls below its lowest position (given by the y coord of the center of rotation of the piece)
# - Each ARR move counts as a reset (this is a bit weird when using 0 ARR but makes sense)

# - Implement Prevent Accidental Hard Drops: When a piece locks on its own, the harddrop action is disabled for a few frames

#  === game logic ===
# - PERFECT CLEAR DETECTION
# - COMBO DETECTION
# - SCORING
# - LEVELS
# - GAME OVER CONDITIONS

# redo render code it is a 3 course itallian meal rn
# - Implement Prefer Soft Drop Over Movement: At very high speeds, the soft drop action will be prioritized over movement (not sure if this is necessary because my control loop can do multiple actions per frame)

async def main():
    game_instance = Core()
    four = Four(game_instance, rotation_system = 'SRS')
    await game_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())
